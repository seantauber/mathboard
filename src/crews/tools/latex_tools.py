from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...utils.latex_utils import (
    validate_latex,
    sanitize_latex,
    fix_common_latex_issues,
    natural_text_to_latex,
    parse_latex_errors
)

class LatexFormatterSchema(BaseModel):
    text: str = Field(..., description="The text containing LaTeX expressions to format")

class LatexGeneratorSchema(BaseModel):
    query: str = Field(..., description="The mathematical concept to convert to LaTeX")

class LatexValidatorSchema(BaseModel):
    latex: str = Field(..., description="The LaTeX expression to validate")

class LatexFormatter(BaseTool):
    name: str = "latex_formatter"
    description: str = "Formats and validates LaTeX expressions"
    args_schema: type[BaseModel] = LatexFormatterSchema

    def _run(self, text: str) -> str:
        """Format and validate LaTeX expressions in text."""
        try:
            # Sanitize the input
            latex = sanitize_latex(text)
            # Fix any common issues
            latex = fix_common_latex_issues(latex)
            # Validate the result
            if not validate_latex(latex):
                return text  # Return original if validation fails
            return latex
        except Exception as e:
            return text  # Return original on error

class LatexGenerator(BaseTool):
    name: str = "latex_generator"
    description: str = "Generates LaTeX code for mathematical expressions"
    args_schema: type[BaseModel] = LatexGeneratorSchema

    def _run(self, query: str) -> str:
        """Convert mathematical concepts into LaTeX notation."""
        try:
            # Convert natural language to LaTeX
            latex = natural_text_to_latex(query)
            # Sanitize the output
            latex = sanitize_latex(latex)
            # Fix any common issues
            latex = fix_common_latex_issues(latex)
            return latex
        except Exception as e:
            return f"Error generating LaTeX: {str(e)}"

class LatexValidator(BaseTool):
    name: str = "latex_validator"
    description: str = "Validates and improves LaTeX expressions"
    args_schema: type[BaseModel] = LatexValidatorSchema

    def _run(self, latex: str) -> str:
        """
        Validate and improve LaTeX syntax.
        Returns the improved LaTeX or error message.
        """
        try:
            # First sanitize
            latex = sanitize_latex(latex)
            
            # Validate
            if not validate_latex(latex):
                # Try to fix common issues
                latex = fix_common_latex_issues(latex)
                
                # Validate again after fixes
                if not validate_latex(latex):
                    return "Invalid LaTeX expression that couldn't be automatically fixed"
            
            return latex
        except Exception as e:
            return f"Error validating LaTeX: {str(e)}"
