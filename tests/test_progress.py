import pytest
from agents.progress_tracker_agent import ProgressTrackerAgent
from tools import progress_store


@pytest.fixture
def isolated_progress(monkeypatch, tmp_path):
    progress_file = tmp_path / "progress.json"
    monkeypatch.setattr(progress_store, "PROGRESS_FILE", str(progress_file))
    return progress_file


def test_mark_real_topic_completed(isolated_progress):
    agent = ProgressTrackerAgent()
    response = agent.track_progress("Mark loops as completed.")

    assert "loops" in response.lower()
    assert "Success" in response
    assert progress_store.get_completed_topics() == ["loops"]


def test_unknown_topic_not_saved(isolated_progress):
    agent = ProgressTrackerAgent()
    response = agent.track_progress("Mark this as completed.")

    completed = progress_store.get_completed_topics()
    assert "unknown" not in completed
    assert completed == []
    assert "could not identify" in response.lower()


def test_normalize_topics_rejects_placeholders():
    agent = ProgressTrackerAgent()
    normalized = agent._normalize_topics(["unknown", "loops", "UNCLEAR", "lists"])

    assert normalized == ["loops", "lists"]
