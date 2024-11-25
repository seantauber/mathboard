import asyncio
from flask_socketio import SocketIO
import time
import sys
import os

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.crews.crew import MathTutorCrew

async def run_interactive_explanation(prompt):
    # Initialize the math tutor crew
    math_crew = MathTutorCrew()
    
    # Format the input correctly
    inputs = {
        'user_query': prompt
    }
    
    # Get the explanation steps
    result = await math_crew.crew().kickoff(inputs=inputs)
    if not result or 'steps' not in result:
        print("Error: Could not get steps from the crew")
        return
    
    steps = result['steps']
    
    # Connect to the Flask-SocketIO server
    socketio = SocketIO(message_queue='redis://')
    
    # Display each step
    for i, step in enumerate(steps, 1):
        # Print the natural language explanation
        print(f"\nStep {i}:")
        print(step['natural'])
        
        # Send the LaTeX to the frontend
        socketio.emit('math_step', {
            'latex': step['math']
        })
        
        # Wait for user input before continuing
        input("\nPress Enter to continue...")
        time.sleep(0.5)  # Small delay to ensure frontend updates

if __name__ == "__main__":
    print("Interactive Math Explanation")
    print("---------------------------")
    prompt = input("Enter your math question: ")
    asyncio.run(run_interactive_explanation(prompt))
