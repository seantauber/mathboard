from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from src.crews.crew import MathTutorCrew
import asyncio
from dotenv import load_dotenv
from functools import partial
import warnings
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Filter out the TracerProvider warning
warnings.filterwarnings('ignore', category=RuntimeWarning, 
                      message='Overriding of current TracerProvider is not allowed')

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize the math teaching crew
math_crew = MathTutorCrew()

def format_latex(latex):
    r"""
    Format LaTeX content for proper display in MathJax.
    
    This function serves several critical purposes:
    1. Standardizes math display mode delimiters to \[...\]
    2. Prevents nested delimiters that would break rendering
    3. Always uses align* environment for consistent formatting
    4. Ensures proper spacing in text mode
    """
    if not latex:
        return latex
    
    logger.info("=== LaTeX Formatting Debug ===")
    logger.info(f"Original LaTeX:\n{latex}")
    
    # Remove any existing math delimiters using precise regex
    latex = latex.strip()
    
    # First preserve LaTeX commands by temporarily replacing them
    commands = {}
    def preserve_command(match):
        cmd = match.group(0)
        token = f"CMD{len(commands)}"
        commands[token] = cmd
        return token
    latex = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})*', preserve_command, latex)
    
    # Normalize backslashes for line breaks
    # Replace any sequence of 2 or more backslashes with a space-separated pair
    latex = re.sub(r'\\{2,}', r'\\\\ ', latex)
    
    # Restore preserved LaTeX commands
    for token, cmd in commands.items():
        latex = latex.replace(token, cmd)
    
    # Ensure proper spacing in text mode
    latex = re.sub(r'(^|\\\\|\s|[^\\])text{', r'\1\\text{', latex)
    latex = re.sub(r'}text{', '} \\text{', latex)
    
    # Remove any existing math delimiters
    latex = re.sub(r'(^|[^\\])\$\$', '', latex)  # Remove $$ but not \$$
    latex = re.sub(r'^\\\[|\\\]$', '', latex)    # Remove only start/end \[ \]
    latex = latex.strip()
    logger.info(f"After delimiter removal:\n{latex}")
    
    # Split into lines and wrap in align* environment
    lines = [line.strip() for line in latex.split('\\\\')]
    # Clean up each line and add alignment points
    processed_lines = []
    for i, line in enumerate(lines):
        if line:  # Only process non-empty lines
            if i > 0 and not line.startswith('&'):
                line = '& ' + line
            processed_lines.append(line)
    
    # Join with proper line breaks and wrap in align*
    latex = '\\begin{align*} ' + ' \\\\ '.join(processed_lines) + ' \\end{align*}'
    
    logger.info(f"After alignment processing:\n{latex}")
    
    # Ensure color commands are properly formatted
    latex = re.sub(r'\\color{([^}]+)}([^{])', r'\\color{\1}{\2}', latex)
    
    # Add proper spacing around text mode content
    latex = re.sub(r'([^{\\])\\text{', r'\1 \\text{', latex)
    latex = re.sub(r'}\\text{', '} \\text{', latex)
    
    # Wrap in display math delimiters
    final_latex = f'\\[{latex}\\]'
    logger.info(f"Final formatted LaTeX:\n{final_latex}")
    logger.info("=== End LaTeX Formatting ===")
    
    return final_latex

@app.route('/')
def index():
    return render_template('index.html')

def async_handler(func):
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

@socketio.on('request_math')
@async_handler
async def handle_math_request(data):
    """Handle incoming math requests using the math teaching crew."""
    try:
        prompt = data.get('prompt', '')
        logger.info(f"Processing math request: {prompt}")
        
        # Get the crew result with Pydantic model
        result = await math_crew.crew().kickoff_async(inputs={'user_query': prompt})
        
        # Get the explanation from the Pydantic model
        explanation = result.pydantic
        
        # Send each step one at a time with formatted LaTeX
        for step in explanation.steps:
            logger.info(f"Processing step with math content:\n{step.math}")
            formatted_math = format_latex(step.math)
            logger.info(f"Emitting step with formatted math:\n{formatted_math}")
            
            emit('display_step', {
                'natural': step.natural,
                'math': formatted_math
            })
            # Small delay between steps for readability
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        emit('display_step', {
            'natural': 'Error processing math request',
            'math': r'\[\begin{align*} \text{Error processing math request} \end{align*}\]'
        })

@socketio.on('math_step')
def handle_math_step(data):
    """Broadcast a math step to all connected clients"""
    # Format any LaTeX content before broadcasting
    if 'math' in data:
        logger.info(f"Processing math step with content:\n{data['math']}")
        data['math'] = format_latex(data['math'])
        logger.info(f"Broadcasting formatted math:\n{data['math']}")
    socketio.emit('display_step', data)

if __name__ == '__main__':
    logger.info("Starting Math Learning Application")
    socketio.run(app, host='127.0.0.1', port=8000, debug=True)
