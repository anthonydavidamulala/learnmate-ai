from pydantic import BaseModel, Field

class QuizQuestion(BaseModel):
    question_text: str = Field(description="The question prompt for the student.")
    options: list[str] = Field(description="List of 3 to 5 multiple choice options.")
    correct_option: str = Field(description="The exact text string matching the correct option from the options list.")
    explanation: str = Field(description="A short, clear explanation of why the correct option is correct.")

class Quiz(BaseModel):
    topic: str = Field(description="The topic of the quiz.")
    questions: list[QuizQuestion] = Field(description="A list of 3 to 5 multiple-choice questions.")

def format_quiz_to_markdown(quiz: Quiz) -> str:
    """Formats a Quiz object into a human-readable markdown string."""
    markdown = f"### Quiz on: {quiz.topic.title()}\n\n"
    for idx, q in enumerate(quiz.questions, 1):
        markdown += f"**Question {idx}:** {q.question_text}\n"
        for opt_idx, opt in enumerate(q.options):
            markdown += f"- {opt}\n"
        markdown += "\n"
    
    markdown += "### Answer Key\n\n"
    for idx, q in enumerate(quiz.questions, 1):
        markdown += f"**Answer {idx}:** {q.correct_option}\n"
        markdown += f"**Explanation:** {q.explanation}\n\n"
        
    return markdown

def verify_answer(question: QuizQuestion, selected_answer: str) -> tuple[bool, str]:
    """Verifies a selected answer against the correct option."""
    is_correct = selected_answer.strip().lower() == question.correct_option.strip().lower()
    return is_correct, question.explanation
