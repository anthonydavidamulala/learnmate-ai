# LearnMate AI - Multi-Agent Study & Coding Coach

LearnMate AI is a multi-agent study and coding coach designed for students learning Python programming, data science, and AI. It guides learners through curriculum roadmaps, details topic explanations, debugs beginner code safely, generates interactive topic-based quizzes, and monitors learning progress.

This project is built as a multi-agent harness demonstrating:
- Multi-agent orchestration
- Agent skills (using skill.md definition files)
- Input/output safety and security guardrails
- Local JSON storage progress persistence
- Spec-driven development and automated evaluation

---

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
Set up the virtual environment and install the required packages:
```bash
# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory (you can copy from `.env.example`) and fill in your Gemini Developer API Key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_GENAI_USE_ENTERPRISE=FALSE
```
*Note: Make sure `.env` is never committed to Git.*

---

## 💻 Running the Application

You can interact with the coach via the Command Line Interface (CLI) or the rich Streamlit Web Dashboard:

### Option A: Streamlit Web Dashboard (Recommended)
Start the web app:
```bash
streamlit run app.py
```
This launches a beautiful local web interface in your browser showing:
- Interactive chatbot console.
- A **Study Room Sidebar** showing syllabus progress, a core topics completion checklist, and active recommendations on what to learn next.
- Stateful **Interactive Quizzes** where you can submit options, get instant feedback, and mark topics completed on scoring 100%.

### Option B: Command Line Interface (CLI)
Start the CLI application:
```bash
python main.py
```
Type your requests (e.g., `"Create a study plan for functions"`, `"Debug my loops code"`, or `"Give me a quiz on lists"`) directly in the shell.

---

## 🧪 Running Tests

The test suite runs automatically with `pytest`. Run this command to verify that all agent routing logic, safety parameters, and quiz builders are functioning perfectly:

```bash
python -m pytest
```

---

## 📂 Project Structure

- `agents/`: Python agent definitions (Orchestrator, Study Planner, Code Debugger, Quiz Agent, Progress Tracker, Safety Reviewer).
- `skills/`: Markdown instructions defining behavioral guardrails for each agent role.
- `tools/`: Backing libraries (Safety validations, local progress storage, quiz schema definitions).
- `tests/`: Automated pytest modules validating routing, quiz generation, and safety filters.
- `specs/`: Project specs and evaluation cases.
- `data/`: Local storage folder for progress database.
