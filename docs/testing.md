# Verification and evidence

Use Python 3.12 and Node.js 22. Tests operate on disposable SQLite databases and controlled provider responses. No credentials are needed for regression checks or replay browser journeys.

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m ruff check patchpilot tests scripts
.venv\Scripts\python.exe -m ruff format --check patchpilot tests scripts
npm --prefix web test
npm --prefix web run build
.\scripts\start.ps1
npm --prefix web run test:e2e
.venv\Scripts\python.exe -m scripts.http_smoke
```

## Exercised behavior

Final local verification: **86 backend tests, 8 UI tests and 4 browser journeys passed**, plus Ruff lint/format, TypeScript/production build, publication key scan, and the final key-free Docker HTTP smoke. The final live example passed 5/5 acceptance and 20/20 local audit using one SerpApi discovery operation, one model proposal, 3,286 reported tokens and 6.45 seconds. These are measured example results, not latency or quality guarantees. [Exact persisted live trace receipt](evidence/live-trace.json) retains 13 spans and typed token counts.

Backend checks cover AST escape attempts, operation/size budgets, strict boolean-vs-number JSON comparison, exact official hosts and redirects, version/incident relevance, literal citations, retries, protected cases, durable resume/cancel, same-origin/Host protections, proof/checksum binding, 20-case scoped counterexample policy, live `.md` source applicability, conflicting user contracts, legacy reports, telemetry disabled/unavailable behavior, metadata privacy and typed LLM usage.

Frontend checks cover landing navigation, local installation/pricing disclosures, old-run proof absence and independent audit display. Four Playwright journeys exercise landing-to-workspace, deterministic replay recovery/export, missing evidence and credential-failure refusal. Visual checks inspect 1440-pixel desktop and 390-pixel phone landing/workspace layouts, with screenshots in `docs/assets/`.

Docker was built and run without `.env` on a separate loopback port. Its health check passed; `/`, `/app`, API replay recovery and Markdown report returned successfully, with 5/5 protected cases, 20/20 local audit and two attempts. Reproduce with `docker compose up --build -d` and `python -m scripts.http_smoke` from a developer environment; the HTTP script can target a different port using `--base-url`.

## Real integrations

[Successful live reference](live-verification.json) records actual SerpApi search, official Stripe page acquisition and Groq proposals against synthetic historical response fixtures. Its final verdict passed 5 supplied cases and 20 local counterexamples. This is a real provider run, not a payment transaction or broad accuracy benchmark. Subsequent [Groq quota refusal](evidence/live-groq-quota.json) and [NVIDIA unverified run](evidence/live-nvidia-unverified.json) are preserved, not overwritten as successes. The [latest attempt](evidence/live-latest-attempt.json) may differ from the successful reference. NVIDIA's retired Llama default returned HTTP 410; an available GPT-OSS model was tested but did not earn a verified verdict within budget.

[neatlogs improvement](evidence/neatlogs-improvement.json) records exact persisted traces and their parent hierarchy. The pre-upgrade adapter passes 5/5 supplied cases but 6/20 counterexamples; the improved replay agent passes 5/5 and 20/20 after a controlled failed attempt. [SDK Doctor](evidence/neatlogs-doctor.json) independently verified trace finalization, hierarchy and numeric token preservation. [Entire](evidence/entire-checkpoint.json) and [cfo.ai](evidence/cfo-model.json) are actual tool readbacks, not mocked artifacts.

## Limits

A successful regression suite does not prove arbitrary migration correctness, production safety or customer demand. Hashes are reproducible checksums, not signatures or tamper-proof attestations. Source quotation and topical matching do not formally establish causality. No public multi-user hosting, billing, payment execution or arbitrary repository repair is claimed. One upstream Starlette TestClient/httpx deprecation warning remains.
