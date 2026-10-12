import copy
import json
from contextlib import contextmanager

import pytest

from patchpilot.examples import REPAIR_CODE, examples
from patchpilot.observability import Telemetry
from patchpilot.proof import audit_cases, build_proof
from patchpilot.sandbox import verify


class FakeSDK:
    def __init__(self, fail=False):
        self.fail = fail
        self.initializations = []
        self.spans = []
        self.stack = []
        self.stops = 0

    def init(self, **kwargs):
        self.initializations.append(kwargs)
        if self.fail:
            raise RuntimeError("secret failure")

    @contextmanager
    def trace(self, name, kind=None):
        record = {
            "name": name,
            "kind": kind,
            "parent": self.stack[-1]["name"] if self.stack else None,
            "attrs": {},
        }
        record["set_attribute"] = None
        self.spans.append(record)
        self.stack.append(record)

        class Span:
            def set_attribute(self, key, value):
                record["attrs"][key] = value

            def get_span_context(self):
                return type("Context", (), {"trace_id": 42})()

        try:
            yield Span()
        finally:
            self.stack.pop()

    def shutdown(self):
        self.stops += 1


def test_telemetry_disabled_and_failed_init_are_safe():
    sdk = FakeSDK()
    telemetry = Telemetry("", sdk=sdk)
    telemetry.start()
    with telemetry.span("agent.run", "WORKFLOW") as span:
        assert span.trace_id is None
    telemetry.close()
    assert not sdk.initializations and not sdk.spans and not sdk.stops
    broken = Telemetry("key", sdk=FakeSDK(fail=True))
    broken.start()
    with broken.span("agent.run", "WORKFLOW"):
        pass
    assert broken.status == "unavailable"


def test_nested_safe_metadata_redacts_exact_keys_and_lifecycle_once():
    sdk = FakeSDK()
    telemetry = Telemetry("opaque-secret", secrets=["tiny-key"], sdk=sdk)
    telemetry.start()
    telemetry.start()
    with telemetry.span("agent.run", "WORKFLOW", mode="replay") as root:
        assert root.trace_id == "0000000000000000000000000000002a"
        with telemetry.span("tools.propose", "TOOL") as child:
            child.set(outcome="tiny-key", source_code="PRIVATE", cases="PRIVATE", passed=5)
    telemetry.close()
    telemetry.close()
    assert len(sdk.initializations) == 1 and sdk.stops == 1
    assert sdk.spans[1]["parent"] == "agent.run"
    assert "PRIVATE" not in repr(sdk.spans)
    assert sdk.spans[1]["attrs"]["patchpilot.outcome"] == "[REDACTED]"
    assert sdk.initializations[0]["instrumentations"] == []
    masked = telemetry.mask(
        {
            "input.value": "private",
            "exception.message": "private",
            "attributes": {"output.value": "private", "safe": "opaque-secret"},
        }
    )
    assert masked == {"attributes": {"safe": "[REDACTED]"}}


def test_canonical_metadata_preserves_counts_and_typed_llm_usage():
    sdk = FakeSDK()
    telemetry = Telemetry("opaque-secret", sdk=sdk)
    telemetry.start()
    with telemetry.span("model.propose", "LLM", model="test-model", provider="test-provider") as span:
        span.set(
            outcome="opaque-secret",
            passed=5,
            total=5,
            prompt_tokens=11,
            completion_tokens=7,
            tokens=18,
            source_code="PRIVATE",
        )
        span.set(audit_passed=20, audit_total=20)
    attrs = sdk.spans[0]["attrs"]
    metadata = json.loads(attrs["neatlogs.metadata"])
    assert metadata["passed"] == 5 and metadata["audit_total"] == 20
    assert metadata["model"] == "test-model" and metadata["outcome"] == "[REDACTED]"
    assert "PRIVATE" not in repr(attrs)
    assert attrs["neatlogs.llm.model_name"] == "test-model"
    assert attrs["neatlogs.llm.provider"] == "test-provider"
    assert attrs["neatlogs.llm.token_count.prompt"] == 11
    assert attrs["neatlogs.llm.token_count.completion"] == 7
    assert attrs["neatlogs.llm.token_count.total"] == 18
    masked = telemetry.mask(
        {
            "neatlogs.metadata": json.dumps(
                {
                    "outcome": "opaque-secret",
                    "cases": "PRIVATE",
                    "nested": {"source_code": "PRIVATE", "safe": "opaque-secret"},
                }
            )
        }
    )
    assert json.loads(masked["neatlogs.metadata"]) == {
        "outcome": "[REDACTED]",
        "nested": {"safe": "[REDACTED]"},
    }
    metrics = json.loads(attrs["output.value"])
    assert metrics == {"patchpilot_metrics": metadata}
    assert attrs["output.mime_type"] == "application/json"
    assert json.loads(telemetry.mask({"output.value": attrs["output.value"]})["output.value"]) == metrics


