import os


def load_skill(agent_folder: str) -> str:
    """Load skill.md instructions for an agent folder under skills/."""
    skill_path = os.path.join("skills", agent_folder, "skill.md")
    if os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""
