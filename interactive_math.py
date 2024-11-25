import asyncio
import sys
import os
import time

# Add the src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from crews.crew import MathTutorCrew

async def run_interactive_explanation(prompt):
    # Initialize the math tutor crew
    math_crew = MathTutorCrew()
    
    # Format the input correctly
    inputs = {
        'user_query': prompt
    }
    
    # Get the explanation steps
    result = await math_crew.crew().kickoff_async(inputs=inputs)
    
    try:
        # Access the Pydantic model from the result
        explanation = result.pydantic
        
        # Display the problem
        print("\nProblem:", explanation.problem)
        print("\nLet's solve this step by step...")
        
        # Display each step
        for i, step in enumerate(explanation.steps, 1):
            print(f"\nStep {i}:")
            print("Explanation:", step.natural)
            if step.math:  # Only print math if it's not empty
                print("Math:", step.math)
            
            # Wait for user input before continuing
            input("\nPress Enter to continue...")
            time.sleep(0.5)  # Small delay between steps
            
    except Exception as e:
        print("Error processing result:", str(e))
        print("Result type:", type(result))
        print("Result content:", result)

if __name__ == "__main__":
    print("Interactive Math Explanation")
    print("---------------------------")
    prompt = input("Enter your math question: ")
    asyncio.run(run_interactive_explanation(prompt))
