import os
import re
import dotenv
from google import genai
from pydantic import BaseModel, Field
from tools import progress_store

dotenv.load_dotenv()

class ProgressAction(BaseModel):
    action: str = Field(description="Must be 'mark_completed', 'view_progress', 'recommend_next', or 'reset_progress'.")
    topics: list[str] = Field(description="List of topics mentioned to be marked completed (e.g. ['loops']), or empty list.")

class ProgressTrackerAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key, vertexai=False)
        else:
            self.client = None

    def track_progress(self, request: str) -> str:
        """
        Parses the progress request, updates local storage, and generates status.
        """
        action = "view_progress"
        topics_to_complete = []

        # Try to extract action/topics using LLM if client is available
        if self.client:
            try:
                prompt = f"""
                You are a Progress Tracker Agent. Inspect this user request and determine the action:
                1. 'mark_completed': The user wants to mark one or more programming topics as completed/finished.
                2. 'view_progress': The user wants to see what they have completed or check their current progress.
                3. 'recommend_next': The user is asking what to study next or for a recommendation.
                4. 'reset_progress': The user wants to clear or reset their progress.
                
                User Request:
                "{request}"
                """
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": ProgressAction,
                        "temperature": 0.0,
                    }
                )
                import json
                result = json.loads(response.text)
                action = result.get("action", "view_progress")
                topics_to_complete = result.get("topics", [])
            except Exception:
                # Fallback to rule-based parsing if LLM fails
                action = self._rule_based_parse(request)
        else:
            action = self._rule_based_parse(request)

        # Execute the action on the progress store
        message = ""
        if action == "mark_completed":
            if not topics_to_complete:
                # Fallback rule-based extraction from text
                extracted = self._extract_topics_rule_based(request)
                if extracted:
                    topics_to_complete = extracted
                else:
                    topics_to_complete = ["unknown"]

            for topic in topics_to_complete:
                progress_store.mark_completed(topic)
            
            topics_str = ", ".join(topics_to_complete)
            message = f"Success! Marked as completed: **{topics_str}**.\n\n"

        elif action == "reset_progress":
            progress_store.reset_progress()
            message = "Your learning progress has been reset.\n\n"

        # Load current status to formulate output according to skill.md
        completed_topics = progress_store.get_completed_topics()
        next_topic = progress_store.get_next_recommendation()
        
        # Build markdown status report
        status_report = message
        status_report += "### Learning Progress Report\n"
        
        if completed_topics:
            status_report += "- **Completed Topics:**\n"
            for t in completed_topics:
                status_report += f"  - ✅ {t.title()}\n"
        else:
            status_report += "- **Completed Topics:** None yet. Ready to start your journey!\n"
            
        status_report += f"- **Current/Next Recommended Topic:** {next_topic.title()}\n"
        status_report += f"- **Next Recommendation:** {next_topic.title()}\n\n"
        
        # Add encouraging message
        if not completed_topics:
            status_report += "🤖 *\"Every expert coder started with their first print statement. Let's get learning!\"*"
        elif len(completed_topics) < 3:
            status_report += "🤖 *\"Great job starting! Keep taking quizzes and writing code to reinforce your skills.\"*"
        elif len(completed_topics) < len(progress_store.SYLLABUS):
            status_report += "🤖 *\"You're making amazing progress! You've got this!\"*"
        else:
            status_report += "🤖 *\"Congratulations! You have completed the core syllabus! Challenge yourself with advanced concepts next!\"*"
            
        return status_report

    def _rule_based_parse(self, request: str) -> str:
        req_lower = request.lower()
        if "completed" in req_lower or "done" in req_lower or "finished" in req_lower or "mark" in req_lower:
            return "mark_completed"
        elif "reset" in req_lower or "clear" in req_lower:
            return "reset_progress"
        elif "next" in req_lower or "recommend" in req_lower or "study next" in req_lower:
            return "recommend_next"
        else:
            return "view_progress"

    def _extract_topics_rule_based(self, request: str) -> list[str]:
        req_lower = request.lower()
        # Look for keywords from the syllabus
        found = []
        for topic in progress_store.SYLLABUS:
            if topic in req_lower:
                found.append(topic)
        return found
