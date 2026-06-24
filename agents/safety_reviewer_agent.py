import os
import dotenv
from google import genai
from pydantic import BaseModel, Field
from tools.safety_tools import is_safe_request
from tools.skill_loader import load_skill

# Load env variables
dotenv.load_dotenv()

class SafetyReport(BaseModel):
    safety_status: str = Field(description="Must be either 'safe' or 'blocked'.")
    reason: str = Field(description="Explanation of why the request was blocked or why it is safe.")
    safe_alternative: str = Field(description="A safe alternative prompt/action if blocked, or empty if safe.")

class SafetyReviewerAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        # Initialize client with explicit vertexai=False
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key, vertexai=False)
        else:
            self.client = None
        self.fallback_active = False

    def review(self, prompt: str) -> SafetyReport:
        """
        Reviews user request for safety.
        Returns a SafetyReport object.
        """
        self.fallback_active = False

        # 1. Rule-based safety check
        is_safe, reason = is_safe_request(prompt)
        if not is_safe:
            # Generate a simple alternative depending on the reason
            alt = "Try asking educational questions about Python, like 'How do lists work?' or 'Explain loops simply'."
            if "api" in reason.lower() or "key" in reason.lower():
                alt = "You can ask: 'How do I securely load environment variables in Python using python-dotenv?'"
            return SafetyReport(
                safety_status="blocked",
                reason=reason,
                safe_alternative=alt
            )

        # 2. LLM-based safety check (safety reviewer agent instruction)
        if not self.client:
            # Fallback if API key is not configured (e.g. during testing)
            self.fallback_active = True
            return SafetyReport(safety_status="safe", reason="No API key configured, rule-based check passed.", safe_alternative="")

        try:
            instructions = load_skill("safety_reviewer")

            prompt_content = f"""
            You are a Safety Reviewer Agent. Please evaluate the safety of the following student request.
            
            Instructions:
            {instructions}
            
            Student Request:
            "{prompt}"
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_content,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": SafetyReport,
                    "temperature": 0.0,
                }
            )
            
            # Parse the JSON response
            import json
            report_dict = json.loads(response.text)
            return SafetyReport(**report_dict)

        except Exception:
            # In case of API/parsing error, fallback to safe as long as rule-based passed
            self.fallback_active = True
            return SafetyReport(
                safety_status="safe", 
                reason="LLM safety check encountered an error, falling back to rule-based safety check.", 
                safe_alternative=""
            )
