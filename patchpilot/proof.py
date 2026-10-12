"""Deterministic artifact binding and an explicitly scoped local fixture audit."""

import difflib
import hashlib
import json

from .examples import STRIPE_URL
from .sandbox import verify


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    ).hexdigest()


def pointer_ids(invoice):
    """Local normalization policy; malformed values are ignored, expanded IDs read."""
    ids = []
    payments = invoice.get("payments")
    if not isinstance(payments, dict) or not isinstance(payments.get("data"), list):
        return ids
    for item in payments["data"]:
        payment = item.get("payment") if isinstance(item, dict) else None
        if not isinstance(payment, dict) or payment.get("type") != "payment_intent":
            continue
        pointer = payment.get("payment_intent")
        if isinstance(pointer, dict):
            pointer = pointer.get("id")
        if isinstance(pointer, str) and pointer:
            ids.append(pointer)
    return ids


def audit_cases(request, sources):
    # Vendor/version and literal fetched migration evidence alone do not establish
    # the caller's output policy: every acceptance case must agree with this one.
    evidence = any(
        s.get("url", "").removesuffix(".md") == STRIPE_URL and "Invoice Payment" in s.get("text", "")
        for s in sources
    )
    if not (
        evidence
        and request.get("vendor", "").lower() == "stripe"
        and request.get("target_version") == "2025-03-31.basil"
        and request.get("entrypoint") == "normalize_invoice"
    ):
        return []
    for case in request.get("cases", []):
        invoice = case.get("input")
        if (
            not isinstance(invoice, dict)
            or "id" not in invoice
            or case.get("expected")
            != {"invoice_id": invoice["id"], "payment_intent_ids": pointer_ids(invoice)}
        ):
            return []
    if not request.get("cases"):
        return []
    shapes = [
        ("Null payment", {"payment": None}),
        ("List payment", {"payment": []}),
        ("String payment", {"payment": "pi_wrong"}),
        ("Missing payment", {}),
        ("Missing pointer", {"payment": {"type": "payment_intent"}}),
        ("Null pointer", {"payment": {"type": "payment_intent", "payment_intent": None}}),
        ("List pointer", {"payment": {"type": "payment_intent", "payment_intent": ["pi_wrong"]}}),
        ("Numeric pointer", {"payment": {"type": "payment_intent", "payment_intent": 7}}),
        ("Boolean pointer", {"payment": {"type": "payment_intent", "payment_intent": True}}),
        ("Empty pointer", {"payment": {"type": "payment_intent", "payment_intent": ""}}),
        ("Malformed expanded pointer", {"payment": {"type": "payment_intent", "payment_intent": {"id": 7}}}),
        (
            "Expanded pointer",
            {"payment": {"type": "payment_intent", "payment_intent": {"id": "pi_expanded"}}},
        ),
        ("Other kind", {"payment": {"type": "payment_record", "payment_intent": "pi_wrong"}}),
        ("Non-object item", None),
    ]
    cases = []
    for name, item in shapes:
        invoice = {
            "id": "in_audit",
            "payments": {
                "data": [item, {"payment": {"type": "payment_intent", "payment_intent": "pi_valid"}}]
            },
        }
        cases.append(
            {
                "name": name,
                "input": invoice,
                "expected": {"invoice_id": "in_audit", "payment_intent_ids": pointer_ids(invoice)},
            }
        )
    for value in (None, [], "invalid", {"data": None}, {"data": {}}, {"data": "invalid"}):
        invoice = {"id": "in_audit", "payments": value}
        cases.append(
            {
                "name": f"Malformed payments container {len(cases)}",
                "input": invoice,
                "expected": {"invoice_id": "in_audit", "payment_intent_ids": []},
            }
        )
    return cases


def build_proof(request, sources, code, results, baseline=(), citations=()):
    cases = audit_cases(request, sources)
    audit_results = verify(code, request["entrypoint"], cases) if cases else []
    audit = {
        "applicable": bool(cases),
        "passed": sum(r["passed"] for r in audit_results),
        "total": len(audit_results),
        "results": audit_results,
        "policy": "Local Stripe invoice fixture normalization: retain nonempty string IDs (including expanded object IDs); ignore malformed values. Not a vendor guarantee."
        if cases
        else "No independent audit policy matched this input contract.",
    }
    contract = {
        k: request.get(k)
        for k in ("vendor", "target_version", "entrypoint", "source_code", "cases", "symptom")
    }
    diff = "".join(
        difflib.unified_diff(
            request["source_code"].splitlines(True),
            code.splitlines(True),
            fromfile="adapter.before.py",
            tofile="adapter.proposed.py",
        )
    )
    proof = {
        "version": 1,
        "contract_hash": digest(contract),
        "case_hash": digest(request["cases"]),
        "evidence_hashes": [
            {
                "source_id": s.get("id"),
                "sha256": hashlib.sha256(s.get("text", "").encode()).hexdigest(),
                "binding_hash": digest(s),
            }
            for s in sources
        ],
        "patch_hash": hashlib.sha256(code.encode()).hexdigest(),
        "diff_hash": hashlib.sha256(diff.encode()).hexdigest(),
        "baseline_hash": digest(baseline),
        "citations_hash": digest(citations),
        "acceptance_hash": digest(results),
        "acceptance_passed": sum(r["passed"] for r in results),
        "total": len(results),
        "audit": audit,
        "verified_scope": "Supplied acceptance cases in the restricted JSON adapter interpreter"
        + (
            " plus the local Stripe invoice counterexample fixture policy."
            if cases
            else ". No independent counterexample policy applies."
        ),
    }
    proof["proof_hash"] = digest(proof)
    return proof


def proof_passes(proof):
    return proof["acceptance_passed"] == proof["total"] and (
        not proof["audit"]["applicable"] or proof["audit"]["passed"] == proof["audit"]["total"]
    )
