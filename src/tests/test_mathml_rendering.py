"""
Frontend MathML rendering test script.
Launches a test page with predefined MathML expressions to validate rendering.
"""
from flask import Flask, render_template_string
import webbrowser
import os

app = Flask(__name__)

# Test cases covering different MathML features
TEST_CASES = [
    {
        "name": "Basic Arithmetic",
        "mathml": """
        <math>
            <mrow>
                <mn>2</mn>
                <mo>+</mo>
                <mn>3</mn>
                <mo>=</mo>
                <mn>5</mn>
            </mrow>
        </math>
        """
    },
    {
        "name": "Fractions",
        "mathml": """
        <math>
            <mfrac>
                <mrow>
                    <mn>1</mn>
                    <mo>+</mo>
                    <mn>2</mn>
                </mrow>
                <mn>3</mn>
            </mfrac>
        </math>
        """
    },
    {
        "name": "Superscripts and Subscripts",
        "mathml": """
        <math>
            <msup>
                <mi>x</mi>
                <mn>2</mn>
            </msup>
            <mo>+</mo>
            <msub>
                <mi>y</mi>
                <mn>1</mn>
            </msub>
        </math>
        """
    },
    {
        "name": "Square Root",
        "mathml": """
        <math>
            <msqrt>
                <mrow>
                    <msup>
                        <mi>x</mi>
                        <mn>2</mn>
                    </msup>
                    <mo>+</mo>
                    <msup>
                        <mi>y</mi>
                        <mn>2</mn>
                    </msup>
                </mrow>
            </msqrt>
        </math>
        """
    },
    {
        "name": "Matrix",
        "mathml": """
        <math>
            <mrow>
                <mo>[</mo>
                <mtable>
                    <mtr>
                        <mtd><mn>1</mn></mtd>
                        <mtd><mn>2</mn></mtd>
                    </mtr>
                    <mtr>
                        <mtd><mn>3</mn></mtd>
                        <mtd><mn>4</mn></mtd>
                    </mtr>
                </mtable>
                <mo>]</mo>
            </mrow>
        </math>
        """
    },
    {
        "name": "Colors and Highlighting",
        "mathml": """
        <math>
            <mrow>
                <mi mathcolor="red">x</mi>
                <mo>+</mo>
                <mi mathcolor="blue">y</mi>
                <mo>=</mo>
                <mn mathcolor="green">5</mn>
            </mrow>
        </math>
        """
    },
    {
        "name": "Complex Expression",
        "mathml": """
        <math>
            <mrow>
                <mfrac>
                    <mrow>
                        <mo>-</mo>
                        <mi>b</mi>
                        <mo>±</mo>
                        <msqrt>
                            <mrow>
                                <msup>
                                    <mi>b</mi>
                                    <mn>2</mn>
                                </msup>
                                <mo>-</mo>
                                <mn>4</mn>
                                <mi>a</mi>
                                <mi>c</mi>
                            </mrow>
                        </msqrt>
                    </mrow>
                    <mrow>
                        <mn>2</mn>
                        <mi>a</mi>
                    </mrow>
                </mfrac>
            </mrow>
        </math>
        """
    },
    {
        "name": "System of Equations",
        "mathml": """
        <math>
            <mtable columnalign="left">
                <mtr>
                    <mtd>
                        <mrow>
                            <mn>2</mn>
                            <mi>x</mi>
                            <mo>+</mo>
                            <mn>3</mn>
                            <mi>y</mi>
                            <mo>=</mo>
                            <mn>8</mn>
                        </mrow>
                    </mtd>
                </mtr>
                <mtr>
                    <mtd>
                        <mrow>
                            <mn>4</mn>
                            <mi>x</mi>
                            <mo>-</mo>
                            <mn>5</mn>
                            <mi>y</mi>
                            <mo>=</mo>
                            <mn>2</mn>
                        </mrow>
                    </mtd>
                </mtr>
            </mtable>
        </math>
        """
    },
    {
        "name": "Multi-step Algebraic Expression",
        "mathml": """
        <math>
            <mtable columnalign="left">
                <mtr>
                    <mtd>
                        <mrow>
                            <mo stretchy="false">(</mo>
                            <mi>x</mi>
                            <mo>+</mo>
                            <mn>2</mn>
                            <mo stretchy="false">)</mo>
                            <mo stretchy="false">(</mo>
                            <mi>x</mi>
                            <mo>-</mo>
                            <mn>3</mn>
                            <mo stretchy="false">)</mo>
                        </mrow>
                    </mtd>
                </mtr>
                <mtr>
                    <mtd>
                        <mrow>
                            <mo>=</mo>
                            <msup>
                                <mi>x</mi>
                                <mn>2</mn>
                            </msup>
                            <mo>-</mo>
                            <mi>x</mi>
                            <mo>-</mo>
                            <mn>6</mn>
                        </mrow>
                    </mtd>
                </mtr>
                <mtr>
                    <mtd>
                        <mrow>
                            <mo>=</mo>
                            <mo stretchy="false">(</mo>
                            <mi>x</mi>
                            <mo>+</mo>
                            <mn>2</mn>
                            <mo stretchy="false">)</mo>
                            <mo stretchy="false">(</mo>
                            <mi>x</mi>
                            <mo>-</mo>
                            <mn>3</mn>
                            <mo stretchy="false">)</mo>
                        </mrow>
                    </mtd>
                </mtr>
            </mtable>
        </math>
        """
    },
    {
        "name": "Calculus Expression",
        "mathml": """
        <math>
            <mrow>
                <munderover>
                    <mo>∫</mo>
                    <mn>0</mn>
                    <mi>∞</mi>
                </munderover>
                <msup>
                    <mi>e</mi>
                    <mrow>
                        <mo>-</mo>
                        <mi>x</mi>
                    </mrow>
                </msup>
                <mi>d</mi>
                <mi>x</mi>
                <mo>=</mo>
                <munder>
                    <mo>lim</mo>
                    <mrow>
                        <mi>n</mi>
                        <mo>→</mo>
                        <mi>∞</mi>
                    </mrow>
                </munder>
                <mfrac>
                    <mn>1</mn>
                    <mi>n</mi>
                </mfrac>
            </mrow>
        </math>
        """
    },
    {
        "name": "Matrix Operation",
        "mathml": """
        <math>
            <mrow>
                <mo>[</mo>
                <mtable>
                    <mtr>
                        <mtd><mi>a</mi></mtd>
                        <mtd><mi>b</mi></mtd>
                    </mtr>
                    <mtr>
                        <mtd><mi>c</mi></mtd>
                        <mtd><mi>d</mi></mtd>
                    </mtr>
                </mtable>
                <mo>]</mo>
                <mo>×</mo>
                <mo>[</mo>
                <mtable>
                    <mtr>
                        <mtd><mi>x</mi></mtd>
                    </mtr>
                    <mtr>
                        <mtd><mi>y</mi></mtd>
                    </mtr>
                </mtable>
                <mo>]</mo>
                <mo>=</mo>
                <mo>[</mo>
                <mtable>
                    <mtr>
                        <mtd>
                            <mrow>
                                <mi>a</mi>
                                <mi>x</mi>
                                <mo>+</mo>
                                <mi>b</mi>
                                <mi>y</mi>
                            </mrow>
                        </mtd>
                    </mtr>
                    <mtr>
                        <mtd>
                            <mrow>
                                <mi>c</mi>
                                <mi>x</mi>
                                <mo>+</mo>
                                <mi>d</mi>
                                <mi>y</mi>
                            </mrow>
                        </mtd>
                    </mtr>
                </mtable>
                <mo>]</mo>
            </mrow>
        </math>
        """
    },
    {
        "name": "Multi-line Proof",
        "mathml": """
        <math>
            <mtable columnalign="left">
                <mtr>
                    <mtd>
                        <mtext>Prove: </mtext>
                        <mrow>
                            <msup>
                                <mi>a</mi>
                                <mn>2</mn>
                            </msup>
                            <mo>+</mo>
                            <msup>
                                <mi>b</mi>
                                <mn>2</mn>
                            </msup>
                            <mo>≥</mo>
                            <mn>2</mn>
                            <mi>a</mi>
                            <mi>b</mi>
                        </mrow>
                    </mtd>
                </mtr>
                <mtr>
                    <mtd>
                        <mrow>
                            <msup>
                                <mi>a</mi>
                                <mn>2</mn>
                            </msup>
                            <mo>+</mo>
                            <msup>
                                <mi>b</mi>
                                <mn>2</mn>
                            </msup>
                            <mo>-</mo>
                            <mn>2</mn>
                            <mi>a</mi>
                            <mi>b</mi>
                            <mo>≥</mo>
                            <mn>0</mn>
                        </mrow>
                    </mtd>
                </mtr>
                <mtr>
                    <mtd>
                        <mrow>
                            <mo stretchy="false">(</mo>
                            <mi>a</mi>
                            <mo>-</mo>
                            <mi>b</mi>
                            <mo stretchy="false">)</mo>
                            <msup>
                                <mrow>
                                    <mo stretchy="false">(</mo>
                                    <mi>a</mi>
                                    <mo>-</mo>
                                    <mi>b</mi>
                                    <mo stretchy="false">)</mo>
                                </mrow>
                                <mrow></mrow>
                            </msup>
                            <mo>≥</mo>
                            <mn>0</mn>
                        </mrow>
                    </mtd>
                </mtr>
                <mtr>
                    <mtd>
                        <mtext>∴ Proved</mtext>
                    </mtd>
                </mtr>
            </mtable>
        </math>
        """
    },
    {
        "name": "Multi-Column Layout",
        "mathml": """
        <math>
            <mtable columnalign="center center right" columnspacing="2em">
                <mtr>
                    <mtd>
                        <mtext>Function</mtext>
                    </mtd>
                    <mtd>
                        <mtext>Derivative</mtext>
                    </mtd>
                    <mtd>
                        <mtext>Domain</mtext>
                    </mtd>
                </mtr>
                <mtr>
                    <mtd>
                        <mrow>
                            <mi>f</mi>
                            <mo>(</mo>
                            <mi>x</mi>
                            <mo>)</mo>
                            <mo>=</mo>
                            <msup>
                                <mi>x</mi>
                                <mn>2</mn>
                            </msup>
                        </mrow>
                    </mtd>
                    <mtd>
                        <mrow>
                            <mi>f'</mi>
                            <mo>(</mo>
                            <mi>x</mi>
                            <mo>)</mo>
                            <mo>=</mo>
                            <mn>2</mn>
                            <mi>x</mi>
                        </mrow>
                    </mtd>
                    <mtd>
                        <mrow>
                            <mo>(</mo>
                            <mo>-</mo>
                            <mi>∞</mi>
                            <mo>,</mo>
                            <mi>∞</mi>
                            <mo>)</mo>
                        </mrow>
                    </mtd>
                </mtr>
                <mtr>
                    <mtd>
                        <mrow>
                            <mi>g</mi>
                            <mo>(</mo>
                            <mi>x</mi>
                            <mo>)</mo>
                            <mo>=</mo>
                            <mi>sin</mi>
                            <mo>(</mo>
                            <mi>x</mi>
                            <mo>)</mo>
                        </mrow>
                    </mtd>
                    <mtd>
                        <mrow>
                            <mi>g'</mi>
                            <mo>(</mo>
                            <mi>x</mi>
                            <mo>)</mo>
                            <mo>=</mo>
                            <mi>cos</mi>
                            <mo>(</mo>
                            <mi>x</mi>
                            <mo>)</mo>
                        </mrow>
                    </mtd>
                    <mtd>
                        <mrow>
                            <mo>(</mo>
                            <mo>-</mo>
                            <mi>∞</mi>
                            <mo>,</mo>
                            <mi>∞</mi>
                            <mo>)</mo>
                        </mrow>
                    </mtd>
                </mtr>
                <mtr>
                    <mtd>
                        <mrow>
                            <mi>h</mi>
                            <mo>(</mo>
                            <mi>x</mi>
                            <mo>)</mo>
                            <mo>=</mo>
                            <msqrt>
                                <mi>x</mi>
                            </msqrt>
                        </mrow>
                    </mtd>
                    <mtd>
                        <mrow>
                            <mi>h'</mi>
                            <mo>(</mo>
                            <mi>x</mi>
                            <mo>)</mo>
                            <mo>=</mo>
                            <mfrac>
                                <mn>1</mn>
                                <mrow>
                                    <mn>2</mn>
                                    <msqrt>
                                        <mi>x</mi>
                                    </msqrt>
                                </mrow>
                            </mfrac>
                        </mrow>
                    </mtd>
                    <mtd>
                        <mrow>
                            <mo>[</mo>
                            <mn>0</mn>
                            <mo>,</mo>
                            <mi>∞</mi>
                            <mo>)</mo>
                        </mrow>
                    </mtd>
                </mtr>
            </mtable>
        </math>
        """
    }
]

