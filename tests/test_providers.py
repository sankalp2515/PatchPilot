import httpx
import pytest

from patchpilot.config import Settings
from patchpilot.examples import examples
from patchpilot.providers import Tools, allowed_url, validate_proposal


@pytest.mark.asyncio
async def test_model_429_retries_once_using_bounded_retry_after(monkeypatch):
    import json

    requests = []
    sleeps = []

    async def sleep(delay):
        sleeps.append(delay)

    def respond(request):
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(429, headers={"Retry-After": "2.5"}, text="private provider body")
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "code": "def normalize_invoice(x):\n    return []",
                                    "diagnosis": "repair",
                                    "citations": [],
                                }
                            )
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr("patchpilot.providers.asyncio.sleep", sleep)
    tools = Tools(
        Settings(groq_api_key="opaque-secret", llm_provider="groq", _env_file=None),
        httpx.MockTransport(respond),
    )
    events = []
    await tools.propose(examples()[0] | {"mode": "live"}, [], [], lambda *args: events.append(args))
    assert len(requests) == 2 and sleeps == [2.5]
    assert any(event[0] == "recovery" for event in events)
    assert "private provider body" not in repr(events) and "opaque-secret" not in repr(events)
    assert json.loads(requests[0].content)["max_tokens"] == 3500


@pytest.mark.asyncio
@pytest.mark.parametrize("header", [None, "invalid", "0", "-1", "61", "nan", "inf"])
async def test_model_429_without_bounded_retry_after_stops(header, monkeypatch):
    requests = []

    async def sleep(delay):
        pytest.fail("Invalid Retry-After must not sleep")

    def respond(request):
        requests.append(request)
        return httpx.Response(429, headers={"Retry-After": header} if header else {})

    monkeypatch.setattr("patchpilot.providers.asyncio.sleep", sleep)
    tools = Tools(
        Settings(groq_api_key="fake", llm_provider="groq", _env_file=None), httpx.MockTransport(respond)
    )
    with pytest.raises(ValueError, match="HTTP 429"):
        await tools.propose(examples()[0] | {"mode": "live"}, [], [], lambda *args: None)
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_model_429_retry_budget_is_one(monkeypatch):
    requests = []
    sleeps = []

    async def sleep(delay):
        sleeps.append(delay)

    def respond(request):
        requests.append(request)
        return httpx.Response(429, headers={"Retry-After": "1"})

    monkeypatch.setattr("patchpilot.providers.asyncio.sleep", sleep)
    tools = Tools(
        Settings(groq_api_key="fake", llm_provider="groq", _env_file=None), httpx.MockTransport(respond)
    )
    with pytest.raises(ValueError, match="HTTP 429"):
        await tools.propose(examples()[0] | {"mode": "live"}, [], [], lambda *args: None)
    assert len(requests) == 2 and sleeps == [1]


def test_retry_after_supports_bounded_http_date_and_rejects_expired_date():
    from datetime import UTC, datetime, timedelta
    from email.utils import format_datetime

    from patchpilot.providers import retry_after_delay

    now = datetime.now(UTC)
    delay = retry_after_delay(format_datetime(now + timedelta(seconds=30), usegmt=True))
    assert 0 < delay <= 30
    assert retry_after_delay(format_datetime(now - timedelta(seconds=30), usegmt=True)) is None
    assert retry_after_delay(format_datetime(now + timedelta(seconds=90), usegmt=True)) is None


