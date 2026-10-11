"""Local trace preparation contract; partner SDK export is intentionally pending.

Place actual neatlogs SDK root/nested spans around agent.run, tools.research,
tools.fetch, tools.propose and verification after the user's account setup.
Local event JSON is not a neatlogs trace and must never be labeled as one.
"""

import re

TOKEN = re.compile(r"(?:gsk_[A-Za-z0-9]{20,}|nvapi-[A-Za-z0-9]{20,}|sk_(?:live|test)_[A-Za-z0-9]{12,})")


def event_record(kind: str, title: str, detail: str) -> dict[str, str]:
    return {"kind": kind, "title": TOKEN.sub("[REDACTED]", title), "detail": TOKEN.sub("[REDACTED]", detail)}
