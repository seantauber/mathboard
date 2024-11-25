class MathboardSocket {
    constructor() {
        this.socket = io();
        this.stepQueue = [];
        this.setupSocketListeners();
    }

    setupSocketListeners() {
        // Handle connection errors
        this.socket.on('connect_error', (error) => {
            this.showError('Connection error. Please try again later.');
            console.log('Connection error:', error);
        });

        // Handle receiving steps from the server
        this.socket.on('display_step', (data) => {
            this.addStepToQueue(data);
        });
    }

    addStepToQueue(data) {
        this.stepQueue.push(data);
        
        // If this is the first step, display it immediately
        if (this.stepQueue.length === 1) {
            this.displayCurrentStep();
        }
        
        // Enable the next step button if there are more steps
        this.updateNextStepButton();
    }

    async displayCurrentStep() {
        if (this.stepQueue.length === 0) return;

        const data = this.stepQueue[0];
        const mathWhiteboard = document.getElementById('mathWhiteboard');
        const explanationDisplay = document.getElementById('explanationDisplay');
        const loadingSpinner = document.querySelector('.loading-spinner');
        
        // Hide loading spinner
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        
        // Display math in whiteboard
        if (data.math) {
            mathWhiteboard.innerHTML = data.math;
        }
        
        // Display explanation
        if (data.natural) {
            explanationDisplay.innerHTML = `<p>${data.natural}</p>`;
        }
        
        // Wait for MathJax to be ready
        try {
            if (window.MathJax && window.MathJax.typesetPromise) {
                await window.MathJax.typesetPromise([mathWhiteboard]);
            } else {
                console.log('MathJax not ready, falling back to basic rendering');
            }
        } catch (err) {
            console.log('Error rendering math:', err);
        }
    }

    nextStep() {
        // Remove the current step and show the next one
        if (this.stepQueue.length > 0) {
            this.stepQueue.shift();
            this.displayCurrentStep();
            this.updateNextStepButton();
        }
    }

    updateNextStepButton() {
        const nextStepButton = document.getElementById('nextStepButton');
        if (nextStepButton) {
            // Enable button if there are more steps in the queue
            nextStepButton.disabled = this.stepQueue.length <= 1;
        }
    }

    showError(message) {
        const errorDisplay = document.getElementById('errorDisplay');
        if (errorDisplay) {
            errorDisplay.textContent = message;
            errorDisplay.style.display = 'block';
        }
    }

    async sendMathQuery(query) {
        if (!query.trim()) {
            this.showError('Please enter a question');
            return;
        }

        const mathWhiteboard = document.getElementById('mathWhiteboard');
        const explanationDisplay = document.getElementById('explanationDisplay');
        const loadingSpinner = document.querySelector('.loading-spinner');
        const nextStepButton = document.getElementById('nextStepButton');

        // Clear previous content and show loading
        if (mathWhiteboard) {
            mathWhiteboard.innerHTML = '';
        }
        if (explanationDisplay) {
            explanationDisplay.innerHTML = `
                <div class="waiting-message">
                    <p>Processing your question...</p>
                </div>
            `;
        }
        if (loadingSpinner) {
            loadingSpinner.style.display = 'block';
        }
        if (nextStepButton) {
            nextStepButton.disabled = true;
        }

        // Clear the step queue
        this.stepQueue = [];

        // Emit the question to the server
        this.socket.emit('request_math', { prompt: query });
    }
}

// Initialize event listeners for standalone usage
document.addEventListener('DOMContentLoaded', function() {
    const mathInput = document.getElementById('mathInput');
    const askButton = document.getElementById('askButton');
    const nextStepButton = document.getElementById('nextStepButton');
    const quickQuestions = document.querySelectorAll('.quick-question');
    
    if (!window.whiteboard) {  // Only initialize if not using whiteboard.js
        const socket = new MathboardSocket();

        // Handle ask button click
        if (askButton) {
            askButton.addEventListener('click', () => {
                socket.sendMathQuery(mathInput.value);
            });
        }

        // Handle next step button click
        if (nextStepButton) {
            nextStepButton.addEventListener('click', () => {
                socket.nextStep();
            });
        }

        // Handle enter key in input
        if (mathInput) {
            mathInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    socket.sendMathQuery(mathInput.value);
                }
            });
        }

        // Handle quick question buttons
        quickQuestions.forEach(button => {
            button.addEventListener('click', () => {
                const question = button.dataset.question;
                if (mathInput) {
                    mathInput.value = question;
                }
                socket.sendMathQuery(question);
            });
        });

        // Handle math symbol clicks
        document.querySelectorAll('.math-symbol').forEach(symbol => {
            symbol.addEventListener('click', () => {
                if (mathInput) {
                    const symbolText = symbol.dataset.symbol;
                    const cursorPos = mathInput.selectionStart;
                    const inputValue = mathInput.value;
                    mathInput.value = inputValue.slice(0, cursorPos) + symbolText + inputValue.slice(cursorPos);
                    mathInput.focus();
                    mathInput.setSelectionRange(cursorPos + symbolText.length, cursorPos + symbolText.length);
                }
            });
        });
    }
});

export default MathboardSocket;
