"""Check tracked publication files for private configuration and exact local keys."""

import subprocess

from dotenv import dotenv_values

from patchpilot.config import ROOT


def main():
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    secrets = [
        value
        for name, value in dotenv_values(ROOT / ".env").items()
        if value and name.endswith(("_KEY", "_TOKEN")) and len(value) >= 12
    ]
    problems = []
    for name in filter(None, files):
        if name == ".env" or name.startswith((".data/", ".private/", ".venv/", "web/node_modules/")):
            problems.append(name)
            continue
        path = ROOT / name
        if path.is_file() and any(secret.encode() in path.read_bytes() for secret in secrets):
            problems.append(name)
    if problems:
        print("Publication blocked: private material detected in", ", ".join(problems))
        return 1
    print("Publication check passed: no private configuration or exact configured keys in tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
