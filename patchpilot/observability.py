"""Optional, content-free SDK tracing. Telemetry must never stop a repair."""

import json
import math
import re
import sys
from contextlib import contextmanager

TOKEN = re.compile(r"(?:gsk_[A-Za-z0-9]{20,}|nvapi-[A-Za-z0-9]{20,}|sk_(?:live|test)_[A-Za-z0-9]{12,})")


def redact(value, secrets=()):
    value = TOKEN.sub("[REDACTED]", value)
    for secret in sorted(filter(None, secrets), key=len, reverse=True):
        value = value.replace(secret, "[REDACTED]")
    return value


def event_record(kind: str, title: str, detail: str, secrets=()) -> dict[str, str]:
    return {"kind": kind, "title": redact(title, secrets), "detail": redact(detail, secrets)}


SAFE_FIELDS = {
    "mode",
    "status",
    "outcome",
    "passed",
    "total",
    "source_count",
    "attempt",
    "recovery",
    "audit_passed",
    "audit_total",
    "tokens",
    "prompt_tokens",
    "completion_tokens",
    "provider",
    "model",
}
CONTENT_FIELDS = {
    "input",
    "output",
    "input.value",
    "output.value",
    "source_code",
    "cases",
    "prompt",
    "messages",
    "exception.message",
    "exception.stacktrace",
}


class SafeSpan:
    def __init__(self, owner, span=None):
        self.owner, self.span = owner, span
        self.trace_id = None
        self.fields = {}
        if span is not None:
            try:
                trace_id = span.get_span_context().trace_id
                if trace_id:
                    self.trace_id = f"{trace_id:032x}"
            except Exception:
                owner.status = "unavailable"

    def set(self, **fields):
        if self.span is None:
            return
        for name, value in fields.items():
            if name not in SAFE_FIELDS or not isinstance(value, (str, int, float, bool)):
                continue
            if name in {"tokens", "prompt_tokens", "completion_tokens"} and (
                type(value) is not int or value < 0
            ):
                continue
            value = redact(value, self.owner.secrets) if isinstance(value, str) else value
            self.fields[name] = value
            try:
                self.span.set_attribute(f"patchpilot.{name}", value)
                canonical = {
                    "model": "neatlogs.llm.model_name",
                    "provider": "neatlogs.llm.provider",
                    "prompt_tokens": "neatlogs.llm.token_count.prompt",
                    "completion_tokens": "neatlogs.llm.token_count.completion",
                    "tokens": "neatlogs.llm.token_count.total",
                }.get(name)
                if canonical:
                    self.span.set_attribute(canonical, value)
            except Exception:
                self.owner.status = "unavailable"
        try:
            self.span.set_attribute(
                "neatlogs.metadata", json.dumps(self.fields, sort_keys=True, allow_nan=False)
            )
        except Exception:
            self.owner.status = "unavailable"
        try:
            self.span.set_attribute(
                "output.value",
                json.dumps({"patchpilot_metrics": self.fields}, sort_keys=True, allow_nan=False),
            )
            self.span.set_attribute("output.mime_type", "application/json")
        except Exception:
            self.owner.status = "unavailable"


class Telemetry:
    def __init__(self, key="", *, secrets=(), sdk=None):
        self.key = key
        self.secrets = tuple(secrets) + (key,)
        self.sdk = sdk
        self.status = "disabled" if not key else "configured"
        self.started = self.initialized = self.closed = False

    def metrics_output(self, value):
        """Allow only our exact metrics envelope; never preserve captured outputs."""
        if not isinstance(value, str):
            return None
        try:
            envelope = json.loads(value)
        except (ValueError, TypeError):
            return None
        if not isinstance(envelope, dict) or set(envelope) != {"patchpilot_metrics"}:
            return None
        fields = envelope["patchpilot_metrics"]
        if not isinstance(fields, dict) or not set(fields).issubset(SAFE_FIELDS):
            return None
        for name, item in fields.items():
            if not isinstance(item, (str, int, float, bool)) or (
                isinstance(item, float) and not math.isfinite(item)
            ):
                return None
            if name in {"tokens", "prompt_tokens", "completion_tokens"} and (
                type(item) is not int or item < 0
            ):
                return None
        fields = {
            name: redact(item, self.secrets) if isinstance(item, str) else item
            for name, item in fields.items()
        }
        return json.dumps({"patchpilot_metrics": fields}, sort_keys=True, allow_nan=False)

    def mask(self, item):
        if isinstance(item, dict):
            result = {}
            for k, v in item.items():
                if k == "output.value":
                    metrics = self.metrics_output(v)
                    if metrics is not None:
                        result[k] = metrics
                    continue
                if k in CONTENT_FIELDS or k.startswith(("gen_ai.prompt", "gen_ai.completion")):
                    continue
                if k == "neatlogs.metadata" and isinstance(v, str):
                    try:
                        result[k] = json.dumps(self.mask(json.loads(v)), sort_keys=True, allow_nan=False)
                    except (ValueError, TypeError):
                        continue
                else:
                    result[k] = self.mask(v)
            return result
        if isinstance(item, list):
            return [self.mask(v) for v in item]
        return redact(item, self.secrets) if isinstance(item, str) else item

    def start(self):
        if self.started:
            return
        self.started = True
        if not self.key:
            return
        try:
            if self.sdk is None:
                import neatlogs

                self.sdk = neatlogs
            self.sdk.init(
                api_key=self.key,
                workflow_name="patchpilot",
                instrumentations=[],
                capture_logs=False,
                mask=self.mask,
                register_shutdown_handlers=False,
            )
            self.initialized = True
            self.status = "enabled"
        except Exception:
            self.status = "unavailable"

    @contextmanager
    def span(self, name, kind, **fields):
        context = None
        raw = None
        if self.initialized and not self.closed:
            try:
                context = self.sdk.trace(name, kind=kind)
                raw = context.__enter__()
            except Exception:
                context = None
                self.status = "unavailable"
        span = SafeSpan(self, raw)
        span.set(**fields)
        try:
            yield span
        except BaseException:
            span.set(outcome="failed")
            if context is not None:
                try:
                    context.__exit__(*sys.exc_info())
                except Exception:
                    self.status = "unavailable"
            raise
        else:
            if context is not None:
                try:
                    context.__exit__(None, None, None)
                except Exception:
                    self.status = "unavailable"

    def close(self):
        if self.closed:
            return
        self.closed = True
        if self.initialized:
            try:
                self.sdk.shutdown()
            except Exception:
                self.status = "unavailable"
