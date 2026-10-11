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
    lines += ["", "## Limitations"] + [f"- {item}" for item in run["limitations"]]
    lines += ["", "## Recorded metrics"] + [f"- {key}: {value}" for key, value in run["metrics"].items()]
    lines += [
        "",
        "## Partner status",
        "neatlogs, Entire and cfo.ai account-backed integration is pending morning setup.",
    ]
    return "\n".join(lines)
