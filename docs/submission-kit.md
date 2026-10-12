# Submission kit

## Ready-to-use project copy

**Name:** PatchPilot
**Tagline:** From broken adapter to evidence-backed repair.
**Repository:** https://github.com/sankalp2515/PatchPilot
**Demo video:** Add the actual published recording URL before submission.
**Public event post:** Add the actual post URL; no post is claimed here.

**Short description**

PatchPilot is a local AI repair agent for API response migrations. It reproduces a failing Python adapter, uses SerpApi to discover version-specific official documentation, generates a cited minimal patch and verifies it against protected acceptance cases. A contract-specific counterexample audit exposes plausible but incomplete Stripe invoice fixes. Reviewers can inspect the evidence, diff, actual results and hashes in a portable repair report.

**Technical description**

React/TypeScript and FastAPI provide a local workspace backed by SQLite checkpoints. Live Google discovery uses SerpApi; Groq or NVIDIA proposes structured repairs. Official-host acquisition, source/version relevance, literal citations and a restricted Python AST interpreter constrain the workflow. Up to three proposals and a 240-second timeout bound execution. Replay runs without accounts and is clearly labelled deterministic. PatchPilot does not auto-merge or deploy.

**What makes it useful**

A patch should travel with its reason and tested boundaries. The demonstration preserves baseline failure, actual fetched evidence and a cited proposal, then reports five protected acceptance cases separately from a 20-case local Stripe audit. The adapter/evidence/proof remain reviewable after the run.

## Evidence package

| Item | Location | Disclosure |
|---|---|---|
| Product screenshots | `docs/assets/landing-desktop.png`, `workspace-desktop.png` | Actual local interface; homepage dossier is labelled illustration |
| Sponsor evidence sheet | [Standalone exported readback](evidence/sponsor-evidence.html) | Actual persisted trace metrics and cfo.ai values, clearly labelled as an export rather than a partner dashboard |
| Live run | [live-verification.json](live-verification.json) | Real search/model/document acquisition, historical synthetic fixtures |
| neatlogs improvement | [neatlogs-improvement.json](evidence/neatlogs-improvement.json) | Baseline commit `2c972e4`, 5/5 + 6/20 versus enhanced replay 5/5 + 20/20; not an LLM benchmark |
| Entire review | [entire-checkpoint.json](evidence/entire-checkpoint.json) | Genuine read-only session import tied to commit; not continuous earlier hook capture |
| cfo.ai scenarios | [cfo-model.json](evidence/cfo-model.json), [economics](economics.md) | Saved/read-back illustrative USD hypotheses, no actual traction |
| Architecture/agent scope | [architecture](architecture.md), [judging guide](judging.md) | Narrow local repair product and explicit limitations |
| Reproduction | [README](../README.md) | Key-free replay plus separately configured live mode |

No credentials, private provider responses or customer records belong in the published evidence. Telemetry uses content exclusion and allowlisted metadata.

## NeatHack delivery

Use the [NeatHack demo script](demo-scripts.md#neathack--250). Keep the video at or below three minutes and explicitly show all three partners: neatlogs, Entire and cfo.ai. Explain the genuine integration rather than showing logos alone.

The event requires a public quote of the official neatlogs submission post on X with team, name, project, repository, video and `#neatHack`. Draft text below is prepared copy, not evidence of publication. Post from the entrant's actual identity and save the resulting URL. The planned window is October 12, 7:00â€“11:55 PM IST; confirm the final cutoff on Discord. Discord is the source of deadline updates, not a substitute for the required X quote post. Confirm current organizer instructions at submission time.

**Draft public post**

> Building PatchPilot for #neatHack: an agent that researches API migrations, proposes a minimal repair and keeps evidence with the patch. SerpApi powers discovery; neatlogs makes the repair loop inspectable; Entire preserves a real review checkpoint; cfo.ai models explicit launch assumptions. The Stripe demo separates protected cases from a local counterexample audit. Repository: https://github.com/sankalp2515/PatchPilot

Use this as the text accompanying the required quote post. Do not imply continuous Entire capture, production customers or measured business demand.

**Draft final entry**

> PatchPilot â€” From broken adapter to evidence-backed repair.
> Repo: https://github.com/sankalp2515/PatchPilot
> Video: [insert actual video URL]
> Public quote post: [insert actual post URL]
> Partner evidence: repository docs/evidence; neatlogs trace readback, genuine Entire review checkpoint and saved cfo.ai scenario model.
> Run locally: docker compose up --build -d; replay needs no keys.
> Scope: single-function JSON adapter repair; historical Stripe fixture demonstration, reviewed exports and no automatic deployment.

## SerpApi delivery

Use the [SerpApi demo script](demo-scripts.md#serpapi--245), showing a real live search as part of the core repair flow. Recorded replay alone does not demonstrate live discovery. Attach the public repository and actual video URL, and use the description above.

The rendered SerpApi homepage was verified in the browser and shows **Submit your project** with the deadline **October 12, 2026, 23:59 IST**. An earlier text-only extraction included a hidden closed-state message; it did not establish that the portal was closed. Use the GitHub-authenticated submission dashboard and preserve the actual acknowledgment. A prepared repository or saved draft is not an accepted entry.

## Remaining external steps

1. Record a real walkthrough, trim within the event limit and upload it.
2. Confirm entrant identity, eligibility and organizer deadlines.
3. Publish the required event quote post and save its actual link.
4. Submit SerpApi through its GitHub-authenticated dashboard; publish the required neatHack quote post with the actual video URL.
5. Preserve submission acknowledgment; verify public repository access from a logged-out browser.

A submission package is prepared; the video, social publication and accepted event entry are separate deliverables. No posts, uploads or submissions are fabricated here.
