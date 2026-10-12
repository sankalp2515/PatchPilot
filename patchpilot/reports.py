def markdown_report(run):
    lines = [
        f"# PatchPilot investigation — {run['input']['title']}",
        "",
        f"Status: **{run['status']}**",
        f"Mode: {run['input']['mode']}",
        f"Target: {run['input']['vendor']} / {run['input']['target_version']}",
        "",
        run["diagnosis"],
        "",
        "## Sources",
    ]
    for source in run["sources"]:
        lines.extend(
            [
                f"- [{source['title']}]({source['url']}) — {source['provenance']}",
                f"  Content SHA256: `{source['sha256']}`",
            ]
        )
    lines += ["", "## Supporting quotations"]
    for citation in run["citations"]:
        lines += [f"- {citation['source_id']}: {citation['quote']}"]
    lines += ["", "## Proposed diff", "```diff", run["diff"], "```", "", "## Protected case results"]
    for result in run["verification"]:
        lines.append(
            f"- {'PASS' if result['passed'] else 'FAIL'}: {result['name']} {result.get('error', '')}"
        )
    proof = run.get("proof")
    if proof:
        lines += [
            "",
            "## Repair proof",
            proof["verified_scope"],
            f"Contract SHA256: `{proof['contract_hash']}`",
            f"Cases SHA256: `{proof['case_hash']}`",
            f"Patch SHA256: `{proof['patch_hash']}`",
            f"Proof SHA256: `{proof['proof_hash']}`",
            f"Acceptance: {proof['acceptance_passed']}/{proof['total']}",
            "",
            "### Independent counterexample audit",
            proof["audit"]["policy"],
            f"Applicable: {proof['audit']['applicable']}; passed {proof['audit']['passed']}/{proof['audit']['total']}",
        ]
        for result in proof["audit"]["results"]:
            lines.append(
                f"- {'PASS' if result['passed'] else 'FAIL'}: {result['name']} {result.get('error', '')}"
            )
        for evidence in proof["evidence_hashes"]:
            lines.append(f"- Evidence {evidence['source_id']}: `{evidence['sha256']}`")
    else:
        lines += ["", "## Repair proof", "No repair proof recorded for this run."]
    lines += ["", "## Limitations"] + [f"- {item}" for item in run["limitations"]]
    lines += ["", "## Recorded metrics"] + [f"- {key}: {value}" for key, value in run["metrics"].items()]
    lines += [
        "",
        "## Partner status",
        "Sponsor verification is recorded separately in the repository integration evidence manifest.",
        "",
        "## Run telemetry",
        f"Status: {run.get('telemetry', {}).get('status', 'not recorded')}",
        f"Trace ID: {run.get('telemetry', {}).get('trace_id') or 'not recorded'}",
    ]
    return "\n".join(lines)