@pytest.mark.parametrize(
    "output",
    [
        "PRIVATE CODE",
        json.dumps({"result": "PRIVATE"}),
        json.dumps({"patchpilot_metrics": {"passed": 5}, "source_code": "PRIVATE"}),
        json.dumps({"patchpilot_metrics": {"cases": "PRIVATE"}}),
        json.dumps({"patchpilot_metrics": {"source_code": "PRIVATE"}}),
        json.dumps({"patchpilot_metrics": {"attempts": "PRIVATE"}}),
        json.dumps({"patchpilot_metrics": {"total": [1, 2]}}),
        json.dumps({"patchpilot_metrics": []}),
        json.dumps({"patchpilot_metrics": {"total": float("nan")}}),
    ],
)
def test_metrics_output_envelope_rejects_private_or_unrecognized_payloads(output):
    assert "output.value" not in Telemetry().mask({"output.value": output})


def test_metrics_output_redacts_exact_secrets_after_json_decoding():
    secret = 'opaque"secret\nkey'
    telemetry = Telemetry(secret)
    output = json.dumps({"patchpilot_metrics": {"outcome": secret, "passed": 5}})
    masked = json.loads(telemetry.mask({"output.value": output})["output.value"])
    assert masked == {"patchpilot_metrics": {"outcome": "[REDACTED]", "passed": 5}}


def test_canonical_metadata_failure_does_not_escape_and_invalid_tokens_are_omitted():
    from patchpilot.observability import SafeSpan

    class BrokenMetadata:
        def get_span_context(self):
            return type("Context", (), {"trace_id": 42})()

        def set_attribute(self, key, value):
            if key == "neatlogs.metadata":
                raise RuntimeError("metadata export failed")

    telemetry = Telemetry()
    span = SafeSpan(telemetry, BrokenMetadata())
    span.set(passed=5)
    assert telemetry.status == "unavailable"
    sdk = FakeSDK()
    telemetry = Telemetry("key", sdk=sdk)
    telemetry.start()
    with telemetry.span("llm", "LLM") as span:
        span.set(prompt_tokens=True, completion_tokens="7", tokens=-1)
    assert not any(k.startswith("neatlogs.llm.token_count") for k in sdk.spans[0]["attrs"])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw_usage,expected",
    [
        (
            {"total_tokens": 18, "prompt_tokens": 11, "completion_tokens": 7},
            {"tokens": 18, "prompt_tokens": 11, "completion_tokens": 7},
        ),
        ({"total_tokens": -1, "prompt_tokens": True, "completion_tokens": "7"}, {}),
        (None, {}),
    ],
)
async def test_provider_keeps_only_reported_integer_token_counters(raw_usage, expected):
    import httpx

    from patchpilot.config import Settings
    from patchpilot.providers import Tools

    def respond(request):
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {"code": REPAIR_CODE, "diagnosis": "repair", "citations": []}
                            )
                        }
                    }
                ],
                "usage": raw_usage,
            },
        )

    tools = Tools(
        Settings(groq_api_key="fake-key", llm_provider="groq", _env_file=None), httpx.MockTransport(respond)
    )
    result = await tools.propose(examples()[0] | {"mode": "live"}, [], [], lambda *args: None)
    assert result["usage"] == expected


