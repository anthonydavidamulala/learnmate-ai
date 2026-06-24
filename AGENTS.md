# AGENTS.md - LearnMate AI

## Project Name
LearnMate AI

## Owner
Amulala Anthony David

## Track
Agents for Good

## Project Goal
LearnMate AI is a multi-agent study and coding coach for students learning programming, data science, and AI.

The system helps students:
- Create study plans
- Understand topics in simple language
- Debug beginner code
- Generate quizzes
- Track learning progress
- Stay safe by avoiding dangerous code execution and exposed secrets

## Technology Stack
- Python
- Custom Python orchestrator with Gemini SDK integration and offline fallback
- Google Gemini API (`google-genai`)
- Streamlit
- python-dotenv
- PyYAML
- pytest
- pydantic
- JSON local storage

## Important Folders
- agents/ contains the Python agent files.
- skills/ contains agent skill folders with skill.md files.
- tools/ contains helper tools used by agents.
- specs/ contains project specifications and evaluation cases.
- tests/ contains automated tests.
- docs/ contains documentation.
- data/ contains local progress data.

## Agent Roles
1. Orchestrator Agent
   - Receives the user's request.
   - Chooses the correct specialist agent.
   - Sends the final safe response back to the user.

2. Study Planner Agent
   - Creates learning plans.
   - Explains what to study next.

3. Code Debugger Agent
   - Explains beginner code errors.
   - Suggests fixes.
   - Must not run dangerous system commands.

4. Quiz Agent
   - Generates short quizzes.
   - Checks answers.
   - Gives feedback.

5. Progress Tracker Agent
   - Saves completed topics.
   - Loads previous progress.
   - Recommends next topics.

6. Safety Reviewer Agent
   - Checks responses for safety issues.
   - Blocks exposed API keys, dangerous commands, and harmful advice.

## Security Rules
- Never expose API keys.
- Never commit .env to GitHub.
- Never run destructive commands such as deleting system files.
- Never access production databases.
- Never store sensitive personal data.
- Use .env for local secrets.
- Use .env.example only as a template.
- Ask for human approval before any risky action.

## Development Rules
- Follow the spec files inside specs/.
- Keep the project simple and reproducible.
- Prefer free and reasonably accessible tools.
- Do not depend on paid private datasets or expensive software.
- Add tests for important behavior.
- Keep code readable for beginner students.

## Completion Requirements
Before calling a task complete:
1. The app must run.
2. The agents must route correctly.
3. Tests must pass.
4. No API key should appear in code.
5. README must explain setup and usage.
6. The project must demonstrate at least three course concepts:
   - Multi-agent system
   - Agent skills
   - Harness/orchestration
   - Safety/security
   - Evaluation/testing
   - Spec-driven development
