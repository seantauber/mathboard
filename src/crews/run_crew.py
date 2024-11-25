#!/usr/bin/env python
import sys
import os

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.crews.crew import MathTutorCrew

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run(topic):
    """
    Run the crew.
    Args:
        topic (str): The topic to explain
    """
    inputs = {
        'user_query': topic  # Changed from 'topic' to 'user_query' to match tasks.yaml
    }
    MathTutorCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "user_query": "AI LLMs"  # Changed from 'topic' to 'user_query'
    }
    try:
        MathTutorCrew().crew().train(
            n_iterations=int(sys.argv[1]), 
            filename=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MathTutorCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "user_query": "AI LLMs"  # Changed from 'topic' to 'user_query'
    }
    try:
        MathTutorCrew().crew().test(
            n_iterations=int(sys.argv[1]), 
            openai_model_name=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_crew.py <command> [args...]")
        print("Commands:")
        print("  run <topic>      - Run the crew with specified topic")
        print("  train <n> <file> - Train the crew for n iterations")
        print("  replay <task_id> - Replay a specific task")
        print("  test <n> <model> - Test the crew with model for n iterations")
        sys.exit(1)

    command = sys.argv[1]
    sys.argv = sys.argv[1:]  # Shift arguments for the command functions

    if command == "run":
        if len(sys.argv) < 2:
            print("Usage: python run_crew.py run <topic>")
            sys.exit(1)
        run(sys.argv[1])
    elif command == "train":
        if len(sys.argv) < 3:
            print("Usage: python run_crew.py train <n_iterations> <filename>")
            sys.exit(1)
        train()
    elif command == "replay":
        if len(sys.argv) < 2:
            print("Usage: python run_crew.py replay <task_id>")
            sys.exit(1)
        replay()
    elif command == "test":
        if len(sys.argv) < 3:
            print("Usage: python run_crew.py test <n_iterations> <model_name>")
            sys.exit(1)
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
