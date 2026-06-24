import os
import json

PROGRESS_FILE = os.path.join("data", "progress.json")

SYLLABUS = [
    "variables",
    "conditionals",
    "loops",
    "lists",
    "dictionaries",
    "functions",
    "classes"
]

def load_progress() -> dict:
    """Loads student progress from local JSON storage."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    
    if not os.path.exists(PROGRESS_FILE):
        default_progress = {"completed_topics": []}
        save_progress(default_progress)
        return default_progress
        
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "completed_topics" not in data:
                data["completed_topics"] = []
            return data
    except Exception:
        # If file is corrupted, return empty default
        return {"completed_topics": []}

def save_progress(data: dict) -> None:
    """Saves student progress to local JSON storage."""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def mark_completed(topic: str) -> dict:
    """Marks a topic as completed and saves the progress."""
    normalized_topic = topic.strip().lower()
    data = load_progress()
    completed = data.get("completed_topics", [])
    if normalized_topic not in completed:
        completed.append(normalized_topic)
        data["completed_topics"] = completed
        save_progress(data)
    return data

def get_completed_topics() -> list[str]:
    """Returns the list of completed topics."""
    data = load_progress()
    return data.get("completed_topics", [])

def reset_progress() -> dict:
    """Resets all completed topics."""
    data = {"completed_topics": []}
    save_progress(data)
    return data

def get_next_recommendation() -> str:
    """Recommends the next topic to study based on what has been completed."""
    completed = get_completed_topics()
    # Normalize completed topics to check against syllabus
    completed_normalized = {c.strip().lower() for c in completed}
    
    for topic in SYLLABUS:
        if topic not in completed_normalized:
            return topic
            
    return "Object-Oriented Programming (OOP) & Advanced Data Structures"
