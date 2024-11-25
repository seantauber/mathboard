# MathBoard

An interactive mathematics teaching application that simulates a teacher explaining concepts while writing on a whiteboard. The system uses CrewAI for orchestrating LLM agents in the roles of teacher and reviewer, rendering mathematical notation in real-time using MathJax.

## Core Concept

The application creates an interactive experience where:
1. A teacher explains mathematical concepts verbally
2. While simultaneously writing mathematical notation
3. Each step pairs natural speech with LaTeX notation
4. Content renders in real-time on a whiteboard interface

## Project Structure

```
mathboard/
├── src/
│   ├── crews/
│   │   ├── config/
│   │   │   ├── agents.yaml     # Agent role definitions
│   │   │   └── tasks.yaml      # Task descriptions and formats
│   │   ├── tools/
│   │   │   └── latex_tools.py  # LaTeX formatting tools
│   │   └── crew.py            # CrewAI implementation
│   │
│   ├── utils/
│   │   └── latex_utils.py     # LaTeX security and formatting
│   │
│   ├── models/                # Pydantic models (if needed)
│   │   └── math.py           # Data structures
│   │
│   └── config/
│       └── settings.py        # Application settings
│
├── static/
│   ├── css/
│   │   ├── styles.css        # Base styles
│   │   └── mathboard.css     # Whiteboard specific styles
│   └── js/
│       ├── socket.js         # WebSocket handling
│       ├── mathjax-config.js # MathJax configuration
│       └── whiteboard.js     # UI interaction logic
│
├── templates/
│   └── index.html            # Main interface template
│
├── app.py                    # Flask application entry point
└── requirements.txt          # Python dependencies
```

## Key Components

### 1. CrewAI Setup

The system uses two agents:
- **Math Teacher**: Generates step-by-step explanations
- **Math Reviewer**: Validates and improves content

Tasks are defined in `crews/config/tasks.yaml`:
- `generate_explanation`: Creates teaching script with speech/math pairs
- `validate_latex`: Ensures correct notation and natural flow

### 2. Frontend

The interface uses:
- MathJax for LaTeX rendering
- WebSocket for real-time updates
- Responsive whiteboard design

### 3. Data Flow

1. User submits query via WebSocket
2. CrewAI processes through agents:
   ```python
   {
     "steps": [
       {
         "natural": "What the teacher says",
         "math": "LaTeX they write"
       }
     ]
   }
   ```
3. Response renders on whiteboard

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```python
   # Required environment variables
   OPENAI_API_KEY=your_key_here
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Development Guidelines

### Adding New Mathematical Capabilities

1. Update `tasks.yaml` with new output formats
2. Extend agent configurations in `agents.yaml`
3. Add any new tools in `crews/tools/`

### Working with CrewAI

- Tasks use variable interpolation:
  ```yaml
  description: "Process query: {user_query}"
  ```
- Agents are decorated with `@agent`
- Tasks are decorated with `@task`

### Frontend Modifications

1. MathJax Configuration:
   - Configure in `static/js/mathjax-config.js`
   - Use double dollars for display math: `$$...$$`

2. WebSocket Events:
   - `request_math`: Send queries
   - `math_response`: Receive formatted content

### Security

- LaTeX sanitization happens in `utils/latex_utils.py`
- Dangerous commands are stripped
- All input is validated before processing

## Testing

Run tests with:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Troubleshooting

Common issues:

1. LaTeX Rendering Issues:
   - Check MathJax configuration
   - Verify LaTeX syntax
   - Look for sanitization issues

2. Agent Communication:
   - Verify CrewAI configuration
   - Check task context variables
   - Monitor agent outputs

3. WebSocket Connections:
   - Check client connection
   - Verify event handling
   - Monitor socket status

## API Reference

### WebSocket Events

```javascript
// Send query
socket.emit('request_math', {
  prompt: "Solve quadratic equation..."
});

// Receive response
socket.on('math_response', function(data) {
  // data.steps = array of teaching steps
});
```

### CrewAI Response Format

```python
{
  "steps": [
    {
      "natural": str,  # Teacher's speech
      "math": str      # LaTeX notation
    },
    ...
  ]
}
```

## Roadmap

- [ ] Add support for multiple teaching styles
- [ ] Implement step-by-step playback
- [ ] Add audio narration support
- [ ] Expand mathematical topic coverage

## License

MIT License - See LICENSE file for details
