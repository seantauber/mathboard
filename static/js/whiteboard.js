import MathboardSocket from './socket.js';
import { formatLatex, validateLatex, insertLatexSymbol } from './latex-helpers.js';

class Whiteboard {
    constructor() {
        this.socket = new MathboardSocket();
        this.currentInput = '';
        this.history = [];
        this.historyIndex = -1;
        this.initializeElements();
        this.setupEventListeners();
    }

    initializeElements() {
        this.inputElement = document.getElementById('mathInput');
        this.mathWhiteboard = document.getElementById('mathWhiteboard');
        this.explanationDisplay = document.getElementById('explanationDisplay');
        this.nextStepButton = document.getElementById('nextStepButton');
    }

    setupEventListeners() {
        if (this.inputElement) {
            // Input handling
            this.inputElement.addEventListener('input', this.handleInput.bind(this));
            this.inputElement.addEventListener('keydown', this.handleKeyPress.bind(this));
        }

        // Next step button
        if (this.nextStepButton) {
            this.nextStepButton.addEventListener('click', () => {
                this.socket.nextStep();
            });
        }

        // Math symbols
        document.querySelectorAll('.math-symbol').forEach(symbol => {
            symbol.addEventListener('click', (e) => {
                this.insertSymbol(e.target.dataset.symbol);
            });
        });

        // Quick questions
        document.querySelectorAll('.quick-question').forEach(button => {
            button.addEventListener('click', (e) => {
                const question = e.target.dataset.question;
                if (this.inputElement) {
                    this.inputElement.value = question;
                    this.sendQuery(question);
                }
            });
        });
    }

    async handleInput(event) {
        this.currentInput = event.target.value;
        
        // Update preview if valid LaTeX
        if (validateLatex(this.currentInput)) {
            this.updatePreview(this.currentInput);
        }
    }

    handleKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendQuery(this.currentInput);
        }
    }

    async sendQuery(query) {
        try {
            await this.socket.sendMathQuery(query);
            this.updateHistory(query);
        } catch (error) {
            console.error('Error sending query:', error);
            this.socket.showError(error.message);
        }
    }

    updatePreview(latex) {
        if (this.mathWhiteboard) {
            const formattedLatex = formatLatex(latex);
            this.mathWhiteboard.innerHTML = formattedLatex;
            MathJax.typesetPromise([this.mathWhiteboard]).catch(err => {
                console.error('MathJax error:', err);
            });
        }
    }

    updateHistory(input) {
        this.history.push(input);
        this.historyIndex = this.history.length;
    }

    insertSymbol(symbol) {
        if (this.inputElement) {
            insertLatexSymbol(this.inputElement, symbol);
            this.currentInput = this.inputElement.value;
            this.handleInput({ target: this.inputElement });
        }
    }

    clearBoard() {
        if (this.inputElement) {
            this.inputElement.value = '';
            this.currentInput = '';
        }
        if (this.mathWhiteboard) {
            this.mathWhiteboard.innerHTML = '';
        }
        if (this.explanationDisplay) {
            this.explanationDisplay.innerHTML = `
                <div class="welcome-message">
                    <h3>Welcome to Interactive Math Learning!</h3>
                    <p>Ask a math question above to get started.</p>
                    <p>You'll receive step-by-step explanations with both text and mathematical notation.</p>
                </div>
            `;
        }
    }
}

// Initialize whiteboard when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.whiteboard = new Whiteboard();
});

export default Whiteboard;