# HTML template for the test page
TEST_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MathML Rendering Tests</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/mml-svg.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test-case {
            border: 1px solid #ccc;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
        }
        .test-name {
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .mathml-source {
            font-family: monospace;
            background: #f5f5f5;
            padding: 10px;
            margin: 10px 0;
            white-space: pre-wrap;
            font-size: 12px;
        }
        .render-area {
            padding: 10px;
            background: white;
            min-height: 50px;
        }
    </style>
</head>
<body>
    <h1>MathML Rendering Test Suite</h1>
    <p>This page tests various MathML expressions to verify proper rendering.</p>
    
    {% for test in tests %}
    <div class="test-case">
        <div class="test-name">{{ test.name }}</div>
        <div class="mathml-source">{{ test.mathml }}</div>
        <div class="render-area">
            {{ test.mathml|safe }}
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def test_page():
    return render_template_string(TEST_PAGE_TEMPLATE, tests=TEST_CASES)

def main():
    # Start the Flask app
    port = 5050
    url = f'http://localhost:{port}'
    
    print(f"Starting MathML rendering test server at {url}")
    print("Opening test page in browser...")
    
    # Open the browser
    webbrowser.open(url)
    
    # Run the Flask app
    app.run(port=port)

if __name__ == '__main__':
    main()
