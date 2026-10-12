# Integrations and observability

## neatlogs: observe runtime and improve the agent

Install the pinned Python 1.4.26 SDK with normal project setup on Python 3.12. Set `NEATLOGS_API_KEY` privately in `.env`. Server startup initializes the SDK once; shutdown closes it once. Traces nest research, official-page acquisition, model calls, protected-case execution and the independent counterexample audit under the agent workflow. Optional telemetry failure never grants a successful repair verdict or breaks a repair. Raw code, case payloads, customer identifiers, prompts, API keys and model completions are excluded from telemetry; sanitized numeric/status metrics are the only recorded output.

Run `python -m scripts.compare_traces` using the project environment to regenerate the same-fixture before/after trace comparison. It loads the preserved adapter from commit `2c972e4`, tests it under the current local fixture audit and runs the improved replay agent through failure recovery. It verifies exact trace IDs, persisted span counts and parent links by authenticated readback. [Receipt](evidence/neatlogs-improvement.json). This is a controlled fixture demonstration, not an independent real-world accuracy benchmark.

The SDK's own authenticated Doctor probe also passed: [Doctor receipt](evidence/neatlogs-doctor.json). Run it privately with an environment containing the key; never paste credentials into command arguments or publish account responses. The receipt has no secrets. Provider-key availability and historic project evidence do not prove a new install's account quotas.

## Entire: retain actual development context

Entire CLI 0.11.4 was installed from the official Windows installer with a verified checksum. `entire enable --agent codex` configured `.entire/settings.json` and `.codex/hooks.json`. The GitHub app connection and local hooks have separate roles.

The recorded development review used a read-only Codex session attached through `entire session attach ... --agent codex --review`. [Checkpoint receipt](evidence/entire-checkpoint.json) records checkpoint `01M4QNEWXG1454P3MWJM7EDW0J`. This is genuine retrospective capture supported by Entire, not continuous historical hook coverage. The review identified interpreter-version reproducibility as a risk; `.python-version`, setup and Docker select Python 3.12, while package compatibility permits Python 3.13. No fabricated session or simulated checkpoint is used.

Inspect with `entire checkpoint list`, `entire checkpoint explain 01M4QNEWXG1454P3MWJM7EDW0J --json` and `entire status --detailed`. Fresh interactive Codex sessions must approve these known vendor hooks in `/hooks` before continuous capture. Do not bypass hook trust. Review session contents for private information before publishing checkpoints.

## cfo.ai: model the business

Codex connects through `codex mcp add cfoai --url https://api.cfo.ai/mcp` and browser OAuth via `codex mcp login cfoai`; no CFO API key belongs in PatchPilot's `.env`. After OAuth, a real MCP workspace read and model readback confirmed access. The saved `PatchPilot launch hypotheses` scenario separates illustrative planning from Main. Three planning cases contain editable prices, customer volume, useful repair rate, cost, review effort, operating expense and opening cash; formulas calculate revenue, direct cost, gross margin, net burn and static runway.

[Business model](business-model.md) and [readback receipt](evidence/cfo-model.json) document the planning assumptions without requiring access to a private account. Inputs are assumptions, not actual customer/financial evidence. The MCP-returned [cfo.ai table link](https://app.cfo.ai/s/p_AQKFqAYkZDJiMDlhNTEtZTAzNS00NmFiLTkwNDktY2I1MDc4NGZiMjZiJGZiMDNiNGFkLTY1NjgtNDZjZS1iMzlhLWMzNjBkNzc3ODgxZg) displayed “Failed to fetch” during browser verification despite successful MCP model reads. Navigate to PatchPilot business plan in the signed-in workspace if the link still fails; the saved JSON remains the verified result.

## SerpApi: a core dependency

Live repair depends on SerpApi Google discovery. Without adequate official version evidence, the agent abstains before code generation. Search snippets are discovery leads only; actual pages, hashes, provenance and literal source quotations support the proposal. Replay is explicitly labelled and incurs no search/model calls. [Live run receipt](live-verification.json) records actual discovery/model execution against public documentation and synthetic historical response fixtures.
