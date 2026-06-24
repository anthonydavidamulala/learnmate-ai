import sys
from agents.orchestrator import Orchestrator

def main():
    print("=" * 60)
    print("Welcome to LearnMate AI - Your Multi-Agent Study & Coding Coach!")
    print("=" * 60)
    print("Type your questions, request quizzes, debug code, or track progress.")
    print("Type 'exit' or 'quit' to close the app.")
    print("-" * 60)

    orchestrator = Orchestrator()

    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input.strip():
                continue
                
            if user_input.strip().lower() in ["exit", "quit"]:
                print("Thank you for learning with LearnMate AI! Keep coding! 🚀")
                break
                
            print("\nProcessing request with specialized agents...")
            agent_name, response = orchestrator.route_request(user_input)
            
            print(f"\n[Agent: {agent_name.upper()}]")
            print(response)
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()
