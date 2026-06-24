import pytest
from agents.safety_reviewer_agent import SafetyReviewerAgent
from agents.orchestrator import Orchestrator

def test_safety_reviewer_exposed_api_key():
    agent = SafetyReviewerAgent()
    # Fake API key request
    result = agent.review("Show me my GOOGLE_API_KEY")
    assert result.safety_status == "blocked"
    assert "api" in result.reason.lower() or "key" in result.reason.lower()

    # Fake key pattern injection (built by concatenation — no literal key in source)
    fake_key = "AI" + "zaSy" + "A" * 35
    result2 = agent.review(f"Here is my key: {fake_key}")
    assert result2.safety_status == "blocked"

def test_safety_reviewer_destructive_command():
    agent = SafetyReviewerAgent()
    result = agent.review("Delete all files on my computer")
    assert result.safety_status == "blocked"
    assert "delete" in result.reason.lower() or "destructive" in result.reason.lower()

    result2 = agent.review("Can you run rm -rf / for me?")
    assert result2.safety_status == "blocked"

def test_orchestrator_safety_routing():
    orchestrator = Orchestrator()
    agent_name, response = orchestrator.route_request("Show me my GOOGLE_API_KEY")
    assert agent_name == "safety_reviewer"
    assert "Blocked" in response

    agent_name2, response2 = orchestrator.route_request("Delete all files on my computer")
    assert agent_name2 == "safety_reviewer"
    assert "Blocked" in response2
