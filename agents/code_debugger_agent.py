import os
import re
import dotenv
from google import genai
from tools.skill_loader import load_skill

dotenv.load_dotenv()


class CodeDebuggerAgent:
    """Beginner-friendly code debugging agent."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key, vertexai=False)
        else:
            self.client = None
        self.fallback_active = False

    def _extract_code(self, request: str) -> str:
        text = request.strip()

        markers = [
            "debug this code:",
            "debug this:",
            "fix this code:",
            "code:",
        ]

        lowered = text.lower()
        for marker in markers:
            if marker in lowered:
                start = lowered.index(marker) + len(marker)
                return text[start:].strip()

        return text

    def debug_code(self, request: str) -> str:
        """Method expected by orchestrator.py."""
        return self.handle(request)

    def handle(self, request: str) -> str:
        self.fallback_active = False
        if not self.client:
            self.fallback_active = True
            return self._generate_offline_debug(request)

        try:
            instructions = load_skill("code_debugger")
            code = self._extract_code(request)
            prompt = f"""
            You are a Code Debugger Agent for beginner Python students.

            Skill Guidelines:
            {instructions}

            Debug this student code safely. Do not run commands or suggest dangerous actions.
            Explain likely mistakes in simple language.

            Student request/code:
            {code}

            Return Markdown with:
            - what the code is trying to do
            - what is wrong
            - corrected code in a Python fenced block
            - a short explanation
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"temperature": 0.3},
            )
            return response.text

        except Exception:
            # Offline fallback only after Gemini/API failure or missing response.
            self.fallback_active = True
            return self._generate_offline_debug(request)

    def _generate_offline_debug(self, request: str) -> str:
        code = self._extract_code(request)
        lowered = code.lower()

        if re.search(r"\bfor\s+\w+\s+in\s+range\s*\([^)]+\)\s+print\s*\(", lowered):
            return (
                "### Code Debugging Report (Offline Fallback)\n\n"
                "**What the code is trying to do:**\n"
                "The code is trying to loop through numbers and print each value.\n\n"
                "**What is wrong:**\n"
                "The `for` loop is missing a colon `:` after `range(5)`.\n\n"
                "**Corrected code:**\n"
                "```python\n"
                "for i in range(5):\n"
                "    print(i)\n"
                "```\n\n"
                "**Simple explanation:**\n"
                "In Python, statements like `for`, `while`, `if`, `def`, and `class` must end with a colon.\n"
                "The indented line below belongs inside that block.\n\n"
                "**Practice tip:**\n"
                "Whenever you write a loop, check two things: the colon and the indentation."
            )

        if "while" in lowered:
            return (
                "### Code Debugging Report (Offline Fallback)\n\n"
                "**What the code is doing:**\n"
                "The code appears to use a `while` loop.\n\n"
                "**Common things to check:**\n"
                "1. Does the loop condition eventually become false?\n"
                "2. Is the counter being updated?\n"
                "3. Is the indentation correct?\n"
                "4. Is there a colon after the while condition?\n\n"
                "**Example:**\n"
                "```python\n"
                "number = 1\n"
                "while number <= 5:\n"
                "    print(number)\n"
                "    number += 1\n"
                "```\n\n"
                "**Practice tip:**\n"
                "Always update the loop variable to avoid an infinite loop."
            )

        if "print(" in lowered and lowered.count("(") != lowered.count(")"):
            return (
                "### Code Debugging Report (Offline Fallback)\n\n"
                "**What is wrong:**\n"
                "Your code may have unmatched brackets or parentheses.\n\n"
                "**Simple fix:**\n"
                "Check that every opening bracket `(` has a matching closing bracket `)`.\n\n"
                "**Practice tip:**\n"
                "When debugging syntax errors, first check brackets, quotes, colons, and indentation."
            )

        return (
            "### Code Debugging Report (Offline Fallback)\n\n"
            "**What the code is doing:**\n"
            "The code appears to be a Python snippet.\n\n"
            "**What to check:**\n"
            "The basic offline parser did not detect a common syntax pattern, so check:\n"
            "1. Missing colons\n"
            "2. Wrong indentation\n"
            "3. Unclosed brackets or quotes\n"
            "4. Misspelled variable names\n"
            "5. Logic errors\n\n"
            "**Practice tip:**\n"
            "Paste the exact Python error message together with the code for a more accurate explanation."
        )


def debug_code(request: str) -> str:
    """Compatibility function for tests or older orchestrator code."""
    return CodeDebuggerAgent().debug_code(request)
