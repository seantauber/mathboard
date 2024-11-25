// Import helper functions
import { formatLatex, validateLatex, insertLatexSymbol } from './latex-helpers.js';

// Initialize socket connection
const socket = io();

// DOM Elements
const mathInput = document.getElementById('mathInput');
const askButton = document.getElementById('askButton');
const mathWhiteboard = document.getElementById('mathWhiteboard');
const explanationDisplay = document.getElementById('explanationDisplay');
const nextStepButton = document.getElementById('nextStepButton');
const errorDisplay = document.getElementById('errorDisplay');
const quickQuestions = document.querySelectorAll('.quick-question');
const mathSymbols = document.querySelectorAll('.math-symbol');

// State management
let currentStep = 0;
let steps = [];

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('display_step', (data) => {
    console.group('=== Received Step Data ===');
    console.log('Natural:', data.natural);
    console.log('Math LaTeX (raw):', data.math);
    console.log('Math LaTeX (escaped):', JSON.stringify(data.math));
    console.groupEnd();
    
    // Add step to queue
    steps.push(data);
    
    // If this is the first step, display it immediately
    if (steps.length === 1) {
        displayCurrentStep();
    } else {
        // Enable next step button if there are more steps
        nextStepButton.disabled = false;
    }
});

// Display current step
function displayCurrentStep() {
    if (currentStep < steps.length) {
        const step = steps[currentStep];
        
        // Display natural language explanation
        explanationDisplay.textContent = step.natural;
        
        // Display math content
        console.group('=== Displaying Math Content ===');
        console.log('Raw LaTeX:', step.math);
        console.log('LaTeX with newlines escaped:', JSON.stringify(step.math));
        
        try {
            mathWhiteboard.innerHTML = '';
            const mathElement = document.createElement('div');
            mathElement.textContent = step.math;
            mathWhiteboard.appendChild(mathElement);
            
            console.log('Math element created');
            console.log('textContent:', mathElement.textContent);
            console.log('innerHTML before MathJax:', mathElement.innerHTML);
            
            // Trigger MathJax processing
            if (window.MathJax) {
                console.log('Processing with MathJax...');
                window.MathJax.typesetPromise([mathWhiteboard]).then(() => {
                    console.log('MathJax processing complete');
                    console.log('Final rendered HTML:', mathWhiteboard.innerHTML);
                    // Log the computed styles to see if newlines are being rendered
                    const mathJaxOutput = mathWhiteboard.querySelector('.MathJax');
                    if (mathJaxOutput) {
                        console.log('MathJax output element:', mathJaxOutput);
                        console.log('MathJax SVG content:', mathJaxOutput.innerHTML);
                    }
                }).catch((err) => {
                    console.error('MathJax processing error:', err);
                });
            } else {
                console.error('MathJax not loaded');
            }
        } catch (error) {
            console.error('Error displaying math:', error);
            errorDisplay.textContent = 'Error displaying mathematical content';
        }
        console.groupEnd();
    }
}

// Event Listeners
askButton.addEventListener('click', () => {
    const query = mathInput.value.trim();
    if (query) {
        // Reset state
        steps = [];
        currentStep = 0;
        mathWhiteboard.innerHTML = '';
        explanationDisplay.textContent = '';
        nextStepButton.disabled = true;
        
        // Show loading state
        document.querySelector('.loading-spinner').style.display = 'block';
        
        // Send request
        socket.emit('request_math', { prompt: query });
        
        // Clear input
        mathInput.value = '';
    }
});

mathInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        askButton.click();
    }
});

nextStepButton.addEventListener('click', () => {
    if (currentStep < steps.length - 1) {
        currentStep++;
        displayCurrentStep();
        
        // Disable button if we're at the last step
        if (currentStep === steps.length - 1) {
            nextStepButton.disabled = true;
        }
    }
});

// Quick questions functionality
quickQuestions.forEach(button => {
    button.addEventListener('click', () => {
        mathInput.value = button.dataset.question;
        askButton.click();
    });
});

// Math symbols functionality
mathSymbols.forEach(symbol => {
    symbol.addEventListener('click', () => {
        insertLatexSymbol(mathInput, symbol.dataset.symbol);
    });
});

// Error handling
socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    errorDisplay.textContent = 'Connection error. Please try again.';
});

socket.on('error', (error) => {
    console.error('Socket error:', error);
    errorDisplay.textContent = 'An error occurred. Please try again.';
});

// Log MathJax configuration when loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.MathJax) {
        console.log('MathJax configuration:', window.MathJax.config);
    }
});
