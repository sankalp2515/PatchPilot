"""Read the bundled synthetic live investigation; never invoke external providers."""

import hashlib
import json
from pathlib import Path


def load_showcase(path=None):
    path = path or Path(__file__).parent / "assets" / "showcase.json"
    envelope = json.loads(Path(path).read_text(encoding="utf-8"))
    payload = envelope["payload"]
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    if hashlib.sha256(encoded).hexdigest() != envelope["sha256"]:
        raise ValueError("Saved investigation checksum mismatch")
    run = payload["run"]
    if payload["kind"] != "saved_live_investigation" or run["input"]["mode"] != "live":
        raise ValueError("Saved investigation must identify its live origin")
    return payload
