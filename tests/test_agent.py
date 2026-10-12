import pytest

from patchpilot.agent import Agent
from patchpilot.config import Settings
from patchpilot.examples import examples
from patchpilot.providers import Tools
from patchpilot.store import Store


async def run_example(tmp_path, index=0, **changes):
    store = Store(tmp_path / "runs.db")
    request = examples()[index] | {"mode": "replay"} | changes
    run = store.create(request)
    await Agent(store, Tools(Settings(_env_file=None))).run(run["id"])
    return store.get(run["id"])


@pytest.mark.asyncio
async def test_end_to_end_repair_is_scoped_and_has_evidence(tmp_path):
    run = await run_example(tmp_path)
    assert run["status"] == "verified"
    assert all(case["passed"] for case in run["verification"])
    assert not all(case["passed"] for case in run["baseline"])
    assert run["diff"] and run["citations"] and run["limitations"]
    assert run["metrics"]["search_calls"] == 0


@pytest.mark.asyncio
async def test_incomplete_first_patch_recovers_without_changing_cases(tmp_path):
    run = await run_example(tmp_path, 1)
    assert run["status"] == "verified"
    assert len(run["attempts"]) == 2
    assert any(not case["passed"] for case in run["attempts"][0]["results"])
    assert run["input"]["cases"] == examples()[1]["cases"]
    assert any(event["kind"] == "recovery" for event in run["events"])


@pytest.mark.asyncio
@pytest.mark.parametrize("index", [2, 3])
async def test_abstains_when_evidence_missing_or_auth_failure(tmp_path, index):
    run = await run_example(tmp_path, index)
    assert run["status"] == "needs_human"
    assert run["proposed_code"] == ""


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "changes",
    [
        {"vendor": "github"},
        {"target_version": "not-a-real-release"},
        {"entrypoint": "other_adapter"},
        {"cases": [{"name": "changed", "input": {}, "expected": []}]},
    ],
)
async def test_recorded_replay_refuses_edited_contract(tmp_path, changes):
    run = await run_example(tmp_path, **changes)
    assert run["status"] == "needs_human"
    assert not run["sources"] and not run["attempts"] and not run["proposed_code"]
    assert any(
        "recorded" in event["detail"].lower() and "live" in event["detail"].lower() for event in run["events"]
    )


@pytest.mark.asyncio
async def test_recorded_proposal_independently_rejects_edited_contract():
    tools = Tools(Settings(_env_file=None))
    request = examples()[0] | {"mode": "replay", "vendor": "github", "target_version": "not-a-real-release"}
    with pytest.raises(ValueError, match="recorded"):
        await tools.propose(request, [], [], lambda *args: None)


@pytest.mark.asyncio
async def test_recorded_research_independently_rejects_edited_contract():
    tools = Tools(Settings(_env_file=None))
    request = examples()[0] | {"mode": "replay", "vendor": "github"}
    events = []
    assert await tools.research(request, lambda *args: events.append(args)) == []
    assert events[0][0] == "decision" and "live mode" in events[0][2]


@pytest.mark.asyncio
async def test_resume_cannot_verify_unrelated_saved_replay_evidence(tmp_path):
    from patchpilot.examples import REPAIR_CODE
    from patchpilot.sandbox import verify

    store = Store(tmp_path / "unrelated.db")
    tools = Tools(Settings(_env_file=None))
    fixture = examples()[0] | {"mode": "replay"}
    sources = await tools.research(fixture, lambda *args: None)
    proposal = await tools.propose(fixture, sources, [], lambda *args: None)
    request = fixture | {"vendor": "github", "target_version": "not-a-real-release"}
    run = store.create(request)
    store.update(
        run["id"],
        {
            "status": "interrupted",
            "sources": sources,
            "proposed_code": REPAIR_CODE,
            "verification": verify(REPAIR_CODE, request["entrypoint"], request["cases"]),
            "citations": proposal["citations"],
        },
    )
    await Agent(store, tools).run(run["id"])
    final = store.get(run["id"])
    assert final["status"] == "needs_human"
    assert not final["attempts"]
    assert final["input"] == request


@pytest.mark.asyncio
async def test_already_passing_adapter_does_not_call_providers(tmp_path):
    run = await run_example(
        tmp_path,
        source_code="def normalize_invoice(x):\n    return []",
        cases=[{"name": "works", "input": {}, "expected": []}],
    )
    assert run["status"] == "no_change"
    assert not run["sources"] and not run["attempts"]


@pytest.mark.asyncio
async def test_cancelled_run_cannot_be_overwritten(tmp_path):
    store = Store(tmp_path / "runs.db")
    run = store.create(examples()[0] | {"mode": "replay"})
    store.update(run["id"], {"status": "cancelled", "cancel_requested": True})
    await Agent(store, Tools(Settings(_env_file=None))).run(run["id"])
    assert store.get(run["id"])["status"] == "cancelled"


@pytest.mark.asyncio
async def test_exhausted_repair_budget_does_not_claim_success(tmp_path):
    run = await run_example(tmp_path, 1, max_attempts=1)
    assert run["status"] == "unverified"
    assert len(run["attempts"]) == 1


def test_restart_preserves_evidence_and_marks_run_interrupted(tmp_path):
    store = Store(tmp_path / "runs.db")
    run = store.create(examples()[0])
    store.update(run["id"], {"status": "researching", "sources": [{"id": "s1"}]})
    store.interrupt_incomplete()
    assert store.get(run["id"])["status"] == "interrupted"
    assert store.get(run["id"])["sources"] == [{"id": "s1"}]


@pytest.mark.asyncio
async def test_resume_finalizes_saved_passing_last_attempt_without_new_model_call(tmp_path):
    from patchpilot.examples import REPAIR_CODE
    from patchpilot.sandbox import verify

    store = Store(tmp_path / "runs.db")
    tools = Tools(Settings(_env_file=None))
    request = examples()[0] | {"mode": "replay", "max_attempts": 1}
    run = store.create(request)
    sources = await tools.research(request, lambda *args: None)
    proposal = await tools.propose(request, sources, [], lambda *args: None)
    results = verify(REPAIR_CODE, request["entrypoint"], request["cases"])
    store.update(
        run["id"],
        {
            "status": "verifying",
            "sources": sources,
            "proposed_code": REPAIR_CODE,
            "diagnosis": proposal["diagnosis"],
            "citations": proposal["citations"],
            "verification": results,
            "attempts": [{"number": 1, "code": REPAIR_CODE, "results": results, "error": ""}],
        },
    )
    store.interrupt_incomplete()
    await Agent(store, tools).run(run["id"])
    final = store.get(run["id"])
    assert final["status"] == "verified"
    assert len(final["attempts"]) == 1
    assert any("Saved passing" in event["title"] for event in final["events"])
