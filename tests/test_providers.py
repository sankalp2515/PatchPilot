import httpx
import pytest

from patchpilot.config import Settings
from patchpilot.providers import Tools, allowed_url, validate_proposal
from patchpilot.examples import examples


@pytest.mark.parametrize("url", ["https://docs.stripe.com.evil.test/a", "http://docs.stripe.com/a",
                                "https://127.0.0.1/a", "https://user:pass@docs.stripe.com/a",
                                "https://docs.stripe.com:444/a"])
def test_rejects_untrusted_source_addresses(url):
    assert not allowed_url(url, "stripe")


def test_accepts_exact_official_domain():
    assert allowed_url("https://docs.stripe.com/changelog/basil", "stripe")


def test_quote_must_exist_in_fetched_source():
    sources = [{"id": "s1", "text": "The payment_intent field was removed."}]
    with pytest.raises(ValueError):
        validate_proposal({"code": "def normalize_invoice(x):\n    return []", "diagnosis": "upgrade",
                           "citations": [{"source_id": "s1", "quote": "Invented replacement"}]}, sources,
                          "normalize_invoice")


@pytest.mark.asyncio
async def test_search_snippets_cannot_be_used_as_fetched_evidence():
    def respond(req):
        if req.url.host == "serpapi.com":
            return httpx.Response(200, json={"organic_results": [{"title": "Change", "link":
                "https://docs.stripe.com/changelog/basil", "snippet": "payment_intent removed"}]})
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
