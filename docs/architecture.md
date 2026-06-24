# LearnMate AI Architecture

## Project Goal

LearnMate AI is a multi-agent study and coding coach for students learning programming, data science, and AI. It helps learners plan study paths, debug beginner code, practice with quizzes, track progress, and stay safe while learning.

The system is built as a **custom Python orchestrator with Gemini SDK integration and offline fallback**. It does not use Google ADK agent objects in code; routing and specialist agents are implemented directly in Python.

## Multi-Agent Architecture

LearnMate AI uses six coordinated roles:

| Agent | File | Responsibility |
| --- | --- | --- |
| Orchestrator | `agents/orchestrator.py` | Routes requests and applies output safety checks |
| Study Planner | `agents/study_planner_agent.py` | Creates study plans and explanations |
| Code Debugger | `agents/code_debugger_agent.py` | Explains beginner code errors safely |
| Quiz Generator | `agents/quiz_agent.py` | Builds topic quizzes with answers |
| Progress Tracker | `agents/progress_tracker_agent.py` | Saves and recommends learning topics |
| Safety Reviewer | `agents/safety_reviewer_agent.py` | Blocks unsafe requests and secrets |

## Orchestrator Routing Flow

```text
User request
    |
    v
Safety pre-check (rule-based)
    |
    +-- blocked --> Safety Reviewer response
    |
    v
Keyword routing (quiz, progress, debug, plan)
    |
    v
Optional Gemini classification (when API key is available)
    |
    v
Specialist agent response
    |
    v
Output safety review (except safety responses)
    |
    v
Final response to user
```

The orchestrator uses:

- Rule-based safety checks first
- Fast keyword routing for common intents
- Gemini structured JSON routing when `GOOGLE_API_KEY` is configured
- Offline keyword fallback when the API is unavailable

## Tools Used

| Tool | Purpose |
| --- | --- |
| `tools/progress_store.py` | Local JSON progress memory |
| `tools/quiz_tools.py` | Quiz models and answer checking |
| `tools/safety_tools.py` | Rule-based unsafe request detection |
| `tools/skill_loader.py` | Loads `skills/*/skill.md` for Gemini prompts |

Agents call these tools directly. There is no MCP server or external tool protocol in the current version.

## Agent Skills

Each specialist agent has a `skill.md` file under `skills/` that defines role, tone, and output expectations.

- `study_planner`, `quiz_generator`, `safety_reviewer`, and `progress_tracker` load skill content into Gemini prompts through `tools/skill_loader.py`.
- `code_debugger` uses a safe offline rule-based parser and does not require live model calls for common beginner syntax issues.

Skill files are the project's spec-driven behavior layer for online generation.

## Safety Guardrails

Safety is applied in two places:

1. **Input review** before routing
2. **Output review** before returning specialist responses

The Safety Reviewer blocks examples such as:

- Requests for API keys or secrets
- Destructive system commands
- Dangerous instructions outside educational support

The Code Debugger analyzes code text only. It does not execute user code or run shell commands.

## Offline Fallback

LearnMate AI is designed to keep working locally even when:

- `GOOGLE_API_KEY` is missing
- Gemini quota is unavailable
- Network access fails during testing

Offline behavior includes:

- Keyword-based orchestrator routing
- Curated study plans in `StudyPlannerAgent`
- Rule-based debugging in `CodeDebuggerAgent`
- Curated quizzes in `QuizAgent`
- Rule-based progress parsing in `ProgressTrackerAgent`
- Rule-based safety blocking in `SafetyReviewerAgent`

## Progress Memory

Completed topics are stored in `data/progress.json` through `tools/progress_store.py`.

The progress tracker only saves valid syllabus topics such as `variables`, `loops`, `lists`, and `functions`. If the learner does not name a clear topic, nothing is saved and the agent asks for a clearer topic name.

## Specs and Evaluation Cases

The `specs/` folder drives project requirements:

- `project_spec.md` — product goals and success criteria
- `requirements.yaml` — feature and security requirements
- `evaluation_cases.yaml` — routing and behavior test cases

`tests/test_evaluation_cases.py` loads the YAML cases and validates orchestrator routing plus key expected behaviors such as safety blocking and debugger corrections.

## Tests

Automated tests live in `tests/`:

- `test_routing.py` — orchestrator routing
- `test_evaluation_cases.py` — spec-driven evaluation cases
- `test_safety.py` — safety blocking
- `test_quiz.py` — quiz generation and answer checking
- `test_code_debugger.py` — debugger offline fallback
- `test_progress.py` — progress saving and unknown-topic protection

Run all tests with:

```bash
python -m pytest
```

## Future Improvements

The current version is intentionally local, simple, and reproducible. Future versions may add:

- MCP server/tools for standardized external tool access
- Agent-to-agent (A2A) collaboration between specialists
- Cloud deployment for online access
- Cloud database storage for synced progress
- A sandboxed code execution environment
- More autonomous learning workflows

These are documented as future improvements, not current implemented features.
