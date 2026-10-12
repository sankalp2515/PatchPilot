# API guide

The local API is served at [127.0.0.1:8017](http://127.0.0.1:8017). The machine-readable specification is [openapi.json](http://127.0.0.1:8017/openapi.json). Interactive Swagger/Redoc pages are disabled. There is no user authentication; this is a loopback single-user application.

## Routes

| Method | Route | Behavior |
|---|---|---|
| GET | `/api/health` | Service identity and health |
| GET | `/api/config` | Readiness, provider/model, partner status and limits; no keys |
| GET | `/api/examples` | Sanitized replay/live incident templates |
| GET | `/api/showcase` | Bundled saved live investigation and integration readbacks; no provider calls |
| GET | `/api/showcase/report` | Download the saved live investigation's Markdown report |
| POST | `/api/runs` | Validate and queue investigation; 202 |
| GET | `/api/runs` | Run summaries |
| GET | `/api/runs/{id}` | Persisted full run, events, attempts, evidence and results |
| POST | `/api/runs/{id}/cancel` | Cancel active investigation and retain artifacts |
| POST | `/api/runs/{id}/resume` | Resume interrupted run only; 202 |
| GET | `/api/runs/{id}/export?format=json` | JSON attachment |
| GET | `/api/runs/{id}/export?format=markdown` | Markdown attachment |

Poll run detail approximately once per second during work. Inspect status and limitations instead of treating a 202 response as completion. Unknown IDs return 404; conflicting lifecycle/another active run return 409; bad content type returns 415; invalid payload/export format returns 422; excessive body size returns 413. A mismatching browser Origin returns 403; unapproved Hosts are rejected.

## Request contract

| Field | Meaning |
|---|---|
| `title` | 3–160 characters |
| `vendor` | `stripe`, `github`, `slack`, `shopify` |
| `target_version` | Required, 1–100 characters |
| `mode` | `replay` (default) or `live` |
| `source_code` | One adapter; 10–12,000 characters |
| `entrypoint` | Valid bounded identifier; default `normalize_invoice` |
| `cases` | 1–12 `{name, input, expected}` objects |
| `symptom` | Observed failure, at most 2,000 characters |
| `search_hint` | Optional specific research terms, at most 200 characters |
| `max_attempts` | 1–3; default 3 |
| `replay_scenario` | `repair`, `recovery`, `no_evidence`, `auth` |

The simplest reproducible API journey uses a bundled request:

```powershell
$examples = Invoke-RestMethod http://127.0.0.1:8017/api/examples
$request = $examples[1]
$request.mode = "replay"
$run = Invoke-RestMethod http://127.0.0.1:8017/api/runs -Method Post -ContentType application/json -Body ($request | ConvertTo-Json -Depth 30)
Invoke-RestMethod "http://127.0.0.1:8017/api/runs/$($run.id)"
```

Check the template's mode before sending; use replay for a key-free run. Reports include sanitized incident content and source text, so handle exports as potentially sensitive.

## Environment and setup

| Variable | Default / use |
|---|---|
| `SERPAPI_API_KEY` | Empty; required for live discovery |
| `GROQ_API_KEY` | Empty; live Groq access |
| `NVIDIA_API_KEY` | Empty; live NVIDIA access |
| `LLM_PROVIDER` | Explicit `groq`/`nvidia`; otherwise Groq if its key exists, else NVIDIA |
| `LLM_MODEL` | Provider default unless overridden |
| `NEATLOGS_API_KEY` | Empty; optional operational telemetry |
| `DATABASE_PATH` | `.data/patchpilot.db` under the project root |
| `PORT` | Settings default 8017; actual listen port is set by startup/uvicorn |

The native start script supports `-Port`; Compose publishes fixed loopback port 8017. `.env` is server-side and ignored by Git. Preserve an existing file. Live credentials are not needed for replay. Restart the service after changes.

Live requests consume provider quota. Token/elapsed metrics are operational observations, not billing invoices. Financial scenario costs are illustrative USD assumptions, not verified provider prices. No checkout/subscription service is implemented.
