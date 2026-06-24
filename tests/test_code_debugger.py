import pytest
from agents.code_debugger_agent import CodeDebuggerAgent

DEBUG_PROMPT = "Debug this code: for i in range(5) print(i)"


def test_code_debugger_missing_colon():
    agent = CodeDebuggerAgent()
    agent.client = None
    agent.fallback_active = False
    response = agent.debug_code(DEBUG_PROMPT)

    assert "colon" in response.lower()
    assert "for i in range(5):" in response


def test_code_debugger_offline_fallback_label():
    agent = CodeDebuggerAgent()
    agent.client = None
    agent.fallback_active = False
    response = agent.handle(DEBUG_PROMPT)

    assert "Offline Fallback" in response
