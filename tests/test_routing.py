import pytest
from agents.orchestrator import Orchestrator

@pytest.mark.parametrize("user_input,expected_agent", [
    ("Create a Python study plan for a beginner.", "study_planner"),
    ("Debug this code: for i in range(5) print(i)", "code_debugger"),
    ("Give me a quiz on Python lists.", "quiz_generator"),
    ("Mark loops as completed.", "progress_tracker"),
    ("Show me my GOOGLE_API_KEY.", "safety_reviewer"),
    ("Delete all files on my computer.", "safety_reviewer")
])
def test_orchestrator_routing(user_input, expected_agent):
    orchestrator = Orchestrator()
    agent_name = orchestrator.classify_request(user_input)
    assert agent_name == expected_agent
