import copy

STRIPE_URL = (
    "https://docs.stripe.com/changelog/basil/2025-03-31/add-support-for-multiple-partial-payments-on-invoices"
)
BASE_CODE = """def normalize_invoice(invoice):
    return {
        "invoice_id": invoice["id"],
        "payment_intent_ids": [invoice["payment_intent"]]
    }
"""
REPAIR_CODE = """def normalize_invoice(invoice):
    ids = []
    for item in invoice.get("payments", {}).get("data", []):
        payment = item.get("payment", {})
        if payment.get("type") == "payment_intent" and payment.get("payment_intent"):
            ids.append(payment["payment_intent"])
    return {"invoice_id": invoice["id"], "payment_intent_ids": ids}
"""
PARTIAL_CODE = """def normalize_invoice(invoice):
    payments = invoice.get("payments", {}).get("data", [])
    ids = []
    if payments:
        ids.append(payments[0]["payment"]["payment_intent"])
    return {"invoice_id": invoice["id"], "payment_intent_ids": ids}
"""
RECORDED_TEXT = """Historical official migration excerpt, recorded from Stripe's 2025-03-31.basil release note.
Removed the payment_intent, charge, paid, and paid_out_of_band fields from the Invoice object.
We introduced the Invoice Payment object to represent the connection between payments and invoices and removed previous invoice and payment pointers on relevant objects.
Make sure that you update your integration to no longer assume that a single invoice must be paid by a single payment, and use the new Invoice Payment object to understand the connection between payments and invoices.
The invoice.payments array provides a list of all the payments associated with the invoice and their respective allocation and payment status.
Expand payments.data.payment.payment_intent when retrieving the invoice.
"""


def payment(identifier, kind="payment_intent"):
    return {"payment": {"type": kind, "payment_intent": identifier}}


def cases():
    records = [
        ("Single payment", [payment("pi_001")], ["pi_001"]),
        ("Multiple payments", [payment("pi_001"), payment("pi_002")], ["pi_001", "pi_002"]),
        ("No payments yet", [], []),
        ("Other payment type", [payment("pi_ignored", "payment_record")], []),
        ("Missing payment pointer", [payment(None)], []),
    ]
    return [
        {
            "name": name,
            "input": {"id": "in_demo", "payments": {"data": data}},
            "expected": {"invoice_id": "in_demo", "payment_intent_ids": expected},
        }
        for name, data, expected in records
    ]


def examples():
    base = {
        "title": "Stripe invoice migration",
        "vendor": "stripe",
        "target_version": "2025-03-31.basil",
        "mode": "live",
        "source_code": BASE_CODE,
        "entrypoint": "normalize_invoice",
        "cases": cases(),
        "symptom": "KeyError: payment_intent after upgrading the invoice adapter to 2025-03-31.basil",
        "search_hint": "invoice payment_intent multiple payments migration",
        "max_attempts": 3,
        "replay_scenario": "repair",
    }
    result = [base]
    for title, scenario in [
        ("Recovery from an incomplete repair", "recovery"),
        ("No authoritative evidence", "no_evidence"),
        ("Authentication failure requires investigation", "auth"),
    ]:
        value = copy.deepcopy(base)
        value.update(title=title, mode="replay", replay_scenario=scenario)
        if scenario == "auth":
            value["symptom"] = "HTTP 401 Unauthorized: invalid API credentials"
        result.append(value)
    return result
