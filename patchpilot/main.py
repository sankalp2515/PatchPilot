import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .agent import Agent
from .config import ROOT, Settings
from .examples import examples
from .observability import Telemetry
from .providers import Tools
from .reports import markdown_report
from .schemas import IncidentRequest
from .showcase import load_showcase
from .store import TERMINAL, Store


def create_app(settings=None):
    settings = settings or Settings()
    store = Store(settings.database_path)
    tasks = {}
    telemetry = Telemetry(
        settings.neatlogs_api_key,
        secrets=[settings.serpapi_api_key, settings.groq_api_key, settings.nvidia_api_key],
    )
    agent = Agent(store, Tools(settings), telemetry)

    @asynccontextmanager
    async def lifespan(app):
        telemetry.start()
        try:
            store.interrupt_incomplete()
            yield
        finally:
            for task in tasks.values():
                if not task.done():
                    task.cancel()
            if tasks:
                await asyncio.gather(*tasks.values(), return_exceptions=True)
            telemetry.close()

    app = FastAPI(title="PatchPilot", version="0.1.0", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
    app.state.store = store
    app.state.telemetry = telemetry

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            expected = f"{request.url.scheme}://{request.headers.get('host', '')}"
            if origin and origin != expected:
                return JSONResponse(
                    {"detail": "Cross-origin local-service mutations are prohibited"}, status_code=403
                )
            if request.url.path == "/api/runs":
                if request.headers.get("content-type", "").split(";")[0] != "application/json":
                    return JSONResponse(
                        {"detail": "Incident intake requires application/json"}, status_code=415
                    )
                chunks = bytearray()
                async for chunk in request.stream():
                    chunks.extend(chunk)
                    if len(chunks) > 256000:
                        return JSONResponse({"detail": "Request body exceeds 256 KB"}, status_code=413)
                request._body = bytes(chunks)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
        )
        return response

    def find(run_id):
        run = store.get(run_id)
        if not run:
            raise HTTPException(404, "Investigation not found")
        return run

    def launch(run_id):
        tasks[run_id] = asyncio.create_task(agent.run(run_id))

    @app.get("/api/health")
    def health():
        return {"status": "ok", "app": "PatchPilot"}

    @app.get("/api/config")
    def config():
        partners = {"neatlogs": "pending", "entire": "pending", "cfo_ai": "pending"}
        try:
            evidence = json.loads((ROOT / "docs" / "integration-evidence.json").read_text(encoding="utf-8"))
            for partner in partners:
                if isinstance(evidence.get(partner), dict) and evidence[partner].get("status") == "verified":
                    partners[partner] = "verified"
        except (OSError, ValueError, AttributeError):
            pass
        return {
            "name": "PatchPilot",
            "live_ready": bool(settings.serpapi_api_key and settings.llm_key),
            "search_ready": bool(settings.serpapi_api_key),
            "model_ready": bool(settings.llm_key),
            "provider": settings.provider,
            "model": settings.model,
            "partners": partners,
            "telemetry": {"status": telemetry.status, "content_capture": False},
            "limits": {"attempts": 3, "cases": 12, "seconds": 240, "code_characters": 12000},
        }

    @app.get("/api/examples")
    def example_list():
        return examples()

    def saved_investigation():
        try:
            return load_showcase()
        except (OSError, ValueError, KeyError):
            raise HTTPException(503, "Saved investigation is unavailable or damaged") from None

    @app.get("/api/showcase")
    def showcase():
        return saved_investigation()

    @app.get("/api/showcase/report")
    def showcase_report():
        run = saved_investigation()["run"]
        return PlainTextResponse(
            f"# Saved live investigation\n\nRun: {run['id']}\n\n"
            "No new provider calls are made when viewing this record.\n\n" + markdown_report(run),
            headers={"Content-Disposition": 'attachment; filename="patchpilot-saved-live-report.md"'},
        )

    @app.post("/api/runs", status_code=202)
    async def create(request: IncidentRequest):
        active = [r for r in store.list() if r["status"] not in TERMINAL]
        if active:
            raise HTTPException(
                409, "An investigation is already running. Wait or cancel it before starting another."
            )
        run = store.create(request.model_dump())
        launch(run["id"])
        return run

    @app.get("/api/runs")
    def listing():
        return [
            {
                "id": r["id"],
                "title": r["input"]["title"],
                "vendor": r["input"]["vendor"],
                "mode": r["input"]["mode"],
                "status": r["status"],
                "created_at": r["created_at"],
                "metrics": r["metrics"],
            }
            for r in store.list()
        ]

    @app.get("/api/runs/{run_id}")
    def detail(run_id: str):
        return find(run_id)

    @app.post("/api/runs/{run_id}/cancel")
    async def cancel(run_id: str):
        run = find(run_id)
        if run["status"] in TERMINAL:
            raise HTTPException(409, "Only an active investigation can be cancelled")
        store.update(
            run_id,
            {"status": "cancelled", "phase": "cancelled", "cancel_requested": True},
            {
                "kind": "decision",
                "title": "Cancellation requested",
                "detail": "Saved artifacts are retained.",
            },
        )
        if run_id in tasks:
            tasks[run_id].cancel()
        return find(run_id)

    @app.post("/api/runs/{run_id}/resume", status_code=202)
    async def resume(run_id: str):
        run = find(run_id)
        if run["status"] != "interrupted":
            raise HTTPException(
                409,
                "Only a run interrupted by a server restart can be resumed; rerun other outcomes as a new investigation",
            )
        if any(r["status"] not in TERMINAL for r in store.list()):
            raise HTTPException(409, "Another investigation is running")
        store.update(run_id, {"status": "queued", "phase": "queued", "cancel_requested": False}, force=True)
        launch(run_id)
        return find(run_id)

    @app.get("/api/runs/{run_id}/export")
    def export(run_id: str, format: str = "json"):
        run = find(run_id)
        headers = {
            "Content-Disposition": f'attachment; filename="patchpilot-{run_id[:8]}.{"md" if format == "markdown" else "json"}"'
        }
        if format == "markdown":
            return PlainTextResponse(markdown_report(run), headers=headers)
        if format != "json":
            raise HTTPException(422, "Use json or markdown format")
        return PlainTextResponse(json.dumps(run, indent=2), media_type="application/json", headers=headers)

    dist = ROOT / "web" / "dist"
    if (dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/")
    @app.get("/app")
    @app.get("/app/{path:path}")
    def index(path: str = ""):
        if (dist / "index.html").exists():
            return FileResponse(dist / "index.html")
        return PlainTextResponse(
            "PatchPilot API is running. Build web/ to open the workbench. API specification: /openapi.json"
        )

    return app


app = create_app()
