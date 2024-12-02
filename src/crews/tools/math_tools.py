from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...utils.math_utils import (
    validate_mathml,
    sanitize_mathml,
    fix_common_mathml_issues,
    natural_text_to_mathml,
    parse_mathml_errors,
    latex_to_mathml,
    # Legacy LaTeX functions for transition period
    validate_latex,
    sanitize_latex,
    fix_common_latex_issues,
    natural_text_to_latex
)

# MathML Schemas
class MathMLFormatterSchema(BaseModel):
    text: str = Field(..., description="The text containing MathML expressions to format")

class MathMLGeneratorSchema(BaseModel):
    query: str = Field(..., description="The mathematical concept to convert to MathML")

class MathMLValidatorSchema(BaseModel):
    mathml: str = Field(..., description="The MathML expression to validate")

class MathMLConverterSchema(BaseModel):
    latex: str = Field(..., description="The LaTeX expression to convert to MathML")

# MathML Tools
class MathMLFormatter(BaseTool):
    name: str = "mathml_formatter"
    description: str = "Formats and validates MathML expressions"
    args_schema: type[BaseModel] = MathMLFormatterSchema

    def _run(self, text: str) -> str:
        """Format and validate MathML expressions in text."""
        try:
            # Sanitize the input
            mathml = sanitize_mathml(text)
            # Fix any common issues
            mathml = fix_common_mathml_issues(mathml)
            # Validate the result
            if not validate_mathml(mathml):
                return text  # Return original if validation fails
            return mathml
        except Exception as e:
            return text  # Return original on error

class MathMLGenerator(BaseTool):
    name: str = "mathml_generator"
    description: str = "Generates MathML code for mathematical expressions"
    args_schema: type[BaseModel] = MathMLGeneratorSchema

    def _run(self, query: str) -> str:
        """Convert mathematical concepts into MathML notation."""
        try:
            # Convert natural language to MathML
            mathml = natural_text_to_mathml(query)
            # Sanitize the output
            mathml = sanitize_mathml(mathml)
            # Fix any common issues
            mathml = fix_common_mathml_issues(mathml)
            return mathml
        except Exception as e:
            return f"Error generating MathML: {str(e)}"

class MathMLValidator(BaseTool):
    name: str = "mathml_validator"
    description: str = "Validates and improves MathML expressions"
    args_schema: type[BaseModel] = MathMLValidatorSchema

    def _run(self, mathml: str) -> str:
        """
        Validate and improve MathML syntax.
        Returns the improved MathML or error message.
        """
        try:
            # First sanitize
            mathml = sanitize_mathml(mathml)
            
            # Validate
            if not validate_mathml(mathml):
                # Try to fix common issues
                mathml = fix_common_mathml_issues(mathml)
                
                # Validate again after fixes
                if not validate_mathml(mathml):
                    errors = parse_mathml_errors(mathml)
                    error_msg = "; ".join([e["message"] for e in errors])
                    return f"Invalid MathML expression that couldn't be automatically fixed: {error_msg}"
            
            return mathml
        except Exception as e:
            return f"Error validating MathML: {str(e)}"

class LaTeXToMathMLConverter(BaseTool):
    name: str = "latex_to_mathml_converter"
    description: str = "Converts LaTeX expressions to MathML"
    args_schema: type[BaseModel] = MathMLConverterSchema

    def _run(self, latex: str) -> str:
        """Convert LaTeX expression to MathML."""
        try:
            # First validate and sanitize the LaTeX
            latex = sanitize_latex(latex)
            if not validate_latex(latex):
                latex = fix_common_latex_issues(latex)
                if not validate_latex(latex):
                    return "Invalid LaTeX expression that couldn't be converted"
            
            # Convert to MathML
            mathml = latex_to_mathml(latex)
            
            # Validate the resulting MathML
            if not validate_mathml(mathml):
                mathml = fix_common_mathml_issues(mathml)
                if not validate_mathml(mathml):
                    return "Conversion resulted in invalid MathML"
            
            return mathml
        except Exception as e:
            return f"Error converting LaTeX to MathML: {str(e)}"
