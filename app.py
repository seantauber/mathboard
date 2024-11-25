from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from src.crews.crew import MathTutorCrew
import asyncio
from dotenv import load_dotenv
from functools import partial
import warnings
import logging

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
    """Format LaTeX content for proper display."""
    if not latex:
        return latex
    
    # Remove any existing math delimiters
    latex = latex.strip()
    latex = latex.replace('$$', '').replace('\\[', '').replace('\\]', '')
    latex = latex.strip()
    
    # Wrap in display math delimiters
    return f'\\[{latex}\\]'

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
            emit('display_step', {
                'natural': step.natural,
                'math': format_latex(step.math)
            })
            # Small delay between steps for readability
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        emit('display_step', {
            'natural': 'Error processing math request',
            'math': r'\[\text{Error processing math request}\]'
        })

@socketio.on('math_step')
def handle_math_step(data):
    """Broadcast a math step to all connected clients"""
    # Format any LaTeX content before broadcasting
    if 'math' in data:
        data['math'] = format_latex(data['math'])
    socketio.emit('display_step', data)

if __name__ == '__main__':
    logger.info("Starting Math Learning Application")
    socketio.run(app, host='127.0.0.1', port=8000, debug=True)
