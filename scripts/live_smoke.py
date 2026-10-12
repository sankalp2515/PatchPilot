"""Explicit live provider check. Prints metadata and scoped verdicts, never credentials."""

import argparse
import asyncio
import json

from patchpilot.agent import Agent
from patchpilot.config import ROOT, Settings
from patchpilot.examples import examples
from patchpilot.observability import Telemetry
from patchpilot.providers import Tools
from patchpilot.store import Store


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("groq", "nvidia"))
    parser.add_argument("--model")
    args = parser.parse_args()
    overrides = {}
    if args.provider:
        overrides.update(llm_provider=args.provider, llm_model="")
    if args.model:
        overrides["llm_model"] = args.model
    settings = Settings(**overrides)
    telemetry = Telemetry(
        settings.neatlogs_api_key,
        secrets=(settings.serpapi_api_key, settings.groq_api_key, settings.nvidia_api_key),
    )
    telemetry.start()
    store = Store(settings.database_path)
    request = examples()[0] | {"mode": "live"}
    run = store.create(request)
    print("Live investigation:", run["id"], flush=True)
    try:
        await Agent(store, Tools(settings), telemetry).run(run["id"])
    finally:
        telemetry.close()
    result = store.get(run["id"])
    summary = {
        key: result[key]
        for key in (
            "id",
            "status",
            "diagnosis",
            "metrics",
            "baseline",
            "verification",
            "proof",
            "telemetry",
            "limitations",
        )
    }
    summary["sources"] = [
        {key: source[key] for key in ("id", "title", "url", "provenance", "sha256")}
        for source in result["sources"]
    ]
    summary["attempt_errors"] = [attempt["error"] for attempt in result["attempts"]]
    summary["provider"] = settings.provider
    (ROOT / "docs" / "evidence" / "live-latest-attempt.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    if result["status"] == "verified":
        (ROOT / "docs" / "live-verification.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if result["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
