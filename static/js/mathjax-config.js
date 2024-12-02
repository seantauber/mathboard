// MathJax Configuration
window.MathJax = {
    loader: {
        load: [
            '[tex]/color', 
            '[tex]/ams', 
            '[tex]/noerrors', 
            '[tex]/noundefined', 
            '[tex]/newcommand', 
            '[tex]/configmacros',
            'input/mml',  // Add MathML input processor
            'output/svg'  // Explicit SVG output processor
        ]
    },
    tex: {
        packages: {
            '[+]': ['color', 'ams', 'noerrors', 'noundefined', 'newcommand', 'configmacros']
        },
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true,
        processRefs: true,
        tags: 'none',
        tagSide: 'right',
        tagIndent: '0.8em',
        multlineWidth: '85%',
        maxMacros: 1000,
        maxBuffer: 5 * 1024,
        formatError: (jax, err) => jax.formatError(err),
        environments: {
            multiline: ['\\\\', '\\\\'],
            aligned: ['\\\\', '\\\\'],
            array: ['\\\\', '\\\\'],
            alignedat: ['\\\\', '\\\\'],
            gathered: ['\\\\', '\\\\'],
            align: ['\\\\', '\\\\'],
            alignat: ['\\\\', '\\\\']
        }
    },
    mml: {
        // MathML-specific configuration
        parseError: (node) => {
            console.warn('MathML Parse Error:', node);
            return node;
        },
        verify: {
            // Verification options for MathML input
            checkArity: true,
            checkAttributes: true,
            fullErrors: true,
            fixMmultiscripts: true,
            fixMtables: true
        }
    },
    svg: {
        fontCache: 'global',
        scale: 1,
        minScale: .5,
        mtextInheritFont: false,
        merrorInheritFont: true,
        mathmlSpacing: true, // Enable MathML spacing rules
        skipAttributes: {},
        exFactor: .5,
        displayAlign: 'center',
        displayIndent: '0',
        localID: null,
        internalSpeechTitles: true,
        titleID: 0
    },
    options: {
        enableMenu: true,
        menuOptions: {
            settings: {
                renderer: 'SVG',
                zoom: 'Click',
                zscale: '200%'
            }
        }
    },
    startup: {
        ready: () => {
            MathJax.startup.defaultReady();
            console.log('MathJax configuration loaded with settings:', {
                packages: MathJax.config.tex.packages,
                environments: MathJax.config.tex.environments,
                displayMath: MathJax.config.tex.displayMath,
                mmlEnabled: !!MathJax.config.mml
            });
        },
        input: ['tex', 'mml'], // Enable both TeX and MathML input
        output: 'svg'          // Use SVG output for both
    }
};

// Debug MathJax loading
if (window.MathJax) {
    console.log('MathJax is available on window object');
} else {
    console.log('MathJax is not yet available');
    document.addEventListener('DOMContentLoaded', () => {
        if (window.MathJax) {
            console.log('MathJax became available after DOM load');
            console.log('MathML support status:', {
                inputProcessor: !!MathJax.config.mml,
                outputProcessor: MathJax.config.svg.mathmlSpacing
            });
        } else {
            console.log('MathJax still not available after DOM load');
        }
    });
}
