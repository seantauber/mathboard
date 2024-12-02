import re
from typing import Optional, List, Dict, Tuple
from xml.etree import ElementTree as ET

# ===== MathML Functions =====

def validate_mathml(expression: str) -> bool:
    """Validate MathML expression for basic syntax."""
    try:
        # Try parsing as XML
        root = ET.fromstring(expression)
        
        # Check if root element is 'math'
        if root.tag != 'math':
            return False
            
        # Validate required attributes
        if 'xmlns' not in root.attrib:
            root.set('xmlns', 'http://www.w3.org/1998/Math/MathML')
            
        return True
    except ET.ParseError:
        return False

def sanitize_mathml(expression: str) -> str:
    """Sanitize MathML expression for safety."""
    dangerous_elements = [
        'annotation', 'annotation-xml', 'maction', 'semantics'
    ]
    
    try:
        root = ET.fromstring(expression)
        
        # Remove dangerous elements
        for element in root.iter():
            if element.tag in dangerous_elements:
                root.remove(element)
                
        # Remove script-like attributes
        for element in root.iter():
            for attr in list(element.attrib):
                if attr.startswith('on') or 'script' in attr.lower():
                    del element.attrib[attr]
                    
        return ET.tostring(root, encoding='unicode')
    except ET.ParseError:
        return expression

def format_mathml(expression: str) -> str:
    """Format MathML expression for display."""
    if not expression.strip().startswith('<math'):
        expression = f'<math xmlns="http://www.w3.org/1998/Math/MathML">{expression}</math>'
    return expression

def latex_to_mathml(latex: str) -> str:
    """Convert LaTeX expression to MathML."""
    # Basic conversion patterns
    patterns = {
        # Fractions
        r'\\frac\{([^}]*)\}\{([^}]*)\}': lambda m: f'<mfrac><mrow>{latex_to_mathml(m.group(1))}</mrow><mrow>{latex_to_mathml(m.group(2))}</mrow></mfrac>',
        
        # Square root
        r'\\sqrt\{([^}]*)\}': lambda m: f'<msqrt>{latex_to_mathml(m.group(1))}</msqrt>',
        
        # Superscript
        r'\^{([^}]*)}': lambda m: f'<msup><mrow>{latex_to_mathml(m.group(1))}</mrow></msup>',
        
        # Subscript
        r'_\{([^}]*)\}': lambda m: f'<msub><mrow>{latex_to_mathml(m.group(1))}</mrow></msub>',
        
        # Greek letters
        r'\\alpha': '<mi>α</mi>',
        r'\\beta': '<mi>β</mi>',
        r'\\gamma': '<mi>γ</mi>',
        r'\\theta': '<mi>θ</mi>',
        r'\\pi': '<mi>π</mi>',
        
        # Operators
        r'\\sum': '<mo>∑</mo>',
        r'\\int': '<mo>∫</mo>',
        r'\\infty': '<mi>∞</mi>',
        
        # Basic operators
        r'\+': '<mo>+</mo>',
        r'-': '<mo>-</mo>',
        r'\*': '<mo>×</mo>',
        r'/': '<mo>÷</mo>',
        r'=': '<mo>=</mo>'
    }
    
    result = latex.strip()
    # Remove display math delimiters
    result = result.replace('$$', '').replace('$', '')
    
    # Apply conversions
    for pattern, replacement in patterns.items():
        if callable(replacement):
            result = re.sub(pattern, replacement, result)
        else:
            result = re.sub(pattern, replacement, result)
    
    # Wrap numbers in <mn> tags
    result = re.sub(r'(\d+)', r'<mn>\1</mn>', result)
    
    # Wrap variables in <mi> tags
    result = re.sub(r'([a-zA-Z])', r'<mi>\1</mi>', result)
    
    return format_mathml(result)

def fix_common_mathml_issues(mathml: str) -> str:
    """Fix common MathML syntax issues."""
    try:
        root = ET.fromstring(mathml)
        
        # Ensure proper nesting of mrow elements
        for element in root.iter():
            if len(element) > 1 and element.tag != 'mrow':
                children = list(element)
                mrow = ET.Element('mrow')
                for child in children:
                    element.remove(child)
                    mrow.append(child)
                element.append(mrow)
        
        # Add missing xmlns attribute
        if 'xmlns' not in root.attrib:
            root.set('xmlns', 'http://www.w3.org/1998/Math/MathML')
        
        return ET.tostring(root, encoding='unicode')
    except ET.ParseError:
        return mathml

def natural_text_to_mathml(text: str) -> str:
    """Convert natural language math expressions to MathML."""
    # First convert to LaTeX as an intermediate step
    latex = natural_text_to_latex(text)
    # Then convert LaTeX to MathML
    return latex_to_mathml(latex)

def parse_mathml_errors(error_log: str) -> List[Dict[str, str]]:
    """Parse MathML errors into structured format."""
    errors = []
    error_patterns = [
        (r'Invalid tag: (\w+)', 'invalid_tag'),
        (r'Missing required attribute: (\w+)', 'missing_attribute'),
        (r'Invalid attribute value: (\w+)', 'invalid_attribute'),
        (r'Malformed XML', 'malformed_xml')
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

def get_mathml_preview(expression: str, max_length: Optional[int] = None) -> str:
    """Generate a preview of MathML expression."""
    if not expression:
        return ''
    
    # Truncate if needed while maintaining valid XML
    if max_length and len(expression) > max_length:
        try:
            root = ET.fromstring(expression)
            preview = ET.tostring(root, encoding='unicode')[:max_length] + '...'
        except ET.ParseError:
            preview = expression[:max_length] + '...'
    else:
        preview = expression
    
    return format_mathml(preview)

# ===== Legacy LaTeX Functions =====

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
