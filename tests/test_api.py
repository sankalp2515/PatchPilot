import time

from fastapi.testclient import TestClient

from patchpilot.config import Settings
from patchpilot.examples import examples
from patchpilot.main import create_app


def client(tmp_path):
    return TestClient(
        create_app(Settings(database_path=str(tmp_path / "runs.db"), _env_file=None)),
        base_url="http://127.0.0.1",
    )


def test_api_repairs_and_exports(tmp_path):
    with client(tmp_path) as api:
        response = api.post("/api/runs", json=examples()[0] | {"mode": "replay"})
        assert response.status_code == 202
        run_id = response.json()["id"]
        for _ in range(50):
            run = api.get(f"/api/runs/{run_id}").json()
            if run["status"] in {"verified", "failed"}:
                break
            time.sleep(0.02)
        assert run["status"] == "verified"
        assert "PatchPilot" in api.get(f"/api/runs/{run_id}/export?format=markdown").text
        assert api.post(f"/api/runs/{run_id}/resume").status_code == 409


def test_api_config_never_returns_credentials(tmp_path):
    settings = Settings(
        database_path=str(tmp_path / "runs.db"), groq_api_key="test-sensitive-key", _env_file=None
    )
    with TestClient(create_app(settings), base_url="http://127.0.0.1") as api:
        text = api.get("/api/config").text
        assert "test-sensitive-key" not in text
        assert set(api.get("/api/config").json()["partners"]) == {"neatlogs", "entire", "cfo_ai"}


def test_cross_origin_mutation_is_rejected(tmp_path):
    with client(tmp_path) as api:
        assert (
            api.post("/api/runs", json=examples()[0], headers={"Origin": "https://evil.example"}).status_code
            == 403
        )
        assert api.post("/api/runs", content="{}", headers={"Content-Type": "text/plain"}).status_code == 415


def test_invalid_input_and_missing_runs(tmp_path):
    with client(tmp_path) as api:
        assert api.post("/api/runs", json={}).status_code == 422
        assert api.get("/api/runs/missing").status_code == 404
        assert (
            api.post(
                "/api/runs", content="x" * 260000, headers={"Content-Type": "application/json"}
            ).status_code
            == 413
        )


def test_untrusted_host_cannot_read_or_mutate_local_workspace(tmp_path):
    with client(tmp_path) as api:
        assert api.get("/api/runs", headers={"Host": "attacker.example:8017"}).status_code == 400
        assert (
            api.post(
                "/api/runs",
                json=examples()[0] | {"mode": "replay"},
                headers={"Host": "attacker.example:8017", "Origin": "http://attacker.example:8017"},
            ).status_code
            == 400
        )


def test_saved_live_walkthrough_needs_no_keys_or_new_runs(tmp_path):
    with client(tmp_path) as api:
        response = api.get("/api/showcase")
        assert response.status_code == 200
        data = response.json()
        assert data["kind"] == "saved_live_investigation"
        assert data["run"]["input"]["mode"] == "live"
        assert data["run"]["status"] == "verified"
        assert data["run"]["proof"]["audit"]["passed"] == 20
        assert data["run"]["sources"][0]["provenance"] == "serpapi_live_fetched"
        assert data["live_trace"]["trace_id"] == data["run"]["telemetry"]["trace_id"]
        assert api.get("/api/runs").json() == []
        report = api.get("/api/showcase/report")
        assert report.status_code == 200
        assert "Saved live investigation" in report.text
        assert data["run"]["id"] in report.text
