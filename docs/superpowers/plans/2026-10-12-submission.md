# Submission implementation plan

> **For agentic workers:** Use executing-plans and dispatch independent frontend/backend work. User authorized continuous execution without permission pauses.

**Goal:** Deliver a polished, tested PatchPilot repository with real sponsor evidence and complete recording/submission materials.

**Architecture:** Preserve the FastAPI/SQLite/React boundary. Add a redacting telemetry adapter, a deterministic repair proof, a landing route and a coherent workspace design. Development evidence and business planning remain separate from runtime secrets.

**Tech stack:** Python 3.12, FastAPI, React, TypeScript, Vite, neatlogs SDK, Entire CLI, cfo.ai MCP.

**Spec:** `docs/submission-design.md`

## Global constraints
No invented customer evidence, sponsor artifacts, published posts or eligibility. Never expose `.env`. Respect protected cases and AST-only execution. Keep offline replay usable. No production mutations.

## Review focus
Absent/failed telemetry must not break repair; invalid JSON/payment pointers must not earn verified status; old runs must render; mobile/keyboard flows must remain usable; installation must select a supported interpreter.

## Tasks
- [ ] 1. Verify sponsor accounts and install supported Python/Entire; inspect current evidence.
- [ ] 2. Implement safe neatlogs spans and real SDK probe/readback; test disabled and failure paths.
- [ ] 3. Add immutable repair proof and independent counterexample audit; regression tests and live smoke.
- [ ] 4. Build landing page, premium design system and guided workspace; UI tests, responsive browser verification.
- [ ] 5. Create and read back cfo.ai financial scenario; capture genuine Entire development checkpoint.
- [ ] 6. Publish clear install/run documentation, architecture, design rationale, sponsor evidence, judging assessment and demo/submission kits.
- [ ] 7. Run backend/frontend/e2e/live checks, review changes, fix material findings, commit and push public repository.

## Progress and rulings
Ruling: work in the user's explicitly selected checkout so the existing service, `.env` and Entire repository context are retained; use a `codex/submission-ready` branch for implementation.
Ruling: the user's continuous-build authorization overrides routine skill approval handoffs; preserve design and plan artifacts before implementation.
