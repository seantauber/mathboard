// Math helper functions for both LaTeX and MathML

// MathML specific functions
export function createMathMLElement(tag, attributes = {}, content = '') {
    const element = `<${tag}${Object.entries(attributes)
        .map(([key, value]) => ` ${key}="${value}"`)
        .join('')}>${content}</${tag}>`;
    return element;
}

export function wrapMathML(content) {
    return `<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">${content}</math>`;
}

export function formatMathML(content) {
    // Remove any existing math delimiters
    content = content.trim()
        .replace(/<\/?math[^>]*>/g, '')
        .trim();
    
    return wrapMathML(content);
}

// Maintain LaTeX support during transition
export function formatLatex(latex) {
    // Remove any existing math delimiters
    latex = latex.trim()
        .replace(/^\$\$|\$\$$|^\\\[|\\\]$|^\\begin{equation}|\\end{equation}$/g, '')
        .trim();
    
    // Wrap in display math delimiters
    return `\\[${latex}\\]`;
}

export function validateMathML(mathml) {
    // Basic validation of MathML syntax
    const parser = new DOMParser();
    const doc = parser.parseFromString(mathml, 'application/xml');
    
    // Check for parsing errors
    const parseError = doc.querySelector('parsererror');
    if (parseError) return false;
    
    // Verify root math element
    const mathElement = doc.querySelector('math');
    if (!mathElement) return false;
    
    // Verify required attributes
    if (!mathElement.getAttribute('xmlns')) return false;
    
    return true;
}

// Maintain LaTeX validation during transition
export function validateLatex(latex) {
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
        
        if (char === '$' || (char === '\\' && (latex[i + 1] === '[' || latex[i + 1] === ']'))) {
            inMathMode = !inMathMode;
            if (char === '\\') i++;
            continue;
        }
        
        for (const [opening, closing] of Object.entries(delimiters)) {
            if (latex.slice(i, i + opening.length) === opening) {
                stack.push(closing);
                i += opening.length - 1;
                break;
            }
        }
        
        for (const closing of Object.values(delimiters)) {
            if (latex.slice(i, i + closing.length) === closing) {
                if (stack.length === 0 || stack.pop() !== closing) {
                    return false;
                }
                i += closing.length - 1;
                break;
            }
        }
    }
    
    return stack.length === 0 && !inMathMode;
}

export function insertMathSymbol(input, symbol, format = 'mathml', cursorOffset = 0) {
    const start = input.selectionStart;
    const end = input.selectionEnd;
    const text = input.value;
    
    // Get the appropriate symbol based on format
    const symbolToInsert = format === 'mathml' ? 
        (mathmlSymbols[symbol] || symbol) : 
        (commonSymbols[symbol] || symbol);
    
    // Insert the symbol
    input.value = text.slice(0, start) + symbolToInsert + text.slice(end);
    
    // Position cursor appropriately
    let newPosition = start + symbolToInsert.length + cursorOffset;
    
    // For MathML tags, position cursor inside element
    if (format === 'mathml' && symbolToInsert.includes('></')) {
        newPosition = start + symbolToInsert.indexOf('></');
    }
    // For LaTeX commands with braces, position cursor inside first brace
    else if (format === 'latex' && symbolToInsert.includes('{}')) {
        newPosition = start + symbolToInsert.indexOf('{}') + 1;
    }
    
    input.selectionStart = input.selectionEnd = newPosition;
    return input.value;
}

// Maintain legacy function name during transition
export const insertLatexSymbol = (input, symbol, cursorOffset = 0) => 
    insertMathSymbol(input, symbol, 'latex', cursorOffset);

// Symbol mappings for both formats
export const mathmlSymbols = {
    operators: {
        '+': '+',
        '-': '−',
        '×': '×',
        '÷': '÷',
        '=': '=',
        '≠': '≠',
        '≈': '≈',
        '±': '±',
    },
    greek: {
        'α': 'α',
        'β': 'β',
        'γ': 'γ',
        'θ': 'θ',
        'π': 'π',
        'Σ': 'Σ',
        'Δ': 'Δ',
        'Ω': 'Ω',
    },
    structures: {
        'fraction': '<mfrac><mrow></mrow><mrow></mrow></mfrac>',
        'square root': '<msqrt></msqrt>',
        'nth root': '<mroot><mrow></mrow><mn>n</mn></mroot>',
        'sum': '<munderover><mo>∑</mo><mrow>i=1</mrow><mi>n</mi></munderover>',
        'integral': '<msubsup><mo>∫</mo><mi>a</mi><mi>b</mi></msubsup>',
        'limit': '<munder><mo>lim</mo><mrow>x→∞</mrow></munder>',
    }
};

// Maintain legacy symbols during transition
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

export function createMathTemplate(type, format = 'mathml', ...args) {
    const mathmlTemplates = {
        fraction: (num = '', den = '') => 
            `<mfrac><mrow>${num}</mrow><mrow>${den}</mrow></mfrac>`,
        sqrt: (content = '') => 
            `<msqrt>${content}</msqrt>`,
        nthroot: (n = 'n', content = '') => 
            `<mroot><mrow>${content}</mrow><mn>${n}</mn></mroot>`,
        sum: (lower = 'i=1', upper = 'n') => 
            `<munderover><mo>∑</mo><mrow>${lower}</mrow><mi>${upper}</mi></munderover>`,
        integral: (lower = 'a', upper = 'b') => 
            `<msubsup><mo>∫</mo><mi>${lower}</mi><mi>${upper}</mi></msubsup>`,
        limit: (var_ = 'x', to = '∞') => 
            `<munder><mo>lim</mo><mrow>${var_}→${to}</mrow></munder>`,
        matrix: (rows = 2, cols = 2) => {
            const cells = Array(rows).fill().map(() => 
                Array(cols).fill('<mtd></mtd>').join('')
            ).map(row => `<mtr>${row}</mtr>`).join('');
            return `<mtable>${cells}</mtable>`;
        }
    };

    const latexTemplates = {
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

    const templates = format === 'mathml' ? mathmlTemplates : latexTemplates;
    return templates[type]?.(...args) || '';
}

// Maintain legacy function name during transition
export const createLatexTemplate = (type, ...args) => 
    createMathTemplate(type, 'latex', ...args);
