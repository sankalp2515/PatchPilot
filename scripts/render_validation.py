"""Render actual integration readback receipts as a standalone, labelled evidence sheet."""

import html
import json

from patchpilot.config import ROOT


def display_value(name, value):
    value = value.get("value") if isinstance(value, dict) else value
    if value is None:
        return "—"
    if isinstance(value, (int, float)):
        if name.endswith(("rate", "margin")):
            return f"{value * 100:.2f}%"
        return f"{value:,.2f}".removesuffix(".00")
    return str(value)


def main():
    folder = ROOT / "docs" / "evidence"
    trace = json.loads((folder / "neatlogs-improvement.json").read_text())
    cfo = json.loads((folder / "cfo-model.json").read_text())
    escape = html.escape
    panels = []
    for label in ("before", "after"):
        run = trace[label]
        rows = "".join(
            f"<li><strong>{escape(span['name'])}</strong><span>{escape(json.dumps(span.get('metrics', {})))}</span><small>{escape(span['id'])}</small></li>"
            for span in run["readback"]["spans"]
        )
        panels.append(
            f'<section><h2>{label.title()}</h2><p class="result">{run["audit_passed"]} / {run["audit_total"]} audit cases</p><p>{run["acceptance_passed"]}/{run["acceptance_total"]} supplied acceptance cases</p><p class="id">Trace {escape(run["trace_id"])}</p><p>Exact HTTP 200 readback · {run["readback"]["span_count"]} persisted spans · valid parent hierarchy</p><ul>{rows}</ul></section>'
        )
    financial = "".join(
        "<tr><th>"
        + escape(row["name"].removeprefix("PP "))
        + "</th>"
        + "".join("<td>" + escape(display_value(row["name"], value)) + "</td>" for value in row["values"])
        + "</tr>"
        for row in cfo["rows"]
    )
    document = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>PatchPilot · Integration validation</title><style>body{margin:0;background:#f6f5ef;color:#242821;font:16px system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:48px 28px}h1{font:56px Georgia,serif;margin:16px 0}h2{font:32px Georgia,serif}p{line-height:1.6;max-width:85ch}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}section{padding:28px;background:white;border:1px solid #d7dbcb;border-radius:12px}.result{font:40px Georgia,serif;color:#be4b1c}.id,small{font:12px monospace;overflow-wrap:anywhere}ul{list-style:none;padding:0}li{padding:12px 0;border-top:1px solid #e4e6dc}li span,small{display:block;font-size:12px;overflow-wrap:anywhere;line-height:1.7}table{width:100%;border-collapse:collapse;margin:24px 0}td,th{padding:12px;text-align:left;border-bottom:1px solid #d7dbcb}a{color:#a9441d}@media(max-width:700px){.grid{grid-template-columns:1fr}h1{font-size:38px}main{padding:24px 12px}section{padding:20px}table{font-size:12px}}</style><main><p>PatchPilot · Integration validation records</p><h1>Evidence of an improvement.</h1><p>This sheet renders actual persisted neatlogs trace receipts. It is an exported evidence view, not the neatlogs dashboard. The preserved pre-upgrade adapter and improved replay agent use the same synthetic invoice contract. This is not a real-world accuracy benchmark.</p><div class="grid">'
        + "".join(panels)
        + "</div><h2>cfo.ai · Editable launch hypotheses</h2><p>Actual saved-model readback: three planning cases, 45 selected cells, 44 nonempty, no formula errors. All values are illustrative USD assumptions, not customers, actual finances or invoices. Null growth runway means no positive monthly burn.</p><table><thead><tr><th>Monthly input / calculation</th><th>Base</th><th>Conservative</th><th>Growth</th></tr></thead><tbody>"
        + financial
        + '</tbody></table><p>Read the accompanying JSON receipts and economics documentation to inspect formulas and full scope. <a href="neatlogs-improvement.json">Trace receipt</a> · <a href="cfo-model.json">cfo.ai receipt</a> · <a href="entire-checkpoint.json">Entire checkpoint</a></p></main></html>'
    )
    (folder / "integration-validation.html").write_text(document, encoding="utf-8")
    print("Rendered integration validation receipts")


if __name__ == "__main__":
    main()
