# MathBoard

An interactive mathematics teaching application that simulates a teacher explaining concepts while writing on a whiteboard. The system uses CrewAI for orchestrating LLM agents in the role of a math teacher, rendering mathematical notation in real-time using MathJax.

## Features

- Real-time step-by-step mathematical explanations
- Natural teaching flow with synchronized text and mathematical notation
- Interactive whiteboard interface with MathJax rendering
- Quick access to common mathematical symbols
- Support for a wide range of mathematical topics

## Project Structure

```
mathboard/
├── src/
│   ├── crews/
│   │   ├── config/
│   │   │   ├── agents.yaml     # Agent role definitions
│   │   │   └── tasks.yaml      # Task descriptions and formats
│   │   ├── tools/
│   │   │   ├── latex_tools.py      # LaTeX formatting tools
│   │   │   └── explanation_tools.py # Explanation validation
│   │   └── crew.py            # CrewAI implementation
│   │
│   ├── utils/
│   │   └── latex_utils.py     # LaTeX security and formatting
│   │
│   └── models/
│       └── math_models.py     # Pydantic data models
│
├── static/
│   ├── css/
│   │   └── styles.css         # Application styles
│   └── js/
│       ├── socket.js          # WebSocket handling
│       ├── latex-helpers.js   # LaTeX utility functions
│       └── whiteboard.js      # UI interaction logic
│
├── templates/
│   └── index.html            # Main interface template
│
├── app.py                    # Flask application entry point
└── requirements.txt          # Python dependencies
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mathboard.git
   cd mathboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Create a .env file with:
   OPENAI_API_KEY=your_key_here
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open in your browser:
   ```
   http://localhost:8000
   ```

## How It Works

### Backend Components

1. **CrewAI Agent**: 
   - Generates step-by-step mathematical explanations
   - Formats content for natural teaching flow
   - Ensures proper LaTeX notation

2. **Flask Server**:
   - Handles WebSocket connections
   - Manages real-time communication
   - Formats and validates content

### Frontend Components

1. **Interactive Interface**:
   - Math symbol toolbar for quick access
   - Split view with whiteboard and explanation
   - Real-time step progression

2. **WebSocket Events**:
   ```javascript
   // Send query
   socket.emit('request_math', {
     prompt: "How do you add fractions?"
   });

   // Receive steps
   socket.on('display_step', function(data) {
     // data.natural = Teacher's explanation
     // data.math = LaTeX notation
   });
   ```

### Data Flow

1. User submits a mathematical question
2. CrewAI processes the query and generates steps
3. Each step contains:
   ```python
   {
     "natural": "Teacher's explanation for this step",
     "math": "LaTeX mathematical notation"
   }
   ```
4. Steps are sent via WebSocket and rendered in real-time

## Development

### Adding New Features

1. **Backend Changes**:
   - Add new tools in `src/crews/tools/`
   - Update task configurations in `tasks.yaml`
   - Modify agent behavior in `crew.py`

2. **Frontend Changes**:
   - Update UI components in `index.html`
   - Modify styles in `styles.css`
   - Add JavaScript functionality in respective files

### Working with LaTeX

1. **Formatting**:
   - Use `\\[` and `\\]` for display math
   - Ensure proper escaping of special characters
   - Follow MathJax syntax guidelines

2. **Validation**:
   - LaTeX is sanitized in `latex_utils.py`
   - Dangerous commands are stripped
   - Syntax is validated before rendering

### WebSocket Communication

1. **Events**:
   - `request_math`: Send mathematical queries
   - `display_step`: Receive formatted steps

2. **Step Format**:
   ```python
   {
     "natural": str,  # Clear, natural language explanation
     "math": str      # Properly formatted LaTeX
   }
   ```

## Troubleshooting

1. **No Steps Displaying**:
   - Check WebSocket connection
   - Verify OpenAI API key
   - Check browser console for errors

2. **LaTeX Not Rendering**:
   - Verify MathJax is loaded
   - Check LaTeX syntax
   - Look for console errors

3. **Slow Response**:
   - Check network connection
   - Verify server is running
   - Monitor API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please ensure:
- Code follows existing style
- Documentation is updated
- Tests pass (if applicable)

## License

MIT License - See LICENSE file for details
