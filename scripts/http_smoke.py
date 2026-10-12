"""Key-free installation check using a synthetic recovery fixture."""

import argparse
import time

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8017")
    args = parser.parse_args()
    with httpx.Client(base_url=args.base_url, timeout=10) as client:
        assert client.get("/api/health").json()["status"] == "ok"
        assert client.get("/").status_code == 200
        assert client.get("/app").status_code == 200
        examples = client.get("/api/examples").json()
        request = examples[1] | {"title": "Installation smoke · replay recovery", "mode": "replay"}
        created = client.post("/api/runs", json=request)
        created.raise_for_status()
        run_id = created.json()["id"]
        for _ in range(100):
            run = client.get(f"/api/runs/{run_id}").json()
            if run["status"] in {"verified", "failed", "unverified", "needs_human", "cancelled"}:
                break
            time.sleep(0.2)
        assert run["status"] == "verified", run["status"]
        assert len(run["attempts"]) == 2
        assert run["proof"]["acceptance_passed"] == run["proof"]["total"] == 5
        assert run["proof"]["audit"]["passed"] == run["proof"]["audit"]["total"] == 20
        report = client.get(f"/api/runs/{run_id}/export?format=markdown")
        assert report.status_code == 200
        assert "proof" in report.text.lower()
        # The report route is also tested by API regression tests.
        print(
            f"Recovery verified: 5/5 acceptance, 20/20 local audit, 2 attempts; report HTTP {report.status_code}; {args.base_url}"
        )


if __name__ == "__main__":
    main()
