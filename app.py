import streamlit as st
import os
import dotenv
import json
from agents.orchestrator import Orchestrator
from tools import progress_store
from tools.quiz_tools import Quiz, QuizQuestion, verify_answer
from agents.quiz_agent import QuizAgent

# Load environment variables
dotenv.load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="LearnMate AI - Multi-Agent Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Main background */
    .stApp {
        background-color: #0d0e15;
        color: #e2e8f0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #141521 !important;
        border-right: 1px solid #23253b;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #a78bfa !important;
    }

    /* Header styling with linear gradient */
    .header-container {
        padding: 2rem 0rem 1rem 0rem;
        text-align: center;
        background: linear-gradient(180deg, rgba(124, 58, 237, 0.1) 0%, rgba(13, 14, 21, 0) 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
    }

    .main-title {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #a78bfa 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Glassmorphism Cards for Assistant Messages */
    .agent-card {
        background: rgba(30, 32, 50, 0.6);
        border: 1px solid rgba(167, 139, 250, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .agent-card:hover {
        border-color: rgba(167, 139, 250, 0.4);
        transform: translateY(-2px);
    }

    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-study_planner { background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-code_debugger { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-quiz_generator { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-progress_tracker { background-color: rgba(139, 92, 246, 0.2); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.3); }
    .badge-safety_reviewer { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

    /* User Message Bubble */
    .user-bubble {
        background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        margin-left: 20%;
        color: #f1f5f9;
        box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0d0e15;
    }
    ::-webkit-scrollbar-thumb {
        background: #1f2937;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #374151;
    }

    /* Interactive Quiz CSS */
    .quiz-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(52, 211, 153, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px 0 rgba(79, 70, 229, 0.3) !important;
    }

    .stButton>button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px 0 rgba(79, 70, 229, 0.4) !important;
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to get badge class
def get_badge_html(agent_name: str) -> str:
    badge_label = agent_name.replace("_", " ").title()
    return f'<span class="agent-badge badge-{agent_name}">{badge_label}</span>'

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = Orchestrator()
if "active_quiz" not in st.session_state:
    st.session_state.active_quiz = None
if "selected_quiz_answers" not in st.session_state:
    st.session_state.selected_quiz_answers = {}
if "quiz_feedback" not in st.session_state:
    st.session_state.quiz_feedback = {}

# Page Header
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">🎓 LearnMate AI</h1>
        <p class="subtitle">Your Multi-Agent Study & Coding Coach for Programming, Data Science & AI</p>
    </div>
""", unsafe_allow_html=True)

# SIDEBAR: Progress & Curriculum Control Panel
with st.sidebar:
    st.markdown("## 📊 Your Study Room")
    st.markdown("Track your learning progress and recommendations.")
    st.markdown("---")

    # Load progress store data
    completed = progress_store.get_completed_topics()
    syllabus = progress_store.SYLLABUS
    
    # Calculate percentage
    num_completed = len(completed)
    total_topics = len(syllabus)
    percentage = int((num_completed / total_topics) * 100) if total_topics > 0 else 0

    st.markdown(f"### Core Progress: `{percentage}%`")
    st.progress(percentage / 100.0)
    
    # Next Recommendation card
    next_rec = progress_store.get_next_recommendation()
    st.markdown(f"""
        <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 8px; padding: 1rem; margin: 1rem 0;">
            <span style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #a78bfa; letter-spacing: 0.05em;">Study Recommendation</span>
            <div style="font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-top: 0.25rem;">{next_rec.title()}</div>
        </div>
    """, unsafe_allow_html=True)

    # List completed/remaining topics
    st.markdown("### 📚 Core Syllabus")
    for topic in syllabus:
        is_done = topic.lower() in [c.lower() for c in completed]
        status_icon = "✅" if is_done else "⚫"
        st.markdown(f"{status_icon} **{topic.title()}**")

    st.markdown("---")
    
    # Actions
    if st.button("🔄 Reset Progress", use_container_width=True):
        progress_store.reset_progress()
        st.session_state.active_quiz = None
        st.session_state.selected_quiz_answers = {}
        st.session_state.quiz_feedback = {}
        st.rerun()

    # Helpful suggestions to click
    st.markdown("### 💡 Quick Queries")
    quick_queries = [
        "Create a study plan for functions.",
        "Give me a quiz on lists.",
        "Debug this Python code:\n```python\nfor i in range(5)\n    print(i)\n```",
        "Mark lists as completed."
    ]
    
    for qq in quick_queries:
        if st.button(qq[:35] + "..." if len(qq) > 35 else qq, key=f"quick_{qq}", use_container_width=True):
            # Pre-populate session variables or handle direct route
            st.session_state.user_query = qq
            # Trigger execute on quick queries by injecting standard submit behavior
            st.session_state.run_quick_query = True

# MAIN CHAT PANEL
chat_placeholder = st.container()

# Render Chat History
with chat_placeholder:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
                <div class="user-bubble">
                    <strong>You:</strong><br>{msg["content"]}
                </div>
            """, unsafe_allow_html=True)
        else:
            badge_html = get_badge_html(msg["agent"])
            st.markdown(f"""
                <div class="agent-card">
                    {badge_html}
                    <div>{msg["content"]}</div>
                </div>
            """, unsafe_allow_html=True)

# INTERACTIVE QUIZ RENDERER
# If a quiz is currently generated and stored in st.session_state, show it as an interactive widget!
if st.session_state.active_quiz:
    quiz = st.session_state.active_quiz
    st.markdown(f"""
        <div style="border-left: 4px solid #34d399; background: rgba(16, 185, 129, 0.05); padding: 1.5rem; border-radius: 0 12px 12px 0; margin-bottom: 2rem;">
            <h3 style="color: #34d399; margin-top: 0;">Interactive Quiz: {quiz.topic.title()}</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">Submit your answers below to verify your knowledge.</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("interactive_quiz_form"):
        for q_idx, q in enumerate(quiz.questions):
            st.markdown(f"**Question {q_idx + 1}:** {q.question_text}")
            # Get previous choice or default to None
            choice = st.radio(
                "Select one option:", 
                q.options, 
                key=f"quiz_opt_{q_idx}",
                index=None
            )
            st.session_state.selected_quiz_answers[q_idx] = choice
            
            # Show inline feedback if graded
            if q_idx in st.session_state.quiz_feedback:
                is_correct, feedback_msg = st.session_state.quiz_feedback[q_idx]
                if is_correct:
                    st.success(f"Correct! 🎉 {feedback_msg}")
                else:
                    st.error(f"Incorrect. {feedback_msg}")
            st.markdown("---")
            
        submitted = st.form_submit_form_processing = st.form_submit_button("Grade Quiz")
        if submitted:
            # Validate all questions
            correct_count = 0
            for q_idx, q in enumerate(quiz.questions):
                selected = st.session_state.selected_quiz_answers.get(q_idx)
                if selected:
                    is_corr, explanation = verify_answer(q, selected)
                    st.session_state.quiz_feedback[q_idx] = (is_corr, explanation)
                    if is_corr:
                        correct_count += 1
                else:
                    st.session_state.quiz_feedback[q_idx] = (False, "No answer selected.")
            
            # Show summary
            total = len(quiz.questions)
            st.success(f"Grading complete! You scored {correct_count} out of {total} correct.")
            
            # If student scored perfectly, mark the topic as completed in progress tracker!
            if correct_count == total and quiz.topic:
                progress_store.mark_completed(quiz.topic)
                st.toast(f"Congratulations! Topic '{quiz.topic}' marked as completed!", icon="🎉")
                # Trigger a refresh of the sidebar progress
                st.rerun()

# Chat Input field
user_query = st.chat_input("Ask a study plan, debug code, request a quiz...")

# If quick query was clicked
if getattr(st.session_state, "run_quick_query", False) and getattr(st.session_state, "user_query", None):
    user_query = st.session_state.user_query
    st.session_state.run_quick_query = False
    st.session_state.user_query = None

if user_query:
    # Render user query first
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Process request using Orchestrator
    with st.spinner("LearnMate AI is thinking..."):
        agent_name, response_text = st.session_state.orchestrator.route_request(user_query)
        
        # If the routed agent was the quiz generator, let's load/parse it as an active interactive quiz
        if agent_name == "quiz_generator":
            # Generate structured quiz using the quiz agent
            quiz_agent = st.session_state.orchestrator.quiz_agent
            structured_quiz = quiz_agent.generate_quiz(user_query)
            st.session_state.active_quiz = structured_quiz
            st.session_state.selected_quiz_answers = {}
            st.session_state.quiz_feedback = {}
            # Display a nice message in the chat
            response_text = f"I've generated a quiz about **{structured_quiz.topic.title()}** for you! Scroll down below the chat window to take it interactive! 📝"
        else:
            # For non-quiz agents, clear any old active quiz to keep screen clean
            st.session_state.active_quiz = None
            
        # Save response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "agent": agent_name
        })
        
    st.rerun()
