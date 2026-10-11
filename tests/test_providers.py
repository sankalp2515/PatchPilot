import httpx
import pytest

from patchpilot.config import Settings
from patchpilot.examples import examples
from patchpilot.providers import Tools, allowed_url, validate_proposal


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