@pytest.mark.asyncio
@pytest.mark.parametrize("conflicting_contract", [False, True])
async def test_initial_model_contract_has_structured_guards_only_when_applicable(conflicting_contract):
    import json

    from patchpilot.examples import RECORDED_TEXT, REPAIR_CODE, STRIPE_URL

    captured = []

    def respond(request):
        captured.append(json.loads(request.content))
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
                ]
            },
        )

    request = examples()[0] | {"mode": "live"}
    if conflicting_contract:
        request["cases"] = [
            {
                "name": "retain numeric pointer",
                "input": {
                    "id": "in_custom",
                    "payments": {"data": [{"payment": {"type": "payment_intent", "payment_intent": 7}}]},
                },
                "expected": {"invoice_id": "in_custom", "payment_intent_ids": [7]},
            }
        ]
    sources = [{"id": "s1", "url": STRIPE_URL + ".md", "text": RECORDED_TEXT}]
    tools = Tools(
        Settings(groq_api_key="fake", llm_provider="groq", _env_file=None), httpx.MockTransport(respond)
    )
    await tools.propose(request, sources, [], lambda *args: None)
    context = json.loads(captured[0]["messages"][1]["content"])
    assert context["incident"] == request
    if conflicting_contract:
        assert "independent_audit_policy" not in context
    else:
        policy = context["independent_audit_policy"]
        assert isinstance(policy, dict)
        assert policy["authority"] == "Local caller fixture normalization policy; not a vendor guarantee."
        assert policy["supported_type_guards"] == [
            "isinstance(value, dict)",
            "isinstance(value, list)",
            "isinstance(value, str)",
        ]
        assert len(policy["guard_rules"]) == 6
        assert policy["ordering"] == "Preserve input order and duplicate accepted IDs."
        assert "boolean" in policy["pointer_rejections"]
        assert REPAIR_CODE not in json.dumps(context)


@pytest.mark.asyncio
async def test_model_feedback_keeps_failed_checks_contract_and_previous_code():
    import copy
    import json

    feedback = [
        {
            "attempt": 1,
            "previous_code": "PREVIOUS CODE",
            "results": [
                {"name": "success acceptance", "passed": True},
                {"name": "failed acceptance", "passed": False, "actual": [], "expected": [1]},
            ],
            "audit": {
                "applicable": True,
                "passed": 1,
                "total": 2,
                "results": [
                    {"name": "success audit", "passed": True},
                    {"name": "failed audit", "passed": False, "error": "shape mismatch"},
                ],
            },
        }
    ]
    original = copy.deepcopy(feedback)
    captured = []

    def respond(request):
        captured.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "code": "def normalize_invoice(x):\n    return []",
                                    "diagnosis": "repair",
                                    "citations": [],
                                }
                            )
                        }
                    }
                ]
            },
        )

    request = examples()[0] | {"mode": "live"}
    tools = Tools(
        Settings(groq_api_key="fake", llm_provider="groq", _env_file=None), httpx.MockTransport(respond)
    )
    await tools.propose(request, [], feedback, lambda *args: None)
    context = json.loads(captured[0]["messages"][1]["content"])
    assert context["incident"] == request
    attempt = context["previous_attempt_feedback"][0]
    assert attempt["previous_code"] == "PREVIOUS CODE"
    assert [r["name"] for r in attempt["results"]] == ["failed acceptance"]
    assert [r["name"] for r in attempt["audit"]["results"]] == ["failed audit"]
    assert feedback == original


@pytest.mark.parametrize(
    "url",
    [
        "https://docs.stripe.com.evil.test/a",
        "http://docs.stripe.com/a",
        "https://127.0.0.1/a",
        "https://user:pass@docs.stripe.com/a",
        "https://docs.stripe.com:444/a",
    ],
)
def test_rejects_untrusted_source_addresses(url):
    assert not allowed_url(url, "stripe")


def test_accepts_exact_official_domain():
    assert allowed_url("https://docs.stripe.com/changelog/basil", "stripe")


def test_quote_must_exist_in_fetched_source():
    sources = [{"id": "s1", "text": "The payment_intent field was removed."}]
    with pytest.raises(ValueError):
        validate_proposal(
            {
                "code": "def normalize_invoice(x):\n    return []",
                "diagnosis": "upgrade",
                "citations": [{"source_id": "s1", "quote": "Invented replacement"}],
            },
            sources,
            "normalize_invoice",
        )


