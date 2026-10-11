import asyncio
import difflib
import re
import time

from .observability import event_record
from .providers import validate_proposal
from .sandbox import verify

PLAN = [
    {"area": "Planning", "task": "Reproduce the failure and define a bounded repair plan"},
    {"area": "Tool use", "task": "Search vendor evidence and inspect actual tool responses"},
    {"area": "State", "task": "Checkpoint sources, attempts, decisions and protected inputs"},
    {"area": "Context", "task": "Select fetched evidence applicable to the target version"},
    {"area": "Execution", "task": "Generate a minimal adapter repair and execute acceptance cases"},
    {"area": "Recovery", "task": "Use failed actions and test feedback within a retry budget"},
    {"area": "Verification", "task": "Require literal source citations and passing independent cases"},
    {"area": "Iteration", "task": "Revise the patch when observed behavior contradicts the proposal"},
]


class Agent:
    def __init__(self, store, tools):
        self.store = store
        self.tools = tools

    async def run(self, run_id):
        started = time.monotonic()
        previous_elapsed = self.store.get(run_id)["metrics"]["elapsed_seconds"]

        def emit(kind, title, detail=""):
            self.store.update(run_id, event=event_record(kind, title, detail))

        def checkpoint(status, **changes):
            current = self.store.get(run_id)
            if current["cancel_requested"] or current["status"] == "cancelled":
                raise asyncio.CancelledError
            metrics = changes.pop("metrics", current["metrics"])
            metrics["elapsed_seconds"] = round(previous_elapsed + time.monotonic() - started, 2)
            self.store.update(run_id, {"status": status, "phase": status, "metrics": metrics, **changes})

        try:
            async with asyncio.timeout(240):
                run = self.store.get(run_id)
                if run["cancel_requested"]:
                    return
                request = run["input"]
                checkpoint("planning", plan=PLAN)
                emit(
                    "plan",
                    "Investigation plan saved",
                    "Protected acceptance cases, authoritative research, bounded repairs and explicit verification.",
                )
                checkpoint("baseline")
                baseline = await asyncio.to_thread(
                    verify, request["source_code"], request["entrypoint"], request["cases"]
                )
                checkpoint("baseline", baseline=baseline)
                emit(
                    "verification",
                    "Baseline reproduced",
                    f"{sum(c['passed'] for c in baseline)}/{len(baseline)} protected cases pass before repair.",
                )
                if all(case["passed"] for case in baseline):
                    checkpoint(
                        "no_change",
                        diagnosis="The supplied adapter already satisfies every supplied case. No repair or provider call was needed.",
                        verification=baseline,
                        limitations=["This result covers only the supplied acceptance cases."],
                    )
                    return
                if re.search(
                    r"\b(?:HTTP\s*)?(401|403|429)\b|unauthorized|invalid.*credentials|rate.limit",
                    request["symptom"],
                    re.I,
                ):
                    checkpoint(
                        "needs_human",
                        diagnosis="This incident indicates authentication, authorization or quota failure. A schema repair is not justified.",
                        limitations=[
                            "Inspect credentials, permissions and quota using the vendor's account tools. No credential changes were attempted."
                        ],
                    )
                    emit(
                        "decision",
                        "Repair declined",
                        "Authentication and rate-limit failures are distinct from contract drift.",
                    )
                    return
                sources = run["sources"]
                if not sources:
                    checkpoint("researching")

                    def research_event(kind, title, detail=""):
                        if kind == "search" and request["mode"] == "live":
                            data = self.store.get(run_id)
                            metrics = data["metrics"]
                            metrics["search_calls"] += 1
                            self.store.update(run_id, {"metrics": metrics})
                        emit(kind, title, detail)

                    sources = await self.tools.research(request, research_event)
                    checkpoint("context", sources=sources)
                else:
                    emit(
                        "recovery",
                        "Saved research restored",
                        "Reusing persisted source evidence; completed research is not repeated.",
                    )
                if not sources:
                    checkpoint(
                        "needs_human",
                        diagnosis="No fetched official source established applicability to the target version. A search snippet alone cannot justify repair.",
                        limitations=[
                            "No patch was generated. Refine the version or search hint, then start a new investigation."
                        ],
                    )
                    emit("decision", "Evidence insufficient", "Stopped before code generation.")
                    return
                emit(
                    "context",
                    "Evidence selected",
                    f"{len(sources)} official source(s), with version applicability and content hashes.",
                )
                attempts = self.store.get(run_id)["attempts"]
                saved = self.store.get(run_id)
                if (
                    saved["proposed_code"]
                    and saved["verification"]
                    and all(case["passed"] for case in saved["verification"])
                ):
                    restored = {
                        "code": saved["proposed_code"],
                        "diagnosis": saved["diagnosis"],
                        "citations": saved["citations"],
                    }
                    validate_proposal(restored, sources, request["entrypoint"], request)
                    checks = await asyncio.to_thread(
                        verify, restored["code"], request["entrypoint"], request["cases"]
                    )
                    if all(case["passed"] for case in checks):
                        checkpoint(
                            "verified",
                            verification=checks,
                            limitations=[
                                "A saved proposal was revalidated against literal evidence citations and the unchanged acceptance cases after restart.",
                                "Verified only within the restricted adapter interpreter and supplied cases. No repository or production system was modified.",
                            ],
                        )
                        emit(
                            "recovery",
                            "Saved passing repair restored",
                            "Rechecked the saved patch and citations without generating a new model proposal.",
                        )
                        return
                feedback = [
                    {
                        "attempt": a["number"],
                        "error": a.get("error", ""),
                        "results": a.get("results", []),
                        "previous_code": a.get("code", ""),
                    }
                    for a in attempts
                ]
                for index in range(len(attempts), request.get("max_attempts", 3)):
                    checkpoint("repairing")
                    number = index + 1
                    emit(
                        "execution",
                        f"Repair attempt {number}",
                        "Generate a minimal adapter change; acceptance cases remain protected.",
                    )
                    attempt = {"number": number, "code": "", "results": [], "error": ""}
                    try:
                        if request["mode"] == "live":
                            data = self.store.get(run_id)
                            metrics = data["metrics"]
                            metrics["model_calls"] += 1
                            self.store.update(run_id, {"metrics": metrics})
                        proposal = await self.tools.propose(request, sources, feedback, emit)
                        data = self.store.get(run_id)
                        metrics = data["metrics"]
                        metrics["tokens"] += proposal.get("usage", {}).get("tokens", 0)
                        self.store.update(run_id, {"metrics": metrics})
                        validate_proposal(proposal, sources, request["entrypoint"], request)
                        attempt["code"] = proposal["code"]
                        checkpoint("verifying")
                        results = await asyncio.to_thread(
                            verify, proposal["code"], request["entrypoint"], request["cases"]
                        )
                        attempt["results"] = results
                        attempts.append(attempt)
                        diff = "".join(
                            difflib.unified_diff(
                                request["source_code"].splitlines(True),
                                proposal["code"].splitlines(True),
                                fromfile="adapter.before.py",
                                tofile="adapter.proposed.py",
                            )
                        )
                        checkpoint(
                            "verifying",
                            attempts=attempts,
                            proposed_code=proposal["code"],
                            diff=diff,
                            diagnosis=proposal["diagnosis"],
                            citations=proposal["citations"],
                            verification=results,
                        )
                        emit(
                            "verification",
                            "Protected cases executed",
                            f"{sum(r['passed'] for r in results)}/{len(results)} cases pass on attempt {number}.",
                        )
                        if all(result["passed"] for result in results):
                            checkpoint(
                                "verified",
                                limitations=[
                                    "Verified only against the supplied acceptance cases and the restricted adapter interpreter.",
                                    "This is a proposed patch; no repository, production endpoint or payment system was modified.",
                                    "Recorded evidence and deterministic repair policy were used in replay mode."
                                    if request["mode"] == "replay"
                                    else "Live SerpApi discovery and model generation were used; historical response fixtures are local test data.",
                                ],
                            )
                            emit(
                                "decision",
                                "Repair verified within tested scope",
                                "Review the evidence, diff and edge-case coverage before applying this proposal to a real repository.",
                            )
                            return
                        feedback.append(
                            {"attempt": number, "previous_code": proposal["code"], "results": results}
                        )
                    except ValueError as exc:
                        attempt["error"] = str(exc)
                        attempts.append(attempt)
                        feedback.append({"attempt": number, "error": str(exc)})
                        checkpoint("repairing", attempts=attempts)
                    emit(
                        "recovery",
                        "Repair requires another iteration",
                        "The next attempt receives the actual failed checks or citation/AST rejection, not a repeated confidence claim.",
                    )
                checkpoint(
                    "unverified",
                    limitations=[
                        "Repair attempts exhausted. The current proposal is not verified and must not be treated as fixed."
                    ],
                )
                emit("decision", "Stopped at the repair budget", "No successful verdict was issued.")
        except asyncio.CancelledError:
            self.store.update(
                run_id,
                {"status": "cancelled", "phase": "cancelled", "cancel_requested": True},
                {
                    "kind": "decision",
                    "title": "Investigation cancelled",
                    "detail": "Completed evidence and attempts remain available.",
                },
            )
        except TimeoutError:
            self.store.update(
                run_id,
                {
                    "status": "failed",
                    "phase": "failed",
                    "diagnosis": "Investigation reached its 240-second time budget. Saved artifacts remain inspectable.",
                },
                {
                    "kind": "recovery",
                    "title": "Time budget reached",
                    "detail": "No verified result was issued.",
                },
            )
        except Exception as exc:
            detail = (
                str(exc)[:500]
                if isinstance(exc, ValueError)
                else "An internal tool failed. Inspect the local server log; no verified result was issued."
            )
            self.store.update(
                run_id,
                {"status": "failed", "phase": "failed", "diagnosis": detail},
                {"kind": "recovery", "title": "Investigation stopped", "detail": detail},
            )
        finally:
            data = self.store.get(run_id)
            metrics = data["metrics"]
            metrics["elapsed_seconds"] = round(previous_elapsed + time.monotonic() - started, 2)
            self.store.update(run_id, {"metrics": metrics}, force=data["status"] == "cancelled")
