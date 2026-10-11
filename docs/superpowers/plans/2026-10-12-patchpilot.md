# PatchPilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. The user authorizes uninterrupted overnight implementation and defers partner account setup until morning.

**Goal:** Deliver a running local evidence-to-repair agent with UI, live providers, replay examples, durable state, and verified safety boundaries.

**Architecture:** React talks to a loopback FastAPI server. A bounded orchestrator persists SQLite snapshots and calls search, evidence acquisition, LLM, and a restricted adapter interpreter.

**Tech Stack:** Python 3.12, FastAPI, SQLite, httpx, React, TypeScript, Vite, pytest, Vitest, Playwright.

**Spec:** `docs/architecture.md` and `docs/system-design.md`.

## Global Constraints

- Use E:\Codex Projects\ContractMedic on branch codex/patchpilot-overnight; do not alter the sibling project.
- 12,000 code characters, 12 cases, 100,000 serialized JSON characters, three patch attempts, three searches, 240 seconds per run.
- Provider keys remain in ignored server-side .env; no arbitrary Python exec/eval or shell execution.
- SerpApi is required for live discovery; all partner compliance remains pending morning integration.
- Immutable acceptance cases determine verdicts; label replay separately from live results.

## Review Focus

- Malicious Python trying imports, dunder access, arbitrary attributes, recursion, or oversized computation must be rejected or budget-stopped.
- Empty/multiple payment records must retain semantic correctness; a first-payment-only patch must fail.
- Provider outage or irrelevant documentation must never produce a false verified state.
- Refresh/restart/cancellation must preserve durable history and bounded attempts.
- Browser errors, mobile navigation, and missing credentials must give usable recovery paths.

### Task 1: Contracts, persistence and restricted verification
Files: `patchpilot/schemas.py`, `config.py`, `store.py`, `sandbox.py`; tests `tests/test_core.py`.
Interfaces: `IncidentRequest`, `Store.create/get/list/update`, `verify(code, entrypoint, cases) -> list[dict]`.
- [x] Write tests for immutable semantic cases, malicious code, operation budget, secret rejection and persistence.
- [x] Run pytest and observe feature-missing failures.
- [x] Implement bounded schemas, transactional store, configuration and AST interpreter.
- [x] Run the core suite and commit verified behavior.

### Task 2: Evidence and provider tools
Files: `providers.py`, `examples.py`; tests `tests/test_providers.py`.
Interfaces: async `research(request, emit) -> list[dict]`, async `propose(request, evidence, feedback, emit) -> dict`.
- [x] Test search provenance, exact-host filtering, redirect boundaries, snippets-only rejection and quote validation.
- [x] Observe missing provider behavior then implement live Groq/NVIDIA and SerpApi adapters.
- [x] Add transparent recorded Stripe replay fixtures and safety examples.
- [x] Run provider tests and a bounded live smoke check; commit.

### Task 3: Durable agent and API
Files: `agent.py`, `main.py`, `observability.py`; tests `tests/test_agent.py`, `tests/test_api.py`.
Interfaces: async `Agent.run(id)`, create/list/detail/cancel/resume/export REST endpoints.
- [x] Test successful repair, failed first patch/recovery, no evidence, auth refusal, already passing input and cancellation.
- [x] Implement state machine, bounded retries, metrics, trace events and restart recovery.
- [x] Test API validation, same-origin mutations, safe configuration and exports.
- [x] Run the full backend suite and commit.

### Task 4: React workbench
Files: `web/src/App.tsx`, feature components, `api.ts`, `styles.css`; tests `web/src/App.test.tsx`.
Interfaces: typed API run models and polling; no credentials in browser.
- [x] Test example loading, incident submission, loading/error states and result panels.
- [x] Implement responsive navigation, intake editor, timeline, evidence, diff, case results, integrations and export.
- [x] Run Vitest, TypeScript and production build; inspect desktop/mobile browser screenshots.
- [x] Exercise real browser end-to-end replay; commit.

### Task 5: Handoff and whole-system verification
Files: `scripts/*.ps1`, `README.md`, Dockerfile, `docs/testing.md`, `docs/morning-integrations.md`, `docs/economics.md`.
- [x] Provide one-command setup/start/stop and sanitized real-data example.
- [x] Run live provider repair and save sanitized evidence/results.
- [x] Run all suites, security boundary cases and browser workflows.
- [x] Request fresh independent review, repair important findings, record limitations.
- [x] Leave the app running, mark plan status, and deliver local URL and guide.
