// MathJax Configuration
window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true,
        // Add macros for commonly used expressions
        macros: {
            // Example macros
            vec: ['\\boldsymbol{#1}', 1],
            mat: ['\\mathbf{#1}', 1],
            R: '\\mathbb{R}',
            N: '\\mathbb{N}'
        }
    },
    svg: {
        fontCache: 'global'
    },
    options: {
        skipHtmlTags: [
            'script', 'noscript', 'style', 'textarea', 'pre', 'code'
        ],
        processHtmlClass: 'math-tex',
        ignoreHtmlClass: 'no-mathjax'
    },
    startup: {
        pageReady: () => {
            console.log('MathJax is ready');
            // You can add custom initialization here
            return MathJax.startup.defaultPageReady();
        }
    },
    loader: {
        load: ['[tex]/color', '[tex]/cancel', '[tex]/physics']
    }
};
