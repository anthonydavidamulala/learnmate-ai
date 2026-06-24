import os
import dotenv
from google import genai
from tools.skill_loader import load_skill

dotenv.load_dotenv()

class StudyPlannerAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key, vertexai=False)
        else:
            self.client = None
        self.fallback_active = False

    def _generate_offline_plan(self, request: str) -> str:
        req_lower = request.lower()
        matched_topic = "general"
        
        # Syllabus topics
        syllabus_topics = ["variables", "conditionals", "loops", "lists", "dictionaries", "functions", "classes"]
        for topic in syllabus_topics:
            if topic in req_lower:
                matched_topic = topic
                break
                
        # Curated plan content
        plans = {
            "variables": {
                "explanation": "Variables are used to store data in a program. They act as labeled containers for values like numbers, text, or lists.",
                "plan": "1. Learn how to declare variables and assign values (e.g., `x = 5`).\n2. Understand basic data types: integers, floats, strings, and booleans.\n3. Practice naming variables using standard Python conventions (snake_case).",
                "task": "Create three variables representing a student's name, age, and grade, then print a message using them.",
                "next": "conditionals"
            },
            "conditionals": {
                "explanation": "Conditionals (`if`, `elif`, `else`) allow your program to make decisions and run different code based on whether a condition is True or False.",
                "plan": "1. Learn comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`).\n2. Write simple `if` statements.\n3. Add alternative branches using `elif` and `else`.",
                "task": "Write a script that checks a temperature variable and prints 'Hot' if it is above 30, 'Warm' if above 15, and 'Cold' otherwise.",
                "next": "loops"
            },
            "loops": {
                "explanation": "Loops (`for` and `while`) are used to repeat a block of code multiple times, helping you avoid writing repetitive code.",
                "plan": "1. Understand the difference between `for` loops (known number of iterations) and `while` loops (condition-based).\n2. Practice iterating over a range using `range()`.\n3. Learn to iterate over lists or strings.",
                "task": "Write a loop that prints the square of numbers from 1 to 5.",
                "next": "lists"
            },
            "lists": {
                "explanation": "Lists are ordered, mutable collections of items, allowing you to store multiple values in a single variable.",
                "plan": "1. Create lists and access elements using 0-based indices.\n2. Add/remove items using `.append()`, `.insert()`, and `.remove()`.\n3. Learn list slicing and common functions like `len()`.",
                "task": "Create a list of 5 favorite fruits, add a new one, remove the second one, and print the final list.",
                "next": "dictionaries"
            },
            "dictionaries": {
                "explanation": "Dictionaries store data in key-value pairs, allowing you to retrieve values quickly using their corresponding keys.",
                "plan": "1. Create a dictionary and access values using keys.\n2. Add, update, and delete key-value pairs.\n3. Practice looping through keys and values.",
                "task": "Create a dictionary for a book with keys: 'title', 'author', and 'year'. Change the year and print the updated dictionary.",
                "next": "functions"
            },
            "functions": {
                "explanation": "Functions are reusable blocks of code that perform a specific task, helping to make programs organized and modular.",
                "plan": "1. Define a function using `def` and call it.\n2. Pass arguments/parameters to a function.\n3. Return values from a function using the `return` statement.",
                "task": "Write a function `calculate_area(width, height)` that returns the area of a rectangle.",
                "next": "classes"
            },
            "classes": {
                "explanation": "Classes are templates for creating objects. They bundle data (attributes) and behavior (methods) together in Object-Oriented Programming (OOP).",
                "plan": "1. Understand classes and objects.\n2. Write a class definition and use the `__init__` constructor.\n3. Create class methods and access attributes.",
                "task": "Create a `Car` class with attributes `make` and `model`, and a method `drive()` that prints a message.",
                "next": "Object-Oriented Programming (OOP) & Advanced Data Structures"
            },
            "general": {
                "explanation": "General Python Programming covers setting up your workspace, learning basic syntax, and building your first command-line scripts.",
                "plan": "1. Learn how to install Python and configure a code editor.\n2. Master variables, basic types, and input/output.\n3. Explore control structures like conditionals and loops.",
                "task": "Write a short program that asks for the user's name and favorite programming language, then prints a personalized greeting.",
                "next": "variables"
            }
        }
        
        info = plans.get(matched_topic, plans["general"])
        
        response = f"""### Study Plan: {matched_topic.title()} (Offline Fallback)

**Topic Explanation:**
{info["explanation"]}

**Step-by-Step Study/Revision Plan:**
{info["plan"]}

**Practice Task:**
{info["task"]}

**Next Recommended Topic:**
{info["next"]}
"""
        return response

    def generate_plan(self, request: str) -> str:
        """Generates a study plan based on the student's request."""
        self.fallback_active = False
        if not self.client:
            self.fallback_active = True
            return self._generate_offline_plan(request)

        try:
            instructions = load_skill("study_planner")

            prompt = f"""
            You are a Study Planner Agent for programming and data science students.
            
            Skill Guidelines:
            {instructions}
            
            Please handle the following request from a student:
            "{request}"
            
            Return the output in a clear, friendly, and structured Markdown format including:
            - A short explanation of the topic
            - A step-by-step study/revision plan
            - A realistic practice task
            - The next recommended topic
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "temperature": 0.4
                }
            )
            return response.text

        except Exception:
            self.fallback_active = True
            return self._generate_offline_plan(request)
