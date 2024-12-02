"""
Backend MathML generation test script.
Tests the CrewAI agent's ability to generate valid MathML output.
Saves results to a file for manual inspection.
"""
import os
import sys
import json
from datetime import datetime

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.crews.crew import MathTutorCrew
from src.models.math_models import MathExplanation

# Test queries covering different mathematical concepts
TEST_QUERIES = [
    "How do you add fractions?"
    # "Explain the quadratic formula",
    # "What is the Pythagorean theorem?",
    # "How do you solve a system of linear equations?",
    # "Explain the concept of square roots",
    # "How do you factor quadratic expressions?",
    # "What are the laws of exponents?"
]

def run_generation_tests():
    # Create output directory if it doesn't exist
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Initialize the teaching crew
    math_tutor = MathTutorCrew()
    crew = math_tutor.crew()
    
    # Store all test results
    test_results = {}
    
    print("Starting MathML generation tests...")
    print(f"Results will be saved to: {output_dir}/")
    
    # Run tests for each query
    for query in TEST_QUERIES:
        print(f"\nTesting query: {query}")
        try:
            result: MathExplanation = crew.kickoff(inputs={'user_query': query})

            # Create output file for this test run
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"{timestamp}_{query.replace(" ", "_")}.json")

            # Save results to file
            print(f"Saving result to {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.pydantic.model_dump_json(indent=2))
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")

def main():
    run_generation_tests()

if __name__ == '__main__':
    main()

from src.models.math_models import MathExplanation
