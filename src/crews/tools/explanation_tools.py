from langchain.tools import BaseTool
from ...utils.latex_utils import validate_latex, sanitize_latex
from pydantic import BaseModel, Field
import re
from typing import List, Optional

class ExplanationValidatorSchema(BaseModel):
    explanation: str = Field(..., description="The mathematical explanation to validate")

class ExplanationValidator(BaseTool):
    name = "explanation_validator"
    description = "Validates mathematical explanations for clarity and educational value"
    args_schema: type[BaseModel] = ExplanationValidatorSchema

    def _run(self, explanation: str) -> str:
        """
        Validate and improve mathematical explanations.
        Args:
            explanation (str): The mathematical explanation to validate
        Returns:
            str: Improved explanation or original if no improvements needed
        """
        try:
            # First check and sanitize any LaTeX in the explanation
            explanation = self._process_latex_in_explanation(explanation)
            
            improvements = []
            
            # Check for structural elements
            if not self._has_introduction(explanation):
                improvements.append(self._add_introduction(explanation))
            
            if not self._has_step_by_step(explanation):
                improvements.append(self._add_step_structure(explanation))
                
            if not self._has_conclusion(explanation):
                improvements.append(self._add_conclusion(explanation))
                
            # If no improvements needed, return original
            if not improvements:
                return explanation
                
            # Merge improvements
            return self._merge_improvements(explanation, improvements)
            
        except Exception as e:
            return f"Error validating explanation: {str(e)}"

    def _process_latex_in_explanation(self, text: str) -> str:
        """Find and validate any LaTeX expressions in the explanation."""
        # Find all LaTeX expressions (between $$ pairs)
        latex_pattern = r'\$\$(.*?)\$\$'
        
        def replace_latex(match):
            latex = match.group(1)
            if validate_latex(latex):
                return f"$${sanitize_latex(latex)}$$"
            return f"$$\\text{{Invalid LaTeX: }}{latex}$$"
        
        return re.sub(latex_pattern, replace_latex, text)

    def _has_introduction(self, text: str) -> bool:
        """Check if the explanation has a proper introduction."""
        intro_patterns = [
            r'^(First|Let\'s|We will|To understand|Let us)',
            r'^(This|The|Here)',
            r'^(Consider|Looking at|When we)'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in intro_patterns)

    def _has_step_by_step(self, text: str) -> bool:
        """Check if the explanation has a step-by-step structure."""
        step_patterns = [
            r'(First|1st|Step 1)',
            r'(Second|2nd|Step 2)',
            r'(Finally|Lastly|In conclusion)'
        ]
        
        # Count how many step patterns we find
        step_count = sum(1 for pattern in step_patterns 
                        if re.search(pattern, text, re.IGNORECASE))
        
        # Consider it step-by-step if we find at least 2 step indicators
        return step_count >= 2

    def _has_conclusion(self, text: str) -> bool:
        """Check if the explanation has a conclusion."""
        conclusion_patterns = [
            r'(Therefore|Thus|Hence)',
            r'(In conclusion|To summarize|Finally)',
            r'(This shows|This proves|This demonstrates)'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) 
                  for pattern in conclusion_patterns)

    def _add_introduction(self, text: str) -> str:
        """Add an introduction if missing."""
        if not text.strip():
            return text
            
        intro_templates = [
            "Let's understand this step by step. ",
            "Let's examine this mathematical concept. ",
            "Here's how we can understand this: "
        ]
        
        # Select template based on content
        selected_intro = intro_templates[0]  # Default
        return selected_intro + text

    def _add_step_structure(self, text: str) -> str:
        """Add step structure if missing."""
        if not text.strip():
            return text
            
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if len(sentences) < 2:
            return text
            
        # Add step markers
        structured_text = "First, " + sentences[0] + " "
        
        for i, sentence in enumerate(sentences[1:-1], 1):
            if i == len(sentences) - 2:
                structured_text += "Finally, " + sentence + " "
            else:
                structured_text += f"Next, {sentence} "
                
        if sentences[-1]:
            structured_text += sentences[-1]
            
        return structured_text

    def _add_conclusion(self, text: str) -> str:
        """Add a conclusion if missing."""
        if not text.strip():
            return text
            
        conclusion_templates = [
            " Therefore, we can conclude that ",
            " Thus, we can see that ",
            " This demonstrates that "
        ]
        
        # Select template based on content
        selected_conclusion = conclusion_templates[0]  # Default
        
        # Extract the main result from the text (simplified)
        last_sentence = text.split('.')[-2] if len(text.split('.')) > 1 else text
        
        return text + selected_conclusion + last_sentence + "."

    def _merge_improvements(self, original: str, improvements: List[str]) -> str:
        """Merge improvements with the original text."""
        # Start with the best improvement (usually the one with introduction)
        best_improvement = max(improvements, key=len, default=original)
        
        # If the improvement is significantly different, use it
        if len(best_improvement) > len(original) * 1.2:
            return best_improvement
            
        return original
