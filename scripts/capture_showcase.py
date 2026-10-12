"""Package a verified, synthetic live investigation for an offline product walkthrough."""

import argparse
import hashlib
import json

from dotenv import dotenv_values

from patchpilot.config import ROOT, Settings
from patchpilot.examples import examples
from patchpilot.store import Store, now
from scripts.compare_traces import readback


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()
    settings = Settings()
    run = Store(settings.database_path).get(args.run_id)
    fixture = examples()[0] | {"mode": "live"}
    if not run or run["input"] != fixture or run["status"] != "verified":
        raise ValueError("Only a verified live run of the unchanged public fixture can be packaged")
    if not run["sources"] or any(s["provenance"] != "serpapi_live_fetched" for s in run["sources"]):
        raise ValueError("Actual live-fetched source provenance is required")
    trace_id = run["telemetry"]["trace_id"]
    trace = readback(trace_id, settings.neatlogs_api_key)
    safe_trace = {
        "source": "Authenticated exact neatlogs live trace readback",
        "trace_id": trace_id,
        "status": trace["status"],
        "span_count": len(trace["spans"]),
        "prompt_tokens": trace.get("promptTokens"),
        "completion_tokens": trace.get("completionTokens"),
        "total_tokens": trace.get("totalTokensUsed"),
        "spans": [
            {
                "name": span["node_name"],
                "type": span["node_type"],
                "id": span["span_id"],
                "parent": span.get("parent_span_id"),
                "metrics": json.loads(span["data"].get("output_value") or "{}").get("patchpilot_metrics", {}),
            }
            for span in trace["spans"]
        ],
    }
    evidence = ROOT / "docs" / "evidence"

    def read(name):
        return json.loads((evidence / name).read_text(encoding="utf-8"))

    cfo = read("cfo-model.json")
    payload = {
        "kind": "saved_live_investigation",
        "captured_at": now(),
        "disclosure": "A completed real SerpApi and model investigation using synthetic historical fixtures. Browsing this saved record makes no new provider calls.",
        "run": run,
        "live_trace": safe_trace,
        "comparison": read("neatlogs-improvement.json"),
        "entire": read("entire-checkpoint.json"),
        "business": {key: cfo[key] for key in ("source", "scenario", "coverage", "cases", "rows")},
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    secrets = [
        value
        for key, value in dotenv_values(ROOT / ".env").items()
        if value and key.endswith(("_KEY", "_TOKEN")) and len(value) >= 12
    ]
    if any(secret.encode() in encoded for secret in secrets):
        raise ValueError("Configured secret detected; capture rejected")
    folder = ROOT / "patchpilot" / "assets"
    folder.mkdir(exist_ok=True)
    envelope = {"sha256": hashlib.sha256(encoded).hexdigest(), "payload": payload}
    (folder / "showcase.json").write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (evidence / "live-trace.json").write_text(json.dumps(safe_trace, indent=2), encoding="utf-8")
    print(
        f"Saved live investigation {run['id']}: {len(trace['spans'])} authenticated spans; complete local snapshot"
    )


if __name__ == "__main__":
    main()
