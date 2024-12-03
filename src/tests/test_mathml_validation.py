"""
Test suite for MathML validation functionality.
Tests the enhanced validation features including DTD validation and error reporting.
"""
import pytest
from src.utils.math_utils import validate_mathml, fix_common_mathml_issues, parse_mathml_errors

# Test cases for valid MathML
VALID_MATHML_CASES = [
    # Basic expression
    '<math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mi>x</mi><mo>+</mo><mn>1</mn></mrow></math>',
    # Fraction
    '<math xmlns="http://www.w3.org/1998/Math/MathML"><mfrac><mrow><mn>1</mn></mrow><mrow><mn>2</mn></mrow></mfrac></math>',
    # Square root
    '<math xmlns="http://www.w3.org/1998/Math/MathML"><msqrt><mrow><mn>2</mn></mrow></msqrt></math>',
]

# Test cases for invalid MathML
INVALID_MATHML_CASES = [
    # Missing xmlns attribute
    ('<math><mi>x</mi></math>', 'xmlns'),
    # Missing mrow in fraction
    ('<math xmlns="http://www.w3.org/1998/Math/MathML"><mfrac><mn>1</mn><mn>2</mn></mfrac></math>', 'mrow'),
    # Invalid tag
    ('<math xmlns="http://www.w3.org/1998/Math/MathML"><invalid>x</invalid></math>', 'invalid tag'),
    # Malformed XML
    ('<math xmlns="http://www.w3.org/1998/Math/MathML"><mrow>x</mrow', 'malformed'),
]

# Test cases for fixable MathML
FIXABLE_MATHML_CASES = [
    # Missing mrow in fraction - should be fixed
    (
        '<math xmlns="http://www.w3.org/1998/Math/MathML"><mfrac><mn>1</mn><mn>2</mn></mfrac></math>',
        '<math xmlns="http://www.w3.org/1998/Math/MathML"><mfrac><mrow><mn>1</mn></mrow><mrow><mn>2</mn></mrow></mfrac></math>'
    ),
    # Missing xmlns - should be added
    (
        '<math><mi>x</mi></math>',
        '<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>x</mi></math>'
    ),
]

def test_valid_mathml():
    """Test validation of valid MathML expressions."""
    for mathml in VALID_MATHML_CASES:
        is_valid, error_msg = validate_mathml(mathml)
        assert is_valid, f"Expected valid MathML, but got error: {error_msg}"
        assert error_msg is None, "Expected no error message for valid MathML"

def test_invalid_mathml():
    """Test validation of invalid MathML expressions."""
    for mathml, expected_error in INVALID_MATHML_CASES:
        is_valid, error_msg = validate_mathml(mathml)
        assert not is_valid, f"Expected invalid MathML for case containing '{expected_error}'"
        assert error_msg is not None, "Expected error message for invalid MathML"
        assert expected_error.lower() in error_msg.lower(), f"Expected error message to contain '{expected_error}'"

def test_fixable_mathml():
    """Test fixing common MathML issues."""
    for input_mathml, expected_output in FIXABLE_MATHML_CASES:
        fixed_mathml = fix_common_mathml_issues(input_mathml)
        is_valid, error_msg = validate_mathml(fixed_mathml)
        assert is_valid, f"Expected fixed MathML to be valid, but got error: {error_msg}"
        # Normalize whitespace for comparison
        fixed_normalized = ' '.join(fixed_mathml.split())
        expected_normalized = ' '.join(expected_output.split())
        assert fixed_normalized == expected_normalized, "Fixed MathML doesn't match expected output"

def test_error_parsing():
    """Test parsing of MathML validation errors."""
    for mathml, _ in INVALID_MATHML_CASES:
        errors = parse_mathml_errors(mathml)
        assert len(errors) > 0, "Expected at least one error for invalid MathML"
        for error in errors:
            assert 'line' in error, "Expected error to contain line number"
            assert 'message' in error, "Expected error to contain message"
            assert 'type' in error, "Expected error to contain type"

def test_validation_error_details():
    """Test that validation errors provide useful details."""
    mathml = '<math xmlns="http://www.w3.org/1998/Math/MathML"><mfrac><mn>1</mn></mfrac></math>'
    is_valid, error_msg = validate_mathml(mathml)
    assert not is_valid, "Expected invalid MathML"
    assert error_msg is not None, "Expected error message"
    assert 'line' in error_msg.lower(), "Expected error message to contain line number"
    
    errors = parse_mathml_errors(mathml)
    assert len(errors) > 0, "Expected detailed error information"
    assert all('line' in error for error in errors), "Expected all errors to have line numbers"
    assert all('message' in error for error in errors), "Expected all errors to have messages"
