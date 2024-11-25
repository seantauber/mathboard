import re
from typing import Optional, List, Dict, Tuple

def validate_latex(expression: str) -> bool:
    """Validate LaTeX expression for basic syntax."""
    delimiters = {
        '{': '}',
        '[': ']',
        '(': ')',
        r'\left': r'\right'
    }
    
    # Check all delimiter pairs
    for opening, closing in delimiters.items():
        if expression.count(opening) != expression.count(closing):
            return False
            
    # Check proper nesting with stack
    stack = []
    simple_delimiters = {'{': '}', '[': ']', '(': ')'}
    
    for char in expression:
        if char in simple_delimiters:
            stack.append(char)
        elif char in simple_delimiters.values():
            if not stack or char != simple_delimiters[stack.pop()]:
                return False
    
    return len(stack) == 0

def sanitize_latex(expression: str) -> str:
    """Sanitize LaTeX expression for safety."""
    dangerous_commands = [
        r'\\input', r'\\include', r'\\write', r'\\read',
        r'\\openout', r'\\closeout', r'\\load', r'\\output'
    ]
    
    sanitized = expression
    for cmd in dangerous_commands:
        sanitized = re.sub(cmd + r'\{.*?\}', '', sanitized)
    
    return sanitized

def format_latex(expression: str) -> str:
    """Format LaTeX expression for display."""
    if not expression.strip().startswith('$$'):
        expression = f'$${expression}$$'
    return expression

def fix_common_latex_issues(latex: str) -> str:
    """Fix common LaTeX syntax issues."""
    fixes = [
        (r'([0-9]) *([a-zA-Z])', r'\1\cdot\2'),  # Add multiplication dot
        (r'\\frac([^{])', r'\\frac{\1}'),        # Fix fractions without braces
        (r'([^\\])(sqrt)', r'\1\\sqrt'),         # Fix sqrt without backslash
        (r'([^_\^])\d+', r'\1{\2}'),            # Add braces to numbers
        (r'([^\\])(sum|int|prod)', r'\1\\\2'),   # Fix missing backslashes
        (r'\\([a-zA-Z]+)([^{])', r'\\\1{\2}')    # Add missing braces to commands
    ]
    
    result = latex
    for pattern, replacement in fixes:
        result = re.sub(pattern, replacement, result)
    
    return result

def natural_text_to_latex(text: str) -> str:
    """Convert natural language math expressions to LaTeX."""
    math_patterns: Dict[str, str] = {
        r'square root of ([^:]+)': r'\\sqrt{\1}',
        r'fraction (\w+)/(\w+)': r'\\frac{\1}{\2}',
        r'sum from ([^:]+) to ([^:]+)': r'\\sum_{\1}^{\2}',
        r'integral from ([^:]+) to ([^:]+)': r'\\int_{\1}^{\2}',
        r'infinity': r'\\infty',
        r'alpha': r'\\alpha',
        r'beta': r'\\beta',
        r'pi': r'\\pi',
        r'theta': r'\\theta',
        r'([0-9]+)th power': r'^{\1}',
        r'subscript ([0-9]+)': r'_{\1}'
    }
    
    result = text
    for pattern, replacement in math_patterns.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result

def parse_latex_errors(error_log: str) -> List[Dict[str, str]]:
    """Parse LaTeX compilation errors into structured format."""
    errors = []
    error_patterns = [
        (r'! Missing (\w+) inserted', 'missing_delimiter'),
        (r'! Undefined control sequence', 'undefined_command'),
        (r'! Missing \$ inserted', 'missing_math_mode'),
        (r'! Extra \}', 'extra_brace'),
        (r'! Missing \} inserted', 'missing_brace')
    ]
    
    for line in error_log.split('\n'):
        for pattern, error_type in error_patterns:
            match = re.search(pattern, line)
            if match:
                errors.append({
                    'type': error_type,
                    'message': line.strip(),
                    'details': match.group(1) if match.groups() else None
                })
    
    return errors

def get_latex_preview(expression: str, max_length: Optional[int] = None) -> str:
    """Generate a preview of LaTeX expression."""
    if not expression:
        return ''
    
    # Truncate if needed
    if max_length and len(expression) > max_length:
        preview = expression[:max_length] + '...'
    else:
        preview = expression
    
    return format_latex(preview)