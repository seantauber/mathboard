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
import os
from src.services.tts_service import generate_speech
from src.utils.math_utils import validate_mathml, format_mathml

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

# Validate environment
if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
socketio = SocketIO(app, 
                   cors_allowed_origins="*", 
                   async_mode='threading',
                   max_http_buffer_size=1e8,
                   binary=True)

# Initialize the math teaching crew
math_crew = MathTutorCrew()

# Track active requests
active_requests = {}

def process_math_content(content):
    """
    Process mathematical content, handling both MathML and LaTeX formats.
    """
    if not content:
        return content
    
    logger.debug("=== Math Content Processing Debug ===")
    logger.debug(f"Original content:\n{content}")
    
    # Check if content is MathML
    if '<math' in content:
        try:
            # Extract MathML if it's wrapped in LaTeX
            mathml_match = re.search(r'<math[\s\S]*?</math>', content)
            if mathml_match:
                mathml = mathml_match.group(0)
                if validate_mathml(mathml):
                    logger.debug("Valid MathML found")
                    return format_mathml(mathml)
        except Exception as e:
            logger.error(f"Error processing MathML: {e}")
            return content
    
    # If not MathML or invalid MathML, treat as LaTeX (legacy support)
    logger.debug("Processing as LaTeX (legacy support)")
    latex = content.strip()
    
    # Remove any existing math delimiters
    latex = re.sub(r'(^|[^\\])\$\$', '', latex)
    latex = re.sub(r'^\\\[|\\\]$', '', latex)
    latex = latex.strip()
    
    # Split into lines and wrap in align* environment
    lines = [line.strip() for line in latex.split('\\\\')]
    processed_lines = []
    for i, line in enumerate(lines):
        if line:
            if i > 0 and not line.startswith('&'):
                line = '& ' + line
            processed_lines.append(line)
    
    latex = '\\begin{align*} ' + ' \\\\ '.join(processed_lines) + ' \\end{align*}'
    
    # Add proper spacing around text mode content
    latex = re.sub(r'([^{\\])\\text{', r'\1 \\text{', latex)
    latex = re.sub(r'}\\text{', '} \\text{', latex)
    
    final_latex = f'\\[{latex}\\]'
    logger.debug(f"Final processed content:\n{final_latex}")
    
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
        
        # Process all steps in parallel for TTS
        tts_tasks = []
        for step in explanation.steps:
            if step.natural:
                tts_tasks.append(generate_speech(step.natural))
            
        audio_results = await asyncio.gather(*tts_tasks)
        
        # Send each step with its audio
        for i, (step, audio_data) in enumerate(zip(explanation.steps, audio_results), 1):
            if request_id not in active_requests:
                logger.info(f"[Request {request_id}] Request cancelled, stopping step emission")
                break
                
            logger.info(f"[Request {request_id}] Processing step {i}/{total_steps}")
            logger.debug(f"[Request {request_id}] Step {i} math content:\n{step.math}")
            
            processed_math = process_math_content(step.math)
            logger.debug(f"[Request {request_id}] Processed math:\n{processed_math}")
            
            active_requests[request_id]['step_count'] = i
            
            # Determine if content is MathML
            is_mathml = '<math' in processed_math
            
            emit('display_step', {
                'natural': step.natural,
                'math': processed_math if not is_mathml else None,
                'mathml': processed_math if is_mathml else None,
                'requestId': request_id,
                'stepNumber': i,
                'totalSteps': total_steps,
                'audio': audio_data,
                'hasAudio': audio_data is not None,
                'audioLength': len(audio_data) if audio_data else 0
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
            'natural': f'Error processing math request: {str(e)}',
            'math': r'\[\begin{align*} \text{Error processing math request} \end{align*}\]',
            'requestId': request_id,
            'error': True,
            'hasAudio': False,
            'audioLength': 0
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
