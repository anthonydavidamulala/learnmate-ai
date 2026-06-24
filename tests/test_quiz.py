import pytest
from agents.quiz_agent import QuizAgent
from tools.quiz_tools import Quiz, QuizQuestion, verify_answer

def test_quiz_model_structure():
    # Verify that Quiz and QuizQuestion can be constructed properly
    q = QuizQuestion(
        question_text="What is print() used for in Python?",
        options=["To display output", "To load a file", "To loop", "To import a library"],
        correct_option="To display output",
        explanation="The print() function prints the specified message to the screen or other standard output device."
    )
    quiz = Quiz(topic="python basics", questions=[q])
    
    assert quiz.topic == "python basics"
    assert len(quiz.questions) == 1
    assert quiz.questions[0].correct_option == "To display output"

def test_verify_answer():
    q = QuizQuestion(
        question_text="What is a loop?",
        options=["A variable", "A repeated instruction block", "A type of list"],
        correct_option="A repeated instruction block",
        explanation="Loops repeat instructions until a condition is met."
    )
    
    is_correct, explanation = verify_answer(q, "A repeated instruction block")
    assert is_correct is True
    assert "repeat" in explanation
    
    is_correct2, _ = verify_answer(q, "A variable")
    assert is_correct2 is False

def test_quiz_agent_generation():
    agent = QuizAgent()
    quiz = agent.generate_quiz("lists")
    assert isinstance(quiz, Quiz)
    assert len(quiz.questions) >= 1
    for q in quiz.questions:
        assert isinstance(q, QuizQuestion)
        assert len(q.options) >= 2
        assert q.correct_option in q.options
        assert len(q.explanation) > 0
        assert len(q.question_text) > 0
