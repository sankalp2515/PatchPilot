import pytest

from patchpilot.sandbox import validate_code, verify
from patchpilot.schemas import IncidentRequest
from patchpilot.store import Store


def incident(**changes):
    value = dict(
        title="Invoice upgrade",
        vendor="stripe",
        target_version="2025-03-31.basil",
        mode="replay",
        source_code="def normalize_invoice(invoice):\n    return invoice['payment_intent']",
        entrypoint="normalize_invoice",
        cases=[{"name": "single", "input": {"payments": []}, "expected": []}],
    )
    return IncidentRequest(**(value | changes))


def test_verification_returns_actual_failures_without_mutating_inputs():
    cases = [{"name": "multiple", "input": {"payments": [{"id": "a"}, {"id": "b"}]}, "expected": ["a", "b"]}]
    original = repr(cases)
    wrong = "def normalize_invoice(invoice):\n    return [invoice['payments'][0]['id']]"
    assert verify(wrong, "normalize_invoice", cases)[0]["passed"] is False
    right = "def normalize_invoice(invoice):\n    return [p['id'] for p in invoice.get('payments', [])]"
    result = verify(right, "normalize_invoice", cases)
    assert result[0]["passed"] is True
    assert result[0]["actual"] == ["a", "b"]
    assert repr(cases) == original


@pytest.mark.parametrize(
    "code",
    [
        "import os\ndef normalize_invoice(x):\n    return os.environ",
        "def normalize_invoice(x):\n    return x.__class__",
        "def normalize_invoice(x):\n    return open('secret')",
        "def normalize_invoice(x):\n    return normalize_invoice(x)",
        "def normalize_invoice(x):\n    while True:\n        pass",
    ],
)
def test_unsafe_code_is_rejected(code):
    with pytest.raises(ValueError):
        validate_code(code, "normalize_invoice")


def test_oversized_computation_is_rejected():
    result = verify(
        "def normalize_invoice(x):\n    return 'a' * 1000000000",
        "normalize_invoice",
        [{"name": "size", "input": {}, "expected": "x"}],
    )
    assert not result[0]["passed"]
    assert "limit" in result[0]["error"].lower()


def test_schema_rejects_credentials():
    with pytest.raises(ValueError):
        incident(cases=[{"name": "secret", "input": {"api_key": "private-key"}, "expected": {}}])


def test_store_survives_reopening_and_preserves_cancel(tmp_path):
    store = Store(tmp_path / "runs.db")
    run = store.create(incident().model_dump())
    store.update(run["id"], {"status": "cancelled"})
    store.update(run["id"], {"status": "verified"})
    reopened = Store(tmp_path / "runs.db")
    assert reopened.get(run["id"])["status"] == "cancelled"
    assert len(reopened.list()) == 1


def test_multiple_and_empty_cases_are_independent():
    code = "def normalize_invoice(x):\n    out = []\n    for p in x.get('payments', []):\n        out.append(p['id'])\n    return out"
    cases = [
        {"name": "empty", "input": {}, "expected": []},
        {"name": "one", "input": {"payments": [{"id": "a"}]}, "expected": ["a"]},
    ]
    assert all(r["passed"] for r in verify(code, "normalize_invoice", cases))


def test_list_growth_is_bounded_even_when_not_returned():
    code = "def normalize_invoice(x):\n    values = [1]\n    for n in [0] * 17:\n        values.extend(values)\n    return []"
    result = verify(code, "normalize_invoice", [{"name": "growth", "input": {}, "expected": []}])
    assert not result[0]["passed"]
    assert "limit" in result[0]["error"].lower()


def test_nested_expansion_is_bounded_before_serializing():
    code = "def normalize_invoice(x):\n    values = [1]\n    for n in [0] * 6:\n        values = [values] * 10\n    return values"
    result = verify(code, "normalize_invoice", [{"name": "nested", "input": {}, "expected": []}])
    assert not result[0]["passed"]
    assert "limit" in result[0]["error"].lower()


def test_boolean_does_not_satisfy_numeric_expected_output():
    result = verify(
        "def normalize_invoice(x):\n    return True",
        "normalize_invoice",
        [{"name": "typed", "input": {}, "expected": 1}],
    )
    assert not result[0]["passed"]


def test_cyclic_fanout_is_rejected_before_queue_expansion():
    from patchpilot.sandbox import Interpreter

    value = []
    value.append(value)
    value.extend([value] * 99)
    with pytest.raises(ValueError, match="limit"):
        Interpreter().json_budget(value)
