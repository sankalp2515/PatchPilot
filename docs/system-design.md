# PatchPilot System Design

## Operational workflow

1. Intake validates `IncidentRequest`: title, vendor, target_version, mode (`replay` or `live`), source_code, entrypoint, cases, and search hints. Limits: 12,000 code characters, 12 cases, 100,000 serialized JSON characters, three patch attempts, three searches, 240 seconds per run. Credentials never enter the browser.
2. Planning records reproducible baseline, failure classification, targeted vendor research, evidence inspection, patch generation, verification, and bounded recovery.
3. Baseline executes the original adapter through the restricted interpreter against immutable acceptance cases. An already passing adapter ends as `no_change`; 401/403/429-like incidents end as `needs_human` without code generation.
4. Search uses SerpApi Google discovery with a vendor host constraint, version, and symptom. Failed transport calls have a bounded retry. Discovery URLs, query, search ID, and provenance are persisted without request keys.
5. Context accepts at most three sources from exact allowlisted official HTTPS hosts, validates every redirect, caps response bytes, extracts visible text, and stores hashes and relevant passages. Acquisition inspects at most three direct official candidates per query and may inspect one Stripe release index plus three related candidates. No useful fetched evidence ends as `needs_human`; snippets cannot unlock repair.
6. LLM generates a JSON patch proposal containing code, diagnosis, supporting evidence IDs and literal quotes. Source passages and user code are delimited untrusted content. The prompt enumerates allowed Python nodes and callable methods. The server checks citation IDs and quotation membership, then validates the AST.
7. Verification runs the patch against the same protected cases. A wrong patch produces actual observed/expected values as feedback to the next attempt. The test cases never change. Cancellation is checked between tool steps. Exhausted attempts end `unverified`.
8. Finalization stores code, unified diff, diagnosis, citations, evidence hashes, case results, attempts, duration, usage, and limitations. JSON and Markdown exports expose the evidence chain.

## State and data

SQLite in `.data/patchpilot.db` uses WAL, a per-operation connection, and transactional JSON run snapshots. A run has an ID, created/updated timestamps, status, phase, input, plan, events, sources, attempts, baseline, verification, proposed code, and metrics. Atomic read-modify-write protects concurrent cancellation. On startup, incomplete runs are moved to a recoverable interrupted state. Explicit resume preserves completed research and previous attempts; completed runs are rerun as new IDs so history stays honest.

States: queued -> planning -> baseline -> researching -> context -> repairing -> verifying -> verified / no_change / needs_human / unverified / failed / cancelled / interrupted. Phase changes are timestamped events. Retries record the prior failure and changed action. User cancellation is durable and wins over a later worker write.

## Verification implementation

User/model code is parsed, never executed with Python exec/eval. A small interpreter handles literals, dictionaries/lists, indexing, assignments, conditions, bounded loops/comprehensions, arithmetic, safe JSON methods and a named adapter function. It forbids imports, dunder identifiers, arbitrary attributes/calls, classes, globals, exceptions and shell access. An operation counter caps work at 20,000 steps, including nested data traversal; traversal queues and mutable list growth are checked before allocation. Outputs must be finite JSON with bounded size and strict canonical comparison. Verification runs off the API event loop so local requests and cancellation remain responsive. This is a constrained adapter repair product, not an arbitrary-code sandbox.

## API

`GET /api/health`, `GET /api/config`, `GET /api/examples`, `POST /api/runs`, `GET /api/runs`, `GET /api/runs/{id}`, `POST /api/runs/{id}/cancel`, `POST /api/runs/{id}/resume`, `GET /api/runs/{id}/export?format=json|markdown`. Poll detail every 1 second during active work. Return 422 for invalid input, 404 for unknown runs, 409 for invalid resume. Same-origin browser requests plus JSON-only mutation endpoints block cross-origin local-service writes.

## UI design inventory

Desktop uses a 230px dark navy navigation rail, broad white workbench, and a contextual right-side inspector. Palette: navy #15243b, page #f4f6fa, ink #17283d, muted #69788a, blue #345fe8, teal #147e68. Typeface: system sans for navigation and prose, Cascadia Code/Consolas for adapter text and diffs. Controls use 8px radii, panels 12px, consistent 8px spacing increments. The signature element is the incident's connected investigation timeline and adjacent evidence-to-test record. No raster imagery is required by this developer workbench; the working concept is code-native.

First viewport: PatchPilot brand, Investigations/Examples/Integrations navigation, heading “Repair integrations with evidence”, short explanation, “New investigation”, example selection, and clear local/provider readiness. Running view exposes the eight focus areas, current task, inputs, sources, attempts, and results. Mobile collapses navigation to a top bar and inspectors below content. Keyboard focus, accessible tab labels, live progress announcements, readable contrast, and reduced motion are required.

## Test data and real information

Bundled Stripe invoice cases are sanitized historical migration fixtures based on official 2025-03-31.basil documentation. Cases exercise a single payment, multiple payments, empty payments, unrelated auth failure, missing evidence, and incomplete first repair. Offline replay uses transparent recorded evidence and a deterministic demonstration policy; it never claims live AI. Live mode uses the configured LLM and SerpApi, fetches real public documentation, and verifies against local response fixtures. Users can paste sanitized real response data and expected behavior using the custom incident editor. It never calls live payment APIs or creates transactions.

## Infrastructure and morning handoff

Python 3.12 FastAPI backend and React/Vite/TypeScript frontend; production frontend served from FastAPI at 127.0.0.1:8017. `scripts/start.ps1` starts a hidden background local process with logs; `scripts/stop.ps1` stops only its recorded PID after identity validation. `scripts/setup.ps1` installs project dependencies and builds the UI. Docker provides a reproducible optional runtime. One server remains running at handoff.

`.env` is copied privately from the specifically authorized sibling project's credential file and ignored by Git. Provider priority is explicit configuration, then Groq, then NVIDIA. Missing credentials block only live mode. Morning partner setup has an honest status panel and checklist, trace export, measured economics inputs, and CLI instructions. All sponsor claims remain pending until account-backed evidence exists.
