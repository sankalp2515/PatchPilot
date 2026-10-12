# Security

PatchPilot is a local single-user prototype without authentication or tenant isolation. Run it on loopback. Do not expose it publicly unchanged.

## Data and execution boundaries

Live mode sends incident fields, adapter, acceptance cases and selected documentation to the configured model provider. Search hints/symptom terms go to SerpApi. Use sanitized data; obvious credential-field/token rejection is not comprehensive secret detection. Exports and SQLite history contain incident and source material.

Keys are server-side in ignored `.env`. Optional neatlogs tracing excludes prompts, code, cases and raw payloads, with automatic content/log capture disabled and allowlisted metadata. Private provider readbacks must remain outside the public repository.

Adapter code is parsed and interpreted through a bounded AST language, not executed with `exec`/`eval`. Imports, arbitrary calls, filesystem, shell and network are unavailable. Operation/data limits constrain execution; this is not a general-purpose Python sandbox. Official-host acquisition validates redirects and bounds responses. Literal citations and fixture checks reduce specific risks without proving all possible behavior.

Host/Origin checks defend a local browser boundary; they are not authentication. Hashes bind content but are not signatures. PatchPilot never automatically merges, deploys or modifies a customer repository.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting on [sankalp2515/PatchPilot](https://github.com/sankalp2515/PatchPilot/security/advisories) if available. If private reporting is unavailable, open a minimal issue requesting a private contact without including exploit details, credentials or sensitive data. No dedicated monitored security mailbox or response SLA is promised.

Include affected revision, reproduction steps, impact and sanitized evidence privately. Do not publish working exploit payloads or private records in a public issue.

## Before shared hosting

Add identity/authentication, authorization, isolation, rate limits, retention/deletion controls, provider budget accounting, audited backups and operational recovery. Shared production hosting is outside this release's verified scope.
