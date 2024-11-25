from typing import List
from pydantic import BaseModel, Field


class Step(BaseModel):
    """A single step in a mathematical explanation."""
    natural: str = Field(
        description="Text-to-speech friendly explanation of the mathematical step"
    )
    math: str = Field(
        description="LaTeX formatted mathematical notation"
    )


class MathExplanation(BaseModel):
    """Complete mathematical explanation with steps."""
    problem: str = Field(
        description="Original problem statement"
    )
    steps: List[Step] = Field(
        description="Sequence of explanation steps"
    )


class ValidatedInput(BaseModel):
    """Result of validating a mathematical input expression."""
    original: str = Field(
        description="Original input expression"
    )
    normalized: str = Field(
        description="Normalized form of the expression"
    )
    is_valid: bool = Field(
        description="Whether the input is valid"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="List of validation errors if any"
    )


class ValidatedLatex(BaseModel):
    """Result of validating and improving LaTeX notation."""
    original: str = Field(
        description="Original LaTeX"
    )
    improved: str = Field(
        description="Improved LaTeX"
    )
    changes: List[str] = Field(
        default_factory=list,
        description="List of improvements made"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Potential issues to review"
    )


class ValidatedText(BaseModel):
    """Result of validating and improving natural language explanations."""
    original: str = Field(
        description="Original explanation"
    )
    improved: str = Field(
        description="Improved explanation"
    )
    readability_score: float = Field(
        description="Text-to-speech suitability score (0-1)"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Improvement suggestions"
    )
