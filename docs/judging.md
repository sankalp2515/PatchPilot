# Judging guide

PatchPilot's concrete problem is an API response migration breaking a JSON adapter. The demonstration investigates the historical Stripe Basil invoice payment-pointer change, preserves evidence and proposes a reviewable patch. SerpApi supplies live Google discovery; fetched official pages ground the repair.

## Eight agent focus areas

| Focus | Evidence in the product | Practical limit |
|---|---|---|
| Planning | Saved baseline/research/repair/verify plan and budgets | Fixed domain workflow, not arbitrary goal decomposition |
| Tool use | Search, acquisition, proposal, interpreter and exports | Four vendor host sets; one function repair |
| State | SQLite events, sources, attempts and interrupted resume | Single process and one active investigation |
| Context | Version/incident relevance, official hosts, literal citations | Missing/stale public docs can block repair |
| Execution | Proposed Python diff and observed JSON outputs | Restricted interpreter, no repository execution |
| Recovery | Transport retry, release-index fallback, cancellation/resume | Bounded retry and manual recovery outside scope |
| Verification | Protected cases, applicable audit and hashes | Fixture correctness, not universal correctness |
| Iteration | Failed/rejected proposals feed subsequent attempts | At most three proposals; replay is deterministic |

## Partner proof

- **neatlogs:** Runtime SDK tracing uses a WORKFLOW root with tool/verification spans and live model tracing. The [readback comparison](evidence/neatlogs-improvement.json) preserves baseline commit `2c972e4`: 5/5 supplied cases but 6/20 separate audit cases. Enhanced actual replay: 5/5 and 20/20. Both trace readbacks returned HTTP 200. This is a synthetic same-contract adapter comparison, not an LLM performance benchmark.
- **Entire:** CLI 0.11.4 enabled local Codex hooks after this development chat began. A real read-only design-review session was attached retrospectively as checkpoint `01M4QNEWXG1454P3MWJM7EDW0J` to commit `791e5a4`. Inspect [checkpoint evidence](evidence/entire-checkpoint.json). Do not characterize earlier work as continuously hook-captured.
- **cfo.ai:** [Saved readback](evidence/cfo-model.json) covers Base, Conservative and Growth scenarios with 45 selected cells, 44 nonempty cells and zero formula errors. All customers, pricing, rates, costs and cash are illustrative USD hypotheses.
- **SerpApi:** Show a live run's Google query/discovery provenance, actual acquisition, version-specific quote, patch and results. [Live verification](live-verification.json) is separate from offline replay.

## Assessment against the NeatHack rubric

| Published weight | Strength to demonstrate | Gap to disclose |
|---|---|---|
| Agent behavior — 30% | Bounded plan, real tools, feedback and unresolved outcomes | Narrow adapter domain |
| Partner integration — 25% | Account-backed neatlogs, Entire and cfo.ai artifacts | Entire import timing; no continuous earlier capture |
| Demo — 20% | Clear baseline → evidence → patch → tested proof | Video remains an external recording/upload step |
| Building in public — 15% | Public code and ready-to-post explanation | Do not claim an event post without its actual link |
| Originality — 10% | Evidence-bound repair plus contract-specific counterexamples | No claim of uniqueness beyond demonstrated design |

These are an evidence mapping, not predicted scores or winning odds. Eligibility, public posting, demo delivery and organizer acceptance are separate from functional verification. See [submission kit](submission-kit.md) for unresolved external steps.

## Assessment against the SerpApi rubric

The event considers these together, with no fixed percentage weights.

| Criterion | Assessment and verifiable evidence | Practical limitation |
|---|---|---|
| Idea strength | Clear engineering insight: a migration repair should preserve the expected contract and travel with version evidence and tested boundaries. | Value and review-time savings need interviews and pilots. |
| Originality | Thoughtful combination of live documentation discovery, literal citation gates, a restricted interpreter and contract-specific counterexample auditing. | Not a claim of inventing program repair or being the only such tool. |
| Technical complexity | Durable state/resume, bounded tool execution, AST safety, cancellation, independent checksums/audit, privacy-preserving traces, responsive frontend and verified Docker workflow. | A single-process local service rather than distributed repository automation. |
| Usefulness | Integration engineers get a downloadable adapter, source passages, diff, protected-case results and an explicit verdict. | One Python JSON adapter; the additional audit is currently scoped to the demonstrated Stripe contract. |
| Meaningful SerpApi usage | Live repair discovers official version documentation through SerpApi. Absent sufficient evidence stops generation; snippets alone cannot support a patch. Actual discovery provenance appears in the live receipt. | Replay is deliberately offline and cannot stand in for the live-search demonstration. |

The strongest demonstration is a real search leading to a source quote and repair, followed by a rejected weak patch and a scoped successful result. The remaining competitive gap is external validation on more migration contracts and the quality of the entrant's demo and public sharing, not a missing visual theme or a fabricated testimonial.