def test_proof_deterministic_tamper_and_independent_audit():
    request = examples()[0]
    original = copy.deepcopy(request)
    sources = [
        {
            "id": "s1",
            "url": "https://docs.stripe.com/changelog/basil/2025-03-31/add-support-for-multiple-partial-payments-on-invoices",
            "text": "Invoice Payment payments payment_intent",
            "sha256": "claimed",
        }
    ]
    results = verify(REPAIR_CODE, request["entrypoint"], request["cases"])
    proof = build_proof(request, sources, REPAIR_CODE, results)
    assert proof == build_proof(request, sources, REPAIR_CODE, results)
    assert proof["audit"]["applicable"] and proof["audit"]["passed"] == proof["audit"]["total"]
    assert (
        proof["contract_hash"]
        != build_proof(request | {"target_version": "other"}, sources, REPAIR_CODE, results)["contract_hash"]
    )
    changed = copy.deepcopy(sources)
    changed[0]["text"] += "tampered"
    assert proof["evidence_hashes"] != build_proof(request, changed, REPAIR_CODE, results)["evidence_hashes"]
    assert request == original


def test_audit_does_not_invent_policy_for_arbitrary_adapter():
    request = examples()[0] | {
        "entrypoint": "custom",
        "cases": [{"name": "custom", "input": {}, "expected": []}],
    }
    assert not audit_cases(request, [])


def test_live_markdown_official_source_keeps_audit_applicable():
    from patchpilot.examples import RECORDED_TEXT, STRIPE_URL

    request = examples()[0]
    source = {"id": "s1", "url": STRIPE_URL + ".md", "text": RECORDED_TEXT}
    assert len(audit_cases(request, [source])) == 20
    assert not audit_cases(request, [source | {"url": STRIPE_URL + ".md.evil"}])
    assert not audit_cases(
        request, [source | {"url": STRIPE_URL.replace("docs.stripe.com", "docs.stripe.com.evil")}]
    )
    different_contract = request | {
        "cases": [
            {
                "name": "retain numeric pointers",
                "input": {
                    "id": "in_custom",
                    "payments": {"data": [{"payment": {"type": "payment_intent", "payment_intent": 7}}]},
                },
                "expected": {"invoice_id": "in_custom", "payment_intent_ids": [7]},
            }
        ]
    }
    assert not audit_cases(different_contract, [source])


def test_old_run_report_without_proof_or_telemetry_remains_readable(tmp_path):
    from patchpilot.reports import markdown_report
    from patchpilot.store import Store

    run = Store(tmp_path / "legacy.db").create(examples()[0])
    del run["proof"]
    del run["telemetry"]
    report = markdown_report(run)
    assert "No repair proof recorded" in report
    assert "Trace ID: not recorded" in report


@pytest.mark.asyncio
async def test_agent_trace_tree_is_real_and_contains_no_private_inputs(tmp_path):
    from patchpilot.agent import Agent
    from patchpilot.config import Settings
    from patchpilot.providers import Tools
    from patchpilot.store import Store

    sdk = FakeSDK()
    telemetry = Telemetry("test-key", sdk=sdk)
    telemetry.start()
    store = Store(tmp_path / "trace.db")
    request = examples()[0] | {
        "mode": "replay",
        "title": "PRIVATE TITLE",
        "symptom": examples()[0]["symptom"] + " PRIVATE SYMPTOM",
    }
    run = store.create(request)
    await Agent(store, Tools(Settings(_env_file=None)), telemetry).run(run["id"])
    final = store.get(run["id"])
    assert final["status"] == "verified"
    assert final["telemetry"]["trace_id"] == "0000000000000000000000000000002a"
    assert sdk.spans[0]["kind"] == "WORKFLOW"
    children = {r["name"]: r for r in sdk.spans[1:]}
    for name in [
        "verification.baseline",
        "tools.research",
        "tools.propose",
        "verification.acceptance",
        "verification.audit",
    ]:
        assert children[name]["parent"] == "agent.run"
    assert children["verification.audit"]["attrs"]["patchpilot.audit_total"] == 20
    assert "PRIVATE" not in repr(sdk.spans)
    assert "model.propose" not in children


