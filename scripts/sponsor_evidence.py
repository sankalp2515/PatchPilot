"""Compare a preserved pre-upgrade adapter with the improved agent; verify exact trace readback.

Uses synthetic replay fixtures, not private user data. No credentials are printed.
"""

import ast
import asyncio
import json
import subprocess
import time

import httpx

from patchpilot.agent import Agent
from patchpilot.config import ROOT, Settings
from patchpilot.examples import examples
from patchpilot.observability import Telemetry
from patchpilot.proof import build_proof
from patchpilot.providers import Tools
from patchpilot.sandbox import verify
from patchpilot.store import Store

EVIDENCE = ROOT / "docs" / "evidence"


def readback(trace_id, key):
    if not trace_id:
        raise RuntimeError("No real SDK trace ID was captured")
    deadline = time.monotonic() + 150
    with httpx.Client(timeout=5, follow_redirects=False) as client:
        while time.monotonic() < deadline:
            response = client.get(
                f"https://ingest.neatlogs.com/api/traces/v3/{trace_id}", headers={"x-api-key": key}
            )
            if response.status_code in (401, 403):
                raise RuntimeError("Trace readback authentication failed")
            if response.status_code == 200:
                data = response.json()
                spans = data.get("spans", [])
                ids = {span.get("span_id") for span in spans}
                roots = [span for span in spans if not span.get("parent_span_id")]
                if (
                    data.get("_id") == trace_id
                    and data.get("status") == "success"
                    and len(roots) == 1
                    and len(spans) == data.get("spanCount")
                    and all(not span.get("parent_span_id") or span["parent_span_id"] in ids for span in spans)
                ):
                    (ROOT / ".data" / f"trace-{trace_id}.json").write_text(json.dumps(data), encoding="utf-8")
                    return data
            time.sleep(1)
    raise RuntimeError("Exact trace readback timed out")


async def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    settings = Settings()
    if not settings.neatlogs_api_key:
        raise RuntimeError("Configure NEATLOGS_API_KEY privately in .env")
    telemetry = Telemetry(
        settings.neatlogs_api_key,
        secrets=(settings.serpapi_api_key, settings.groq_api_key, settings.nvidia_api_key),
    )
    telemetry.start()
    request = examples()[0] | {"mode": "replay", "replay_scenario": "recovery"}
    tools = Tools(settings)
    old = subprocess.check_output(["git", "show", "2c972e4:patchpilot/examples.py"], cwd=ROOT, text=True)
    tree = ast.parse(old)
    weak = next(
        ast.literal_eval(n.value)
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "REPAIR_CODE" for t in n.targets)
    )
    sources = await tools.research(request, lambda *args: None)
    with telemetry.span("agent.before.counterexample_audit", "WORKFLOW", mode="replay") as root:
        with telemetry.span("verification.acceptance", "TOOL") as span:
            acceptance = verify(weak, request["entrypoint"], request["cases"])
            span.set(passed=sum(x["passed"] for x in acceptance), total=len(acceptance))
        with telemetry.span("verification.audit", "TOOL") as span:
            before = build_proof(request, sources, weak, acceptance)
            span.set(
                audit_passed=before["audit"]["passed"], audit_total=before["audit"]["total"], outcome="failed"
            )
        before_trace = root.trace_id
        root.set(
            status="evaluated",
            passed=before["acceptance_passed"],
            total=before["total"],
            audit_passed=before["audit"]["passed"],
            audit_total=before["audit"]["total"],
        )
    store = Store(settings.database_path)
    run = store.create(request | {"title": "Improvement evidence · Stripe counterexample recovery"})
    await Agent(store, tools, telemetry).run(run["id"])
    after = store.get(run["id"])
    telemetry.close()
    receipt = {
        "experiment": "Synthetic same-contract evaluation of preserved pre-upgrade adapter vs enhanced replay agent; not a benchmark of real-world accuracy or model performance.",
        "baseline_commit": "2c972e4d16d2d17036d0fc684372796357dd2f5d",
        "before": {
            "trace_id": before_trace,
            "acceptance_passed": before["acceptance_passed"],
            "acceptance_total": before["total"],
            "audit_passed": before["audit"]["passed"],
            "audit_total": before["audit"]["total"],
        },
        "after": {
            "run_id": run["id"],
            "trace_id": after["telemetry"]["trace_id"],
            "status": after["status"],
            "acceptance_passed": after["proof"]["acceptance_passed"],
            "acceptance_total": after["proof"]["total"],
            "audit_passed": after["proof"]["audit"]["passed"],
            "audit_total": after["proof"]["audit"]["total"],
            "attempts": len(after["attempts"]),
            "proof_hash": after["proof"]["proof_hash"],
        },
    }
    (ROOT / ".data" / "sponsor-pending.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("Waiting for exact persisted traces:", before_trace, after["telemetry"]["trace_id"], flush=True)
    for label in ("before", "after"):
        data = readback(receipt[label]["trace_id"], settings.neatlogs_api_key)
        spans = data["spans"]
        receipt[label]["readback"] = {
            "http_status": 200,
            "exact_trace_id": data["_id"],
            "status": data["status"],
            "span_count": len(spans),
            "hierarchy_valid": True,
            "spans": [
                {
                    "name": s["node_name"],
                    "type": s["node_type"],
                    "id": s["span_id"],
                    "parent": s.get("parent_span_id"),
                    "metrics": json.loads(s["data"].get("output_value") or "{}").get(
                        "patchpilot_metrics", {}
                    ),
                }
                for s in spans
            ],
            "private_response_saved": True,
        }
    (EVIDENCE / "neatlogs-improvement.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
