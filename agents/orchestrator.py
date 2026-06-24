import os
import dotenv
from google import genai
from pydantic import BaseModel, Field

# Import specialist agents
from agents.safety_reviewer_agent import SafetyReviewerAgent, SafetyReport
from agents.study_planner_agent import StudyPlannerAgent
from agents.code_debugger_agent import CodeDebuggerAgent
from agents.quiz_agent import QuizAgent
from agents.progress_tracker_agent import ProgressTrackerAgent

dotenv.load_dotenv()

class RouteResult(BaseModel):
    agent: str = Field(description="Must be one of 'study_planner', 'code_debugger', 'quiz_generator', 'progress_tracker', or 'safety_reviewer'.")

class Orchestrator:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key, vertexai=False)
        else:
            self.client = None

        # Instantiate specialist agents
        self.safety_agent = SafetyReviewerAgent()
        self.study_planner_agent = StudyPlannerAgent()
        self.code_debugger_agent = CodeDebuggerAgent()
        self.quiz_agent = QuizAgent()
        self.progress_tracker_agent = ProgressTrackerAgent()

    def classify_request(self, request: str) -> str:
        """
        Classifies the incoming user request into the correct specialist agent role.
        """
        # First, run rule-based / quick safety checks. If blocked, immediately route to safety_reviewer
        safety_report = self.safety_agent.review(request)
        if safety_report.safety_status == "blocked":
            return "safety_reviewer"

        # Check for obvious keywords to avoid LLM latency / fallback failures
        req_lower = request.lower()
        if any(kw in req_lower for kw in ["quiz", "test me", "practice question", "ask me question"]):
            return "quiz_generator"
        if any(kw in req_lower for kw in ["mark", "completed", "done", "finished", "progress", "study next", "what should i learn next"]):
            return "progress_tracker"
        if any(kw in req_lower for kw in ["debug", "error", "wrong", "fix", "syntax", "indented"]):
            return "code_debugger"
        if any(kw in req_lower for kw in ["plan", "study plan", "roadmap", "curriculum", "explain"]):
            return "study_planner"

        # Use Gemini model to classify the request if keyword matching is not definitive
        if self.client:
            try:
                prompt = f"""
                You are the Orchestrator Router for a student study and coding coach called LearnMate AI.
                Your job is to route the student request to the correct specialist agent:
                1. 'study_planner': For requests about creating study plans, roadmaps, step-by-step guides, or general topic explanations (e.g. "Explain loops simply").
                2. 'code_debugger': For requests showing code snippets, asking why code isn't working, or asking to debug errors.
                3. 'quiz_generator': For requests asking for quizzes, multiple-choice questions, or tests.
                4. 'progress_tracker': For requests updating or checking progress, marking topics as completed, or asking what to study next.
                5. 'safety_reviewer': For requests that look dangerous, ask for secrets/API keys, or system alterations.
                
                Student Request:
                "{request}"
                """
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": RouteResult,
                        "temperature": 0.0,
                    }
                )
                import json
                result = json.loads(response.text)
                return result.get("agent", "study_planner")
            except Exception:
                pass

        # Fallback default routing based on context
        if "code" in req_lower or "print(" in req_lower or "def " in req_lower:
            return "code_debugger"
        return "study_planner"

    def route_request(self, request: str) -> tuple[str, str]:
        """
        Routes the request to the correct agent, retrieves response, 
        and runs safety reviewer checks.
        Returns:
            (agent_name, response_text)
        """
        # 1. Classify the request
        agent_name = self.classify_request(request)

        # 2. Get response from routed agent
        response_text = ""
        
        if agent_name == "safety_reviewer":
            report = self.safety_agent.review(request)
            response_text = f"🛑 **Blocked by Safety Guardrails**\n\n**Reason:** {report.reason}"
            if report.safe_alternative:
                response_text += f"\n\n**Safe Alternative:** {report.safe_alternative}"
                
        elif agent_name == "study_planner":
            response_text = self.study_planner_agent.generate_plan(request)
            
        elif agent_name == "code_debugger":
            response_text = self.code_debugger_agent.debug_code(request)
            
        elif agent_name == "quiz_generator":
            response_text = self.quiz_agent.generate_quiz_markdown(request)
            
        elif agent_name == "progress_tracker":
            response_text = self.progress_tracker_agent.track_progress(request)
            
        else:
            response_text = "I'm sorry, I encountered an routing error. Please try again."

        # 3. Guardrail check on output response (excluding safety agent responses)
        if agent_name != "safety_reviewer":
            output_safety = self.safety_agent.review(response_text)
            if output_safety.safety_status == "blocked":
                agent_name = "safety_reviewer"
                response_text = f"🛑 **Response Blocked by Safety Guardrails**\n\n**Reason:** {output_safety.reason}"
                if output_safety.safe_alternative:
                    response_text += f"\n\n**Safe Alternative:** {output_safety.safe_alternative}"

        return agent_name, response_text