@pytest.mark.asyncio
async def test_search_snippets_cannot_be_used_as_fetched_evidence():
    def respond(req):
        if req.url.host == "serpapi.com":
            return httpx.Response(
                200,
                json={
                    "organic_results": [
                        {
                            "title": "Change",
                            "link": "https://docs.stripe.com/changelog/basil",
                            "snippet": "payment_intent removed",
                        }
                    ]
                },
            )
        return httpx.Response(503)

    tools = Tools(Settings(serpapi_api_key="test", _env_file=None), httpx.MockTransport(respond))
    events = []
    result = await tools.research(examples()[0], lambda *args: events.append(args))
    assert result == []
    assert events


@pytest.mark.asyncio
async def test_provider_failure_does_not_leak_key():
    def respond(req):
        raise httpx.ConnectError("request failed with api_key=test-secret-key", request=req)

    tools = Tools(Settings(serpapi_api_key="test-secret-key", _env_file=None), httpx.MockTransport(respond))
    events = []
    with pytest.raises(ValueError) as error:
        await tools.research(examples()[0], lambda *args: events.append(args))
    assert "test-secret-key" not in str(error.value)
    assert "test-secret-key" not in str(events)


@pytest.mark.asyncio
async def test_follows_official_release_index_when_search_returns_adjacent_page():
    def respond(req):
        if req.url.host == "serpapi.com":
            return httpx.Response(
                200,
                json={
                    "organic_results": [
                        {
                            "title": "Adjacent change",
                            "link": "https://docs.stripe.com/changelog/basil/2025-03-31/adjacent",
                        }
                    ]
                },
            )
        if req.url.path == "/changelog/basil.md":
            return httpx.Response(
                200,
                text="2025-03-31.basil release notes\n[Multiple invoice payments](https://docs.stripe.com/changelog/basil/2025-03-31/invoice-payments)\n"
                * 2,
            )
        if req.url.path.endswith("invoice-payments.md"):
            return httpx.Response(
                200,
                text="2025-03-31.basil: invoice payment_intent removed; multiple payments now use the invoice payments data array.",
            )
        return httpx.Response(
            200,
            text="2025-03-31.basil: unrelated checkout button changes. This does not explain an invoice failure.",
        )

    tools = Tools(Settings(serpapi_api_key="test", _env_file=None), httpx.MockTransport(respond))
    result = await tools.research(examples()[0], lambda *args: None)
    assert any(source["url"].endswith("invoice-payments") for source in result)
    assert all(
        "invoice" in source["text"].lower() and "payment_intent" in source["text"] for source in result
    )


@pytest.mark.asyncio
async def test_empty_search_hint_still_requires_incident_relevance():
    def respond(req):
        if req.url.host == "serpapi.com":
            return httpx.Response(
                200,
                json={
                    "organic_results": [
                        {
                            "title": "Checkout change",
                            "link": "https://docs.stripe.com/changelog/basil/2025-03-31/checkout",
                        }
                    ]
                },
            )
        return httpx.Response(
            200,
            text="2025-03-31.basil: Checkout buttons now use rounded corners. The official release documents a new visual appearance.",
        )

    tools = Tools(Settings(serpapi_api_key="test", _env_file=None), httpx.MockTransport(respond))
    request = examples()[0] | {
        "search_hint": "",
        "symptom": "KeyError: payment_intent in invoice after upgrade",
    }
    assert await tools.research(request, lambda *args: None) == []


def test_literal_but_unrelated_citation_cannot_support_incident():
    request = examples()[0] | {"search_hint": "", "symptom": "invoice payment_intent missing"}
    source = {
        "id": "s1",
        "text": "Checkout buttons now use rounded corners. invoice payment_intent was removed.",
    }
    with pytest.raises(ValueError, match="incident"):
        validate_proposal(
            {
                "code": "def normalize_invoice(x):\n    return []",
                "diagnosis": "Fix",
                "citations": [{"source_id": "s1", "quote": "Checkout buttons now use rounded corners."}],
            },
            [source],
            "normalize_invoice",
            request,
        )
