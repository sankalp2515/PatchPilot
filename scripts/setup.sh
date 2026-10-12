#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if command -v uv >/dev/null 2>&1; then
  uv sync --python 3.12 --extra dev
else
  python3.12 -m venv .venv
  .venv/bin/python -m pip install -r requirements-dev.txt
fi
(cd web && npm ci && npm run build)
printf '%s\n' 'Setup complete. Start with: sh scripts/start.sh'
