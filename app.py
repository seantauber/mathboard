from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from src.crews.crew import MathTutorCrew
import asyncio
from dotenv import load_dotenv
from functools import partial
import warnings
import logging
import re
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
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

# Track active requests
active_requests = {}

def format_latex(latex):
    r"""
    Format LaTeX content for proper display in MathJax.
    """
    if not latex:
        return latex
    
    logger.debug("=== LaTeX Formatting Debug ===")
    logger.debug(f"Original LaTeX:\n{latex}")
    
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
    latex = re.sub(r'\\{2,}', r'\\\\ ', latex)
    
    # Restore preserved LaTeX commands
    for token, cmd in commands.items():
        latex = latex.replace(token, cmd)
    
    # Ensure proper spacing in text mode
    latex = re.sub(r'(^|\\\\|\s|[^\\])text{', r'\1\\text{', latex)
    latex = re.sub(r'}text{', '} \\text{', latex)
    
    # Remove any existing math delimiters
    latex = re.sub(r'(^|[^\\])\$\$', '', latex)
    latex = re.sub(r'^\\\[|\\\]$', '', latex)
    latex = latex.strip()
    logger.debug(f"After delimiter removal:\n{latex}")
    
    # Split into lines and wrap in align* environment
    lines = [line.strip() for line in latex.split('\\\\')]
    processed_lines = []
    for i, line in enumerate(lines):
        if line:
            if i > 0 and not line.startswith('&'):
                line = '& ' + line
            processed_lines.append(line)
    
    latex = '\\begin{align*} ' + ' \\\\ '.join(processed_lines) + ' \\end{align*}'
    logger.debug(f"After alignment processing:\n{latex}")
    
    # Ensure color commands are properly formatted
    latex = re.sub(r'\\color{([^}]+)}([^{])', r'\\color{\1}{\2}', latex)
    
    # Add proper spacing around text mode content
    latex = re.sub(r'([^{\\])\\text{', r'\1 \\text{', latex)
    latex = re.sub(r'}\\text{', '} \\text{', latex)
    
    final_latex = f'\\[{latex}\\]'
    logger.debug(f"Final formatted LaTeX:\n{final_latex}")
    
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
        request_id = data.get('requestId', str(time.time()))
        
        logger.info(f"[Request {request_id}] New math request received: {prompt}")
        logger.info(f"[Request {request_id}] Active requests before: {list(active_requests.keys())}")
        
        # Cancel any existing request from this client
        for old_request_id in list(active_requests.keys()):
            logger.info(f"[Request {request_id}] Cancelling old request: {old_request_id}")
            del active_requests[old_request_id]
        
        # Track request start time
        active_requests[request_id] = {
            'start_time': datetime.now(),
            'prompt': prompt,
            'step_count': 0
        }
        
        # Get the crew result with Pydantic model
        logger.info(f"[Request {request_id}] Starting crew execution")
        result = await math_crew.crew().kickoff_async(inputs={'user_query': prompt})
        
        # Get the explanation from the Pydantic model
        explanation = result.pydantic
        total_steps = len(explanation.steps)
        logger.info(f"[Request {request_id}] Received explanation with {total_steps} steps")
        
        # Send each step one at a time with formatted LaTeX
        for i, step in enumerate(explanation.steps, 1):
            if request_id not in active_requests:
                logger.info(f"[Request {request_id}] Request cancelled, stopping step emission")
                break
                
            logger.info(f"[Request {request_id}] Processing step {i}/{total_steps}")
            logger.debug(f"[Request {request_id}] Step {i} math content:\n{step.math}")
            
            formatted_math = format_latex(step.math)
            logger.debug(f"[Request {request_id}] Formatted math:\n{formatted_math}")
            
            active_requests[request_id]['step_count'] = i
            
            emit('display_step', {
                'natural': step.natural,
                'math': formatted_math,
                'requestId': request_id,
                'stepNumber': i,
                'totalSteps': total_steps
            })
            
            # Small delay between steps for readability
            await asyncio.sleep(0.5)  # Reduced delay to 0.5s for better responsiveness
            
        # Log completion
        if request_id in active_requests:
            duration = datetime.now() - active_requests[request_id]['start_time']
            logger.info(f"[Request {request_id}] Completed in {duration.total_seconds():.2f}s")
            logger.info(f"[Request {request_id}] Emitted {active_requests[request_id]['step_count']} steps")
            del active_requests[request_id]
            
    except Exception as e:
        logger.error(f"[Request {request_id}] Error processing request:", exc_info=True)
        emit('display_step', {
            'natural': 'Error processing math request',
            'math': r'\[\begin{align*} \text{Error processing math request} \end{align*}\]',
            'requestId': request_id,
            'error': True
        })
        if request_id in active_requests:
            del active_requests[request_id]

@socketio.on('disconnect')
def handle_disconnect():
    """Clean up when a client disconnects"""
    logger.info("Client disconnected, cleaning up active requests")
    active_requests.clear()

if __name__ == '__main__':
    logger.info("Starting Math Learning Application")
    socketio.run(app, host='127.0.0.1', port=8000, debug=True)
