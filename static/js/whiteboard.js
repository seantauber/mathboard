// Import helper functions
import { formatLatex, validateLatex, insertLatexSymbol } from './latex-helpers.js';
import MathboardSocket from './socket.js';

// DOM Elements
const mathInput = document.getElementById('mathInput');
const askButton = document.getElementById('askButton');
const mathWhiteboard = document.getElementById('mathWhiteboard');
const explanationDisplay = document.getElementById('explanationDisplay');
const nextStepButton = document.getElementById('nextStepButton');
const errorDisplay = document.getElementById('errorDisplay');
const quickQuestions = document.querySelectorAll('.quick-question');
const mathSymbols = document.querySelectorAll('.math-symbol');

// Initialize socket connection
const mathboardSocket = new MathboardSocket({
    mathWhiteboard,
    explanationDisplay,
    nextStepButton,
    errorDisplay
});

// Event Listeners
askButton.addEventListener('click', () => {
    const query = mathInput.value.trim();
    if (query) {
        // Show loading state
        document.querySelector('.loading-spinner').style.display = 'block';
        
        // Send request
        mathboardSocket.sendMathQuery(query);
        
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
    mathboardSocket.nextStep();
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

// Log MathJax configuration when loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.MathJax) {
        console.log('MathJax configuration:', window.MathJax.config);
    }
});
