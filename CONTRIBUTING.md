# Contributing

PatchPilot is a local research-and-repair MVP. Keep changes focused, preserve explicit replay/live labels, and do not broaden security or correctness claims without evidence.

## Development

Use Python 3.12 and Node.js 22.12 or newer. Install locked Python dependencies with `uv sync --python 3.12 --extra dev` and frontend dependencies with `npm --prefix web ci`. Preserve private `.env`; use replay for normal development.

Run backend tests and lint, frontend tests and build:

```sh
uv run pytest -q
uv run ruff check patchpilot tests scripts
npm --prefix web test
npm --prefix web run build
```

For browser verification, build/start the application, install Playwright Chromium and run `npm --prefix web run test:e2e`. A local HTTP smoke is available as `uv run python scripts/http_smoke.py --base-url http://127.0.0.1:8017`. Live smoke consumes real quota; run it separately only with configured credentials.

## Review expectations

Explain the problem, resulting behavior and relevant validation. Keep protected cases immutable. Tests should establish behavior rather than mirror implementation. Citation/acquisition changes need hostile/missing source cases; interpreter changes need unsupported-code and resource-limit cases; state changes need cancellation/restart checks.

Never commit credentials, private account responses, customer payloads, database history or generated local logs. Screenshots must not expose secrets. Keep partner evidence factual and synthetic fixtures labelled. A fixture pass is not universal correctness. See [SECURITY.md](SECURITY.md) for private reporting and [system design](docs/system-design.md) for boundaries.

Use a focused branch/PR and include updated docs when changing API, configuration, proof semantics or execution limits. Third-party contributions are licensed under the repository's MIT license.
