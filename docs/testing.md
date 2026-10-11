# PatchPilot Evaluation and Verification

The deliverable includes a working native Windows server, compiled React frontend, offline replay demonstrations, and a live SerpApi/Groq repair. The repaired Stripe example is a historical API migration tested on sanitized local fixtures. Real public documentation is fetched in live mode; no live payment transaction is created.

## Reproducible examples

| Example | Expected outcome | What it establishes |
| --- | --- | --- |
| Stripe invoice migration in live mode | Verified if relevant evidence and providers are available; otherwise explicit stop | Search, official source acquisition, literal citations, AI patch and protected cases. |
| Recovery from incomplete repair in replay | First patch 2/5, second patch 5/5 | Failed test feedback changes the next deterministic proposal. |
| No authoritative evidence in replay | Needs investigation, no patch | Evidence absence does not become fabricated certainty. |
| Authentication failure in replay | Needs investigation, no patch | Credential/quota failures are distinguished from schema drift. |
| Custom sanitized real response | Scoped result, refusal or failure depending on evidence and adapter compatibility | User-defined target behavior and real public research. |

## Automated coverage

Backend tests cover AST restrictions, immutable inputs, strict JSON comparison, output/numeric/list/nested queue budgets, credentials, persistent state, bounded retry, recovery, cancellation, saved passing repair restoration, source host validation, citation membership and incident relevance, missing evidence, same-origin requests, trusted local hosts, API errors and reports. Frontend tests cover editable samples, pending partner status, initial connection errors and selected-run retry recovery. Browser tests cover an end-to-end repair/recovery, evidence/diff/tests/report download, phone layout, invalid JSON and credential-bearing input.

Use the exact commands in README. External network providers are mocked in automated tests; the explicit live smoke is separate. One upstream Starlette TestClient deprecation warning is currently emitted because runtime networking uses httpx; it does not indicate a failed check.

## Independent review

A separate read-only reviewer examined the whole application. The review identified source relevance without search hints, selected-run polling recovery, local Host validation, restart restoration and verifier resource/comparison boundaries. Each finding received a regression test and a fix. SQLite connections now close deterministically. The review did not find an interpreter escape.

## UI verification ledger

The code-native design inventory is in `system-design.md`. Browser QA inspected the actual default viewport, 1440x1000 desktop, and 390x844 phone layouts. Navigation, intake, timeline, evidence, diff, before/after results and report download were exercised. The first viewport preserves the workbench heading, investigation action and sample cards. The navy navigation, white panels, blue controls and restrained green verification state follow the inventory. Desktop repair and mobile screenshots are saved under `docs/assets/`.

## Practical limits

Only a bounded single adapter is repaired; arbitrary repositories, package installation and production remediation are intentionally excluded. Inputs must be sanitized. Fetched-source authority/version/token checks and literal quote membership do not constitute formal semantic proof of causality. Supplied acceptance cases, strict output comparison and reviewer inspection establish the tested scope. Expanding coverage to unseen versions and real SDK execution is future work. Docker packaging is provided but the native runtime is the exercised deployment. Partner SDK/CLI/account-backed compliance remains pending.
