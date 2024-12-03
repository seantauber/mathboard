from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests

from ...utils.math_utils import fix_common_mathml_issues

class MathMLValidatorInput(BaseModel):
    mathml_code: str = Field(..., description="A string containing the MathML code to validate.")

class MathMLValidatorTool(BaseTool):
    name: str = "MathML Validator"
    description: str = "Validates MathML code and provides feedback on its validity and any errors found."
    args_schema: Type[BaseModel] = MathMLValidatorInput

    def _run(self, mathml_code: str) -> str:
        # Prepare the MathML code for validation
        xhtml_wrapper = f"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1 plus MathML 2.0//EN" "http://www.w3.org/TR/MathML2/dtd/xhtml-math11-f.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <title>MathML Validation</title>
            <meta http-equiv="content-type" content="mathml" />
        </head>
        <body>
            {mathml_code}
        </body>
        </html>
        """

        # Send the code to the W3C Validator
        validator_url = "https://validator.w3.org/check"
        headers = {'Content-Type': 'text/html; charset=UTF-8'}
        response = requests.post(validator_url, data=xhtml_wrapper.encode('utf-8'), headers=headers)

        # Process the validation results
        if "Valid" in response.text:
            return "The MathML code is valid."
        else:
            # Extract and format error messages
            error_start = response.text.find("List of Errors")
            error_end = response.text.find("</ol>", error_start)
            error_list = response.text[error_start:error_end]
            
            # Remove HTML tags and format the error messages
            import re
            errors = re.findall(r'<li class="error">(.*?)</li>', error_list, re.DOTALL)
            formatted_errors = "\n".join([f"- {error.strip()}" for error in errors])

            return f"The MathML code is invalid. Errors found:\n{formatted_errors}"


    async def _arun(self, mathml_code: str) -> str:
        """
        Async implementation - in this case just calls the sync version
        """
        return self._run(mathml_code)


    # Example usage in a CrewAI task:
    """
    from src.crews.tools.mathml_validator_tool import MathMLValidatorTool

    # Create the validator tool
    mathml_validator = MathMLValidatorTool()

    # Create an agent that uses the MathML validator tool
    agent = Agent(
        role="Math Expert",
        goal="Generate and validate mathematical expressions",
        backstory="You are an expert in mathematics who ensures all mathematical expressions are properly formatted.",
        tools=[mathml_validator]
    )

    # Create a task for the agent
    task = Task(
        description="Generate and validate the following mathematical expression...",
        agent=agent
    )

    # The agent can now use the validator tool during its execution
    """
