# LearnMate AI Project Specification

## Overview
LearnMate AI is a multi-agent study and coding coach for students. It helps learners understand programming topics, debug beginner code, generate quizzes, and track progress.

## Kaggle Capstone Track
Agents for Good

## Problem
Many students struggle to learn programming because they:
- Do not know what to study next
- Get stuck on code errors
- Lack simple explanations
- Do not practise enough
- Forget what they have already completed

## Solution
LearnMate AI uses a custom Python orchestrator with Gemini SDK integration and offline fallback. Multiple specialized agents guide students through learning.

## Main Features
1. Study Planning
   - Creates a personalized learning path.
   - Recommends what to study next.

2. Topic Explanation
   - Explains coding and data science topics in simple language.
   - Uses beginner-friendly examples.

3. Code Debugging
   - Accepts beginner code snippets.
   - Explains what the code does.
   - Identifies likely mistakes.
   - Suggests safer corrections.

4. Quiz Generation
   - Creates short quizzes from a selected topic.
   - Provides answers and feedback.

5. Progress Tracking
   - Saves completed topics locally.
   - Shows what the student has already covered.
   - Recommends the next topic.

6. Safety Review
   - Checks for exposed API keys.
   - Blocks dangerous requests.
   - Avoids unsafe code execution.

## Course Concepts Demonstrated
- Agentic engineering instead of casual vibe coding
- Multi-agent system
- Harness/orchestrator
- Agent skills using skill.md files
- Progressive disclosure through skills
- Security guardrails
- Environment variables
- Sandbox-style safe code handling
- Evaluation cases
- Spec-driven development

## User Flow
1. Student opens the Streamlit app.
2. Student enters a request.
3. Orchestrator classifies the request.
4. Correct specialist agent handles it.
5. Safety reviewer checks the response.
6. Final answer is shown to the student.
7. Progress may be saved locally.

## Example Requests
- Create a Python learning plan for me.
- Explain while loops simply.
- Debug this Python code.
- Give me a quiz on lists.
- Mark functions as completed.
- What should I study next?

## Success Criteria
The project is successful if:
- It runs locally.
- It uses multiple agents.
- It includes skill.md files.
- It has safety checks.
- It saves progress locally.
- It has tests.
- It has clear documentation.
- It can be reproduced by another user using free or accessible tools.
