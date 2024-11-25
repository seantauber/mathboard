from typing import Dict, Any
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).parent.parent.parent

# Flask Configuration
FLASK_CONFIG: Dict[str, Any] = {
    'SECRET_KEY': 'your-secret-key-here',  # Change this in production
    'DEBUG': True
}

# Socket.IO Configuration
SOCKETIO_CONFIG: Dict[str, Any] = {
    'async_mode': None,
    'cors_allowed_origins': '*',
    'ping_timeout': 60,
    'ping_interval': 25
}

# MathJax Configuration
MATHJAX_CONFIG: Dict[str, Any] = {
    'output_format': 'svg',
    'enable_menu': False,
    'enable_assistive_mml': True
}

# Agent Configuration Path
AGENTS_CONFIG_PATH = BASE_DIR / 'src' / 'crews' / 'config' / 'agents.yaml'
TASKS_CONFIG_PATH = BASE_DIR / 'src' / 'crews' / 'config' / 'tasks.yaml'

# Latex Configuration
LATEX_CONFIG: Dict[str, Any] = {
    'max_expression_length': 1000,
    'allowed_commands': [
        'sqrt', 'frac', 'sum', 'int', 'prod',
        'alpha', 'beta', 'gamma', 'delta', 'theta',
        'pi', 'infty', 'partial'
    ],
    'timeout_seconds': 30
}
