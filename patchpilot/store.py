import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

TERMINAL = {"verified", "no_change", "needs_human", "unverified", "failed", "cancelled", "interrupted"}


def now():
    return datetime.now(UTC).isoformat()


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, updated TEXT, data TEXT)")

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=15)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def create(self, request):
        run = {
            "id": uuid.uuid4().hex,
            "created_at": now(),
            "updated_at": now(),
            "status": "queued",
            "phase": "queued",
            "input": request,
            "plan": [],
            "events": [],
            "sources": [],
            "attempts": [],
            "baseline": [],
            "verification": [],
            "proposed_code": "",
            "diff": "",
            "diagnosis": "",
            "citations": [],
            "proof": None,
            "telemetry": {"status": "disabled", "trace_id": None},
            "limitations": [],
            "metrics": {"search_calls": 0, "model_calls": 0, "tokens": 0, "elapsed_seconds": 0},
            "cancel_requested": False,
        }
        with self.connect() as db:
            db.execute("INSERT INTO runs VALUES (?, ?, ?)", (run["id"], run["updated_at"], json.dumps(run)))
        return run

    def get(self, run_id):
        with self.connect() as db:
            row = db.execute("SELECT data FROM runs WHERE id = ?", (run_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def list(self):
        with self.connect() as db:
            rows = db.execute("SELECT data FROM runs ORDER BY updated DESC LIMIT 100").fetchall()
        return [json.loads(row[0]) for row in rows]

    def update(self, run_id, changes=None, event=None, force=False):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT data FROM runs WHERE id = ?", (run_id,)).fetchone()
            if not row:
                return None
            data = json.loads(row[0])
            if data["status"] == "cancelled" and not force:
                return data
            data.update(changes or {})
            if event:
                data["events"].append({"at": now(), **event})
            data["updated_at"] = now()
            db.execute(
                "UPDATE runs SET updated=?, data=? WHERE id=?", (data["updated_at"], json.dumps(data), run_id)
            )
        return data

    def interrupt_incomplete(self):
        for run in self.list():
            if run["status"] not in TERMINAL:
                self.update(
                    run["id"],
                    {"status": "interrupted", "phase": "interrupted"},
                    {
                        "kind": "recovery",
                        "title": "Server restarted",
                        "detail": "Resume this investigation to continue from saved evidence and attempts.",
                    },
                )