@pytest.mark.asyncio
async def test_span_export_failure_does_not_fail_repair(tmp_path):
    from patchpilot.agent import Agent
    from patchpilot.config import Settings
    from patchpilot.providers import Tools
    from patchpilot.store import Store

    class BrokenSDK(FakeSDK):
        def trace(self, *args, **kwargs):
            raise RuntimeError("private contents must not escape")

    telemetry = Telemetry("key", sdk=BrokenSDK())
    telemetry.start()
    store = Store(tmp_path / "broken.db")
    run = store.create(examples()[0] | {"mode": "replay"})
    await Agent(store, Tools(Settings(_env_file=None)), telemetry).run(run["id"])
    assert store.get(run["id"])["status"] == "verified"
    assert store.get(run["id"])["telemetry"] == {"status": "unavailable", "trace_id": None}


@pytest.mark.asyncio
async def test_live_proposal_is_nested_llm_without_capturing_model_payload(tmp_path):
    from patchpilot.agent import Agent
    from patchpilot.config import Settings
    from patchpilot.providers import Tools
    from patchpilot.store import Store

    class LiveFixtureTools(Tools):
        async def research(self, request, emit):
            return await super().research(request | {"mode": "replay"}, emit)

        async def propose(self, request, sources, feedback, emit):
            return await super().propose(request | {"mode": "replay"}, sources, feedback, emit)

    sdk = FakeSDK()
    telemetry = Telemetry("key", sdk=sdk)
    telemetry.start()
    store = Store(tmp_path / "live.db")
    run = store.create(examples()[0])
    await Agent(store, LiveFixtureTools(Settings(_env_file=None)), telemetry).run(run["id"])
    llm = next(r for r in sdk.spans if r["kind"] == "LLM")
    assert llm["parent"] == "tools.propose"
    assert store.get(run["id"])["status"] == "verified"
    assert "normalize_invoice" not in repr(sdk.spans)


def test_app_lifecycle_and_config_require_saved_verification(tmp_path, monkeypatch):
    import json

    from fastapi.testclient import TestClient

    import patchpilot.main as main
    from patchpilot.config import Settings
    from patchpilot.main import create_app

    monkeypatch.setattr(main, "ROOT", tmp_path)
    (tmp_path / "docs").mkdir()
    sdk = FakeSDK()
    app = create_app(
        Settings(database_path=str(tmp_path / "api.db"), neatlogs_api_key="configured-key", _env_file=None)
    )
    app.state.telemetry.sdk = sdk
    with TestClient(app, base_url="http://127.0.0.1") as client:
        assert client.get("/api/config").json()["partners"]["neatlogs"] == "pending"
        (tmp_path / "docs" / "integration-evidence.json").write_text(
            json.dumps({"neatlogs": {"status": "verified"}, "entire": {"status": "configured"}})
        )
        data = client.get("/api/config").json()
        assert data["partners"]["neatlogs"] == "verified"
        assert data["partners"]["entire"] == "pending"
        assert "configured-key" not in repr(data)
    assert len(sdk.initializations) == 1 and sdk.stops == 1


@pytest.mark.asyncio
async def test_happy_path_patch_fails_audit_and_receives_feedback(tmp_path):
    from patchpilot.agent import Agent
    from patchpilot.config import Settings
    from patchpilot.providers import Tools
    from patchpilot.store import Store

    class WeakTools(Tools):
        async def propose(self, request, evidence, feedback, emit):
            result = await super().propose(request, evidence, feedback, emit)
            if not feedback:
                result["code"] = """def normalize_invoice(invoice):
    ids = []
    for item in invoice.get("payments", {}).get("data", []):
        payment = item.get("payment", {})
        if payment.get("type") == "payment_intent" and payment.get("payment_intent"):
            ids.append(payment["payment_intent"])
    return {"invoice_id": invoice["id"], "payment_intent_ids": ids}
"""
            else:
                assert any(not r["passed"] for r in feedback[-1]["audit"]["results"])
            return result

    store = Store(tmp_path / "runs.db")
    run = store.create(examples()[0] | {"mode": "replay"})
    await Agent(store, WeakTools(Settings(_env_file=None))).run(run["id"])
    final = store.get(run["id"])
    assert final["status"] == "verified"
    assert len(final["attempts"]) == 2
    assert all(r["passed"] for r in final["attempts"][0]["results"])
    assert final["attempts"][0]["audit"]["passed"] < final["attempts"][0]["audit"]["total"]
    assert final["proof"]["audit"]["passed"] == final["proof"]["audit"]["total"]
