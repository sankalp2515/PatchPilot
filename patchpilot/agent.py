import asyncio
import difflib
import re
import time

from .observability import Telemetry, event_record
from .proof import build_proof, proof_passes
from .providers import REPLAY_SCOPE_MESSAGE, recorded_contract_matches, validate_proposal
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
    def __init__(self, store, tools, telemetry=None):
        self.store = store
        self.tools = tools
        self.telemetry = telemetry or Telemetry()
        self.tools.telemetry = self.telemetry

    async def run(self, run_id):
        run = self.store.get(run_id)
        with self.telemetry.span(
            "agent.run",
            "WORKFLOW",
            mode=run["input"]["mode"],
            recovery=bool(run["attempts"] or run["sources"]),
        ) as span:
            self.store.update(
                run_id, {"telemetry": {"status": self.telemetry.status, "trace_id": span.trace_id}}
            )
            await self._run(run_id)
            final = self.store.get(run_id)
            span.set(
                status=final["status"],
                passed=sum(r["passed"] for r in final["verification"]),
                total=len(final["verification"]),
            )
        final = self.store.get(run_id)
        self.store.update(
            run_id,
            {"telemetry": {"status": self.telemetry.status, "trace_id": span.trace_id}},
            force=final["status"] == "cancelled",
        )

    async def _checks(self, code, entrypoint, cases, name="verification.acceptance"):
        with self.telemetry.span(name, "TOOL", total=len(cases)) as span:
            results = await asyncio.to_thread(verify, code, entrypoint, cases)
            span.set(
                passed=sum(r["passed"] for r in results),
                outcome="passed" if all(r["passed"] for r in results) else "failed",
            )
            return results

    async def _proof(self, request, sources, code, results, baseline, citations):
        with self.telemetry.span("verification.audit", "TOOL") as span:
            proof = await asyncio.to_thread(build_proof, request, sources, code, results, baseline, citations)
            span.set(
                audit_passed=proof["audit"]["passed"],
                audit_total=proof["audit"]["total"],
                outcome="passed" if proof_passes(proof) else "failed",
            )
            return proof

    async def _run(self, run_id):
        started = time.monotonic()
        previous_elapsed = self.store.get(run_id)["metrics"]["elapsed_seconds"]

        def emit(kind, title, detail=""):
            self.store.update(run_id, event=event_record(kind, title, detail, self.telemetry.secrets))

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
                baseline = await self._checks(
                    request["source_code"], request["entrypoint"], request["cases"], "verification.baseline"
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
                if request["mode"] == "replay" and not recorded_contract_matches(request):
                    checkpoint(
                        "needs_human", diagnosis=REPLAY_SCOPE_MESSAGE, limitations=[REPLAY_SCOPE_MESSAGE]
                    )
                    emit("decision", "Recorded replay scope mismatch", REPLAY_SCOPE_MESSAGE)
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

                    with self.telemetry.span("tools.research", "TOOL") as span:
                        sources = await self.tools.research(request, research_event)
                        span.set(source_count=len(sources), outcome="found" if sources else "insufficient")
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
                    checks = await self._checks(restored["code"], request["entrypoint"], request["cases"])
                    proof = await self._proof(
                        request, sources, restored["code"], checks, baseline, restored["citations"]
                    )
                    checkpoint("verifying", verification=checks, proof=proof)
                    if proof_passes(proof):
                        checkpoint(
                            "verified",
                            verification=checks,
                            proof=proof,
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
                        "audit": a.get("audit", {}),
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
                        with self.telemetry.span(
                            "tools.propose", "TOOL", attempt=number, recovery=bool(feedback)
                        ) as span:
                            if request["mode"] == "live":
                                with self.telemetry.span(
                                    "model.propose",
                                    "LLM",
                                    provider=getattr(self.tools.settings, "provider", ""),
                                    model=getattr(self.tools.settings, "model", ""),
                                ) as llm_span:
                                    proposal = await self.tools.propose(request, sources, feedback, emit)
                                    llm_span.set(outcome="generated", **proposal.get("usage", {}))
                            else:
                                proposal = await self.tools.propose(request, sources, feedback, emit)
                            span.set(outcome="generated")
                        data = self.store.get(run_id)
                        metrics = data["metrics"]
                        metrics["tokens"] += proposal.get("usage", {}).get("tokens", 0)
                        self.store.update(run_id, {"metrics": metrics})
                        validate_proposal(proposal, sources, request["entrypoint"], request)
                        attempt["code"] = proposal["code"]
                        checkpoint("verifying")
                        results = await self._checks(
                            proposal["code"], request["entrypoint"], request["cases"]
                        )
                        proof = await self._proof(
                            request, sources, proposal["code"], results, baseline, proposal["citations"]
                        )
                        attempt["audit"] = proof["audit"]
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
                            proof=proof,
                        )
                        emit(
                            "verification",
                            "Protected cases executed",
                            f"{sum(r['passed'] for r in results)}/{len(results)} cases pass on attempt {number}.",
                        )
                        emit(
                            "verification",
                            "Independent counterexample audit",
                            f"{proof['audit']['passed']}/{proof['audit']['total']} local policy checks pass; applicable: {proof['audit']['applicable']}.",
                        )
                        if proof_passes(proof):
                            checkpoint(
                                "verified",
                                limitations=[
                                    proof["verified_scope"],
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
                            {
                                "attempt": number,
                                "previous_code": proposal["code"],
                                "results": results,
                                "audit": proof["audit"],
                            }
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
