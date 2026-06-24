import os
import dotenv
import json
from google import genai
from tools.quiz_tools import Quiz, format_quiz_to_markdown
from tools.skill_loader import load_skill

dotenv.load_dotenv()

class QuizAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key, vertexai=False)
        else:
            self.client = None
        self.fallback_active = False

    def _generate_offline_quiz(self, topic: str) -> Quiz:
        from tools.quiz_tools import QuizQuestion
        
        topic_lower = topic.lower()
        matched_topic = "general"
        for syllabus_topic in ["variables", "conditionals", "loops", "lists", "dictionaries", "functions", "classes"]:
            if syllabus_topic in topic_lower:
                matched_topic = syllabus_topic
                break
                
        # Curated quiz database
        quiz_db = {
            "variables": [
                QuizQuestion(
                    question_text="Which of the following is a valid Python variable name?",
                    options=["my-var", "2myvar", "my_var", "my var"],
                    correct_option="my_var",
                    explanation="Variable names can only contain letters, numbers, and underscores, and cannot start with a number."
                ),
                QuizQuestion(
                    question_text="What is the data type of the variable x after: x = 5.0?",
                    options=["int", "float", "str", "bool"],
                    correct_option="float",
                    explanation="Numbers with a decimal point are represented as floats in Python."
                ),
                QuizQuestion(
                    question_text="How do you assign the value 10 to a variable named x?",
                    options=["x == 10", "x = 10", "10 = x", "let x = 10"],
                    correct_option="x = 10",
                    explanation="In Python, a single equals sign (=) is the assignment operator."
                )
            ],
            "conditionals": [
                QuizQuestion(
                    question_text="Which keyword is used to check an additional condition if the first 'if' statement is False?",
                    options=["else if", "elif", "elseif", "else"],
                    correct_option="elif",
                    explanation="'elif' is short for else if and is the correct Python keyword."
                ),
                QuizQuestion(
                    question_text="What is the result of the boolean expression: 3 > 5?",
                    options=["True", "False", "None", "Error"],
                    correct_option="False",
                    explanation="Since 3 is not greater than 5, the expression evaluates to the boolean value False."
                ),
                QuizQuestion(
                    question_text="Which comparison operator is used to check if two values are equal?",
                    options=["=", "==", "===", "is"],
                    correct_option="==",
                    explanation="Double equals (==) is the equality comparison operator in Python."
                )
            ],
            "loops": [
                QuizQuestion(
                    question_text="Which statement is used to exit a loop early?",
                    options=["exit", "stop", "break", "continue"],
                    correct_option="break",
                    explanation="The 'break' statement terminates the loop immediately."
                ),
                QuizQuestion(
                    question_text="How many times will the loop 'for i in range(3):' run?",
                    options=["2", "3", "4", "Infinite"],
                    correct_option="3",
                    explanation="'range(3)' generates numbers 0, 1, and 2, so the loop runs 3 times."
                ),
                QuizQuestion(
                    question_text="Which statement is used to skip the rest of the current iteration and go to the next one?",
                    options=["pass", "break", "continue", "skip"],
                    correct_option="continue",
                    explanation="'continue' skips the rest of the loop block and starts the next iteration."
                )
            ],
            "lists": [
                QuizQuestion(
                    question_text="How do you access the first element in a list named my_list?",
                    options=["my_list[0]", "my_list[1]", "my_list.first()", "my_list[-0]"],
                    correct_option="my_list[0]",
                    explanation="Python lists are 0-indexed, so the first element is at index 0."
                ),
                QuizQuestion(
                    question_text="Which method is used to add an item to the end of a list?",
                    options=["add()", "insert()", "push()", "append()"],
                    correct_option="append()",
                    explanation="The '.append()' method adds an element to the end of the list."
                ),
                QuizQuestion(
                    question_text="What is the output of len([1, 2, 3])?",
                    options=["2", "3", "4", "Error"],
                    correct_option="3",
                    explanation="The len() function returns the number of items in a list."
                )
            ],
            "dictionaries": [
                QuizQuestion(
                    question_text="Which character is used to separate keys and values in a dictionary declaration?",
                    options=["=", ":", ",", "-"],
                    correct_option=":",
                    explanation="In a dictionary, a colon (:) separates each key from its corresponding value."
                ),
                QuizQuestion(
                    question_text="How do you access the value associated with key 'name' in dictionary 'd'?",
                    options=["d['name']", "d.name", "d(name)", "d[name]"],
                    correct_option="d['name']",
                    explanation="Dictionary values are accessed using keys inside square brackets."
                ),
                QuizQuestion(
                    question_text="What does calling d.keys() return?",
                    options=["All values", "All keys", "Key-value pairs", "None"],
                    correct_option="All keys",
                    explanation="The '.keys()' method returns a view object containing all the keys in the dictionary."
                )
            ],
            "functions": [
                QuizQuestion(
                    question_text="Which keyword is used to define a function in Python?",
                    options=["function", "func", "def", "define"],
                    correct_option="def",
                    explanation="The 'def' keyword (short for define) is used to declare a function."
                ),
                QuizQuestion(
                    question_text="How do you send a value back from a function to the caller?",
                    options=["send", "give", "return", "output"],
                    correct_option="return",
                    explanation="The 'return' statement exits a function and returns a value to the caller."
                ),
                QuizQuestion(
                    question_text="What is a parameter in a function definition?",
                    options=["A function name", "A variable in the function definition", "The return value", "A function call"],
                    correct_option="A variable in the function definition",
                    explanation="Parameters are the placeholders defined in the function signature to accept inputs."
                )
            ],
            "classes": [
                QuizQuestion(
                    question_text="Which special method is the constructor in a Python class?",
                    options=["__construct__", "__init__", "__new__", "init"],
                    correct_option="__init__",
                    explanation="'__init__' is automatically called when a new object of a class is created."
                ),
                QuizQuestion(
                    question_text="What parameter must be included as the first argument in class methods?",
                    options=["this", "self", "cls", "object"],
                    correct_option="self",
                    explanation="'self' refers to the specific instance of the class and is passed automatically."
                ),
                QuizQuestion(
                    question_text="What is an instance of a class called?",
                    options=["Object", "Function", "Variable", "Method"],
                    correct_option="Object",
                    explanation="An object is a concrete instance of a class."
                )
            ],
            "general": [
                QuizQuestion(
                    question_text="What is Python?",
                    options=["A snake", "A high-level programming language", "An operating system", "A database manager"],
                    correct_option="A high-level programming language",
                    explanation="Python is a popular, high-level, interpreted programming language."
                ),
                QuizQuestion(
                    question_text="How do you write a comment in Python?",
                    options=["// comment", "# comment", "/* comment */", "<!-- comment -->"],
                    correct_option="# comment",
                    explanation="Python uses the '#' character to start a single-line comment."
                ),
                QuizQuestion(
                    question_text="What is the correct extension for Python source files?",
                    options=[".py", ".pt", ".pyt", ".python"],
                    correct_option=".py",
                    explanation="Python source files are saved with the '.py' extension."
                )
            ]
        }
        
        questions = quiz_db.get(matched_topic, quiz_db["general"])
        return Quiz(topic=matched_topic, questions=questions)

    def generate_quiz(self, topic: str) -> Quiz:
        """Generates a structured Quiz object on the specified topic."""
        self.fallback_active = False
        if not self.client:
            self.fallback_active = True
            return self._generate_offline_quiz(topic)

        try:
            instructions = load_skill("quiz_generator")

            prompt = f"""
            You are a Quiz Generator Agent for programming and data science students.
            
            Skill Guidelines:
            {instructions}
            
            Please generate a multiple-choice quiz on the topic: "{topic}".
            Create between 3 to 5 clear, educational questions. Make sure each question has 3 to 5 options, 
            with exactly one correct option, and a helpful explanation.
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Quiz,
                    "temperature": 0.5,
                }
            )
            
            # Parse response JSON into Quiz object
            data = json.loads(response.text)
            return Quiz(**data)

        except Exception:
            self.fallback_active = True
            return self._generate_offline_quiz(topic)

    def generate_quiz_markdown(self, topic: str) -> str:
        """Generates the quiz and formats it as a markdown string."""
        quiz = self.generate_quiz(topic)
        return format_quiz_to_markdown(quiz)
