from pathlib import Path

import pytest
import yaml

from agents.orchestrator import Orchestrator
from tools import progress_store


def _load_evaluation_cases() -> list[dict]:
    spec_path = Path(__file__).resolve().parent.parent / "specs" / "evaluation_cases.yaml"
    with open(spec_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    cases = data.get("evaluation_cases", data)
    if isinstance(cases, dict):
        return list(cases.values())
    return cases


@pytest.fixture
def isolated_progress(monkeypatch, tmp_path):
    progress_file = tmp_path / "progress.json"
    monkeypatch.setattr(progress_store, "PROGRESS_FILE", str(progress_file))
    return progress_file


@pytest.fixture(scope="module")
def evaluation_cases():
    return _load_evaluation_cases()


@pytest.fixture(scope="module")
def orchestrator():
    return Orchestrator()


@pytest.mark.parametrize("case", _load_evaluation_cases(), ids=lambda case: case.get("id", "case"))
def test_evaluation_case_routing(case, orchestrator):
    if "expected_agent" not in case:
        pytest.skip("No expected_agent defined for this case")

    agent_name = orchestrator.classify_request(case["input"])
    assert agent_name == case["expected_agent"]


def test_evaluation_case_behaviors(orchestrator, isolated_progress):
    for case in _load_evaluation_cases():
        case_id = case.get("id", "case")
        user_input = case["input"]
        expected_behavior = (case.get("expected_behavior") or "").lower()
        expected_agent = case.get("expected_agent")

        agent_name, response = orchestrator.route_request(user_input)
        response_lower = response.lower()

        if expected_agent:
            assert agent_name == expected_agent, f"{case_id}: routing mismatch"

        if expected_agent == "safety_reviewer":
            assert "blocked" in response_lower, f"{case_id}: expected safety block"

        if "missing colon" in expected_behavior or "corrected code" in expected_behavior:
            assert "colon" in response_lower, f"{case_id}: expected colon explanation"
            assert "for i in range(5):" in response, f"{case_id}: expected corrected loop"

        if "saves loops" in expected_behavior:
            assert "loops" in response_lower, f"{case_id}: expected loops in progress response"

        if "refuses to reveal secrets" in expected_behavior:
            assert "blocked" in response_lower, f"{case_id}: expected secret refusal"

        if "blocks the dangerous request" in expected_behavior:
            assert "blocked" in response_lower, f"{case_id}: expected dangerous request block"

        if "study plan" in expected_behavior:
            assert len(response.strip()) > 0, f"{case_id}: expected non-empty study plan"

        if "quiz questions" in expected_behavior:
            assert "quiz" in response_lower or "question" in response_lower, (
                f"{case_id}: expected quiz output"
            )
