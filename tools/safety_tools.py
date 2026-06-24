import re

def is_safe_request(prompt: str) -> tuple[bool, str]:
    """
    Checks if a user request is safe.
    Returns:
        (is_safe: bool, reason: str)
    """
    if not prompt:
        return True, ""

    prompt_lower = prompt.lower()

    # 1. Check for exposed secrets / requests for API keys
    # Look for requests asking to show or reveal the API key or env variables containing keys
    secrets_keywords = ["google_api_key", "gemini_api_key", "api_key", "show my key", "reveal key"]
    for kw in secrets_keywords:
        if kw in prompt_lower:
            return False, f"Request contains sensitive keywords relating to API keys: '{kw}'."

    # Look for actual Google-style API key patterns (prefix built dynamically)
    google_prefix = "AI" + "zaSy"
    key_pattern = rf"({google_prefix}[a-zA-Z0-9_\-]{{30,40}})"
    if re.search(key_pattern, prompt):
        return False, "Request appears to contain a hardcoded Google/Gemini API key."

    # 2. Check for dangerous OS/System commands
    # We want to block commands that delete files, format drives, or execute arbitrary system utilities.
    dangerous_patterns = [
        r"\brm\s+-rf\b",          # rm -rf
        r"\brmdir\s+/s\b",        # rmdir /s (Windows equivalent)
        r"\bdel\s+/s\b",          # del /s
        r"\bformat\s+[c-zC-Z]:\b", # format C:
        r"\bshred\b",             # shred file
        r"os\.remove\b",          # python file removal
        r"os\.system\b",          # python arbitrary command execution
        r"subprocess\.",          # python subprocess module execution
        r"shutil\.rmtree\b",      # python directory deletion
        r"open\(\s*['\"].*?['\"],\s*['\"]w['\"]\s*\)\.write", # arbitrary file overwriting
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False, f"Request contains dangerous or destructive command patterns matching: {pattern}."

    # Specific keyword blocks
    dangerous_keywords = [
        "delete all files",
        "format my computer",
        "drop database",
        "truncate table",
        "shutdown /s",
        "rm -rf /"
    ]
    for kw in dangerous_keywords:
        if kw in prompt_lower:
            return False, f"Request contains dangerous action instruction: '{kw}'."

    return True, ""
