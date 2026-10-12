# User flows

Recorded replay is limited to Stripe `2025-03-31.basil`, `normalize_invoice`, and the unchanged five fixture acceptance cases. Edited vendor/version/entrypoint/cases receive a scoped refusal; use live mode for custom contracts.

## First run without credentials

The homepage's **Product walkthrough** opens a guided, read-only saved live investigation. Navigate **The problem → Find evidence → Review repair → Verify outcome → Tools and business**. The captured source text, literal citations, diff, results, trace readback, development checkpoint and illustrative business model are available in one tab without accounts or new external requests. The saved-record label and capture time remain visible. This view does not start an investigation or modify your history; **Open workspace** starts your own workflow.

Start with Docker or the native scripts in the [README](../README.md). Open the homepage, then **Open workspace**. A new installation has its own run history; screenshot investigations are not a shared hosted account.

Choose **Recovery from an incomplete repair**, keep **Recorded replay**, and start. Inspect the baseline, captured source, failed first proposal, subsequent results and bound proof. Five supplied acceptance cases and the applicable 20-case local audit are reported separately. Download code/report and inspect the diff before manual use. Replay is deterministic and offline.

## Live Stripe investigation

Configure SerpApi and one model provider privately. Select **Stripe invoice migration**, then **Live search + AI**. Start with sanitized historical fixtures. Watch the saved plan and research activity; inspect the actual search query, vendor source/version and literal citation. Compare original and proposed results. The app calls no Stripe transaction API.

Success means the reported local checks pass. If the provider is unavailable, evidence is insufficient or attempts are exhausted, inspect the reason; the app does not replace live execution with replay. See [live verification](live-verification.json) for a saved run, not a guarantee that future requests reproduce it.

## Custom incident

Open **Examples → Custom incident**. Provide one adapter function, vendor, target version, precise symptom and a JSON array of `{name, input, expected}` cases. Use sanitized data and public migration documentation. Discovery supports official Stripe, GitHub, Slack and Shopify hosts.

At most 12 supplied cases and 12,000 code characters are allowed. Define the desired output yourself; vendor documentation does not decide your application's normalization policy. The additional audit applies only to the matching Stripe example contract. Unsupported Python syntax, bad JSON and obvious credentials are rejected.

## Recovery and cancellation

Use cancellation during active work; saved artifacts remain. Cancelled/failed/unverified outcomes can be rerun as a new investigation. A service restart marks unfinished runs **Ready to resume**. Resume reuses saved evidence and prior attempts, preserving the attempt budget and rechecking a saved passing candidate.

Only one run can be active. A passing original adapter produces **No change needed** based on supplied cases. Auth/rate-limit incidents produce a human-action outcome rather than an unnecessary code patch.

## Review and handoff

Review source applicability, quote, code/diff, baseline, acceptance and audit applicability/results. Export JSON for machine inspection or Markdown for a reviewer. Keep the original contract and proof with the proposed adapter. Human review and additional production-representative tests precede integration; PatchPilot does not auto-merge or deploy.
