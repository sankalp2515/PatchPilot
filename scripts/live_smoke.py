"""Explicit live provider check. Prints metadata and scoped verdicts, never credentials."""

import asyncio
import json

from patchpilot.agent import Agent
from patchpilot.config import ROOT, Settings
from patchpilot.examples import examples
from patchpilot.providers import Tools
from patchpilot.store import Store


async def main():
    settings = Settings()
    store = Store(settings.database_path)
    request = examples()[0] | {"mode": "live"}
    run = store.create(request)
    print("Live investigation:", run["id"], flush=True)
    await Agent(store, Tools(settings)).run(run["id"])
    result = store.get(run["id"])
    summary = {
        key: result[key] for key in ("id", "status", "diagnosis", "metrics", "verification", "limitations")
    }
    summary["sources"] = [
        {key: source[key] for key in ("id", "title", "url", "provenance", "sha256")}
        for source in result["sources"]
    ]
    summary["attempt_errors"] = [attempt["error"] for attempt in result["attempts"]]
    (ROOT / "docs" / "live-verification.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
