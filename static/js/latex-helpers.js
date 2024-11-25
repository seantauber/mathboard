// LaTeX helper functions

export function formatLatex(latex) {
    // Remove any existing math delimiters
    latex = latex.trim()
        .replace(/^\$\$|\$\$$|^\\\[|\\\]$|^\\begin{equation}|\\end{equation}$/g, '')
        .trim();
    
    // Wrap in display math delimiters
    return `\\[${latex}\\]`;
}

export function validateLatex(latex) {
    // Basic validation of LaTeX syntax
    const delimiters = {
        '{': '}',
        '[': ']',
        '(': ')',
        '\\{': '\\}',
        '\\[': '\\]',
        '\\begin{': '\\end{',
    };
    
    const stack = [];
    let inMathMode = false;
    
    for (let i = 0; i < latex.length; i++) {
        const char = latex[i];
        
        // Check math mode delimiters
        if (char === '$' || (char === '\\' && (latex[i + 1] === '[' || latex[i + 1] === ']'))) {
            inMathMode = !inMathMode;
            if (char === '\\') i++; // Skip the next character
            continue;
        }
        
        // Check opening delimiters
        for (const [opening, closing] of Object.entries(delimiters)) {
            if (latex.slice(i, i + opening.length) === opening) {
                stack.push(closing);
                i += opening.length - 1; // Skip the rest of the opening delimiter
                break;
            }
        }
        
        // Check closing delimiters
        for (const closing of Object.values(delimiters)) {
            if (latex.slice(i, i + closing.length) === closing) {
                if (stack.length === 0 || stack.pop() !== closing) {
                    return false;
                }
                i += closing.length - 1; // Skip the rest of the closing delimiter
                break;
            }
        }
    }
    
    return stack.length === 0 && !inMathMode;
}

export function insertLatexSymbol(input, symbol, cursorOffset = 0) {
    const start = input.selectionStart;
    const end = input.selectionEnd;
    const text = input.value;
    
    // Insert the symbol
    input.value = text.slice(0, start) + symbol + text.slice(end);
    
    // Position cursor appropriately for commands with braces
    let newPosition = start + symbol.length + cursorOffset;
    
    // For commands with empty braces, position cursor inside first brace
    if (symbol.includes('{}')) {
        newPosition = start + symbol.indexOf('{}') + 1;
    }
    
    input.selectionStart = input.selectionEnd = newPosition;
    return input.value;
}

export const commonSymbols = {
    operators: {
        '+': '+',
        '-': '-',
        '×': '\\times',
        '÷': '\\div',
        '=': '=',
        '≠': '\\neq',
        '≈': '\\approx',
        '±': '\\pm',
    },
    greek: {
        'α': '\\alpha',
        'β': '\\beta',
        'γ': '\\gamma',
        'θ': '\\theta',
        'π': '\\pi',
        'Σ': '\\Sigma',
        'Δ': '\\Delta',
        'Ω': '\\Omega',
    },
    structures: {
        'fraction': '\\frac{}{}',
        'square root': '\\sqrt{}',
        'nth root': '\\sqrt[n]{}',
        'sum': '\\sum_{i=1}^n',
        'integral': '\\int_{a}^b',
        'limit': '\\lim_{x \\to \\infty}',
    }
};

export function createLatexTemplate(type, ...args) {
    const templates = {
        fraction: (num = '', den = '') => `\\frac{${num}}{${den}}`,
        sqrt: (content = '') => `\\sqrt{${content}}`,
        nthroot: (n = 'n', content = '') => `\\sqrt[${n}]{${content}}`,
        sum: (lower = 'i=1', upper = 'n') => `\\sum_{${lower}}^{${upper}}`,
        integral: (lower = 'a', upper = 'b') => `\\int_{${lower}}^{${upper}}`,
        limit: (var_ = 'x', to = '\\infty') => `\\lim_{${var_} \\to ${to}}`,
        matrix: (rows = 2, cols = 2) => {
            const cells = Array(rows).fill().map(() => Array(cols).fill('').join(' & '));
            return `\\begin{bmatrix}${cells.join(' \\\\ ')}\\end{bmatrix}`;
        }
    };

    return templates[type]?.(...args) || '';
}
