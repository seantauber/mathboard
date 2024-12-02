# LaTeX to MathML Migration Plan

## Overview
This document outlines the step-by-step plan for migrating the MathBoard application from LaTeX to MathML rendering. The goal is to make minimal changes while maintaining current functionality.

## Current Architecture Analysis
The application currently uses:
1. MathJax for LaTeX rendering (frontend)
2. LaTeX utilities for validation and formatting (backend)
3. LaTeX-specific tools for the CrewAI agent
4. LaTeX string generation in task configurations

## Migration Steps

### Phase 1: Frontend Changes
1. **MathJax Configuration Update** ✓
   - Modify `static/js/mathjax-config.js`
   - Switch from tex-svg.js to mml-svg.js loader
   - Update configuration to handle MathML input

2. **Helper Functions Refactor** ✓
   - Rename `static/js/latex-helpers.js` to `math-helpers.js`
   - Update formatLatex() to formatMathML()
   - Modify validateLatex() to handle MathML validation
   - Update symbol insertion functions for MathML syntax

3. **UI Component Updates** ✓
   - Update symbol toolbar in `templates/index.html` to support MathML
   - Add data attributes for MathML syntax
   - Implement MathML preview functionality
   - Add format toggle during transition period

### Phase 2: Backend Utilities
1. **Math Utilities Refactor** ✓
   - Rename `src/utils/latex_utils.py` to `math_utils.py`
   - Update validation functions for MathML syntax
   - Modify sanitization for MathML security
   - Create MathML formatting functions
   - Keep LaTeX-to-MathML conversion utility for backward compatibility

2. **CrewAI Tools Update** ✓
   - Rename `src/crews/tools/latex_tools.py` to `math_tools.py`
   - Update tool classes to handle MathML
   - Modify validation and formatting logic
   - Update tool descriptions and documentation

### Phase 3: Task Configuration
1. **Update Task Descriptions** ✓
   - Modify `src/crews/config/tasks.yaml`
   - Update examples to use MathML syntax
   - Update format requirements section
   - Maintain structure of step outputs

### Phase 4: Testing & Validation
1. **Independent Test Implementation** ✓
   - Created frontend rendering test suite (`src/tests/test_mathml_rendering.py`):
     * Standalone test page with predefined MathML expressions
     * Direct MathJax rendering without WebSocket dependency
     * Coverage of different MathML features
     * Easy to run and inspect results
   
   - Created backend generation test suite (`src/tests/test_mathml_generation.py`):
     * Tests agent's MathML output independently
     * Saves results to timestamped files
     * Covers various mathematical concepts
     * Easy to inspect and debug output

   To run the tests:
   1. Frontend rendering test (no backend required):
      ```bash
      python src/tests/test_mathml_rendering.py
      ```
      This will open a browser window with test cases.
   
   2. Backend generation test (no frontend required):
      ```bash
      python src/tests/test_mathml_generation.py
      ```
      This will save results to test_output directory.

### Phase 5: Integration
1. **WebSocket Handler Updates** ✓
   - Modify `static/js/socket.js` to handle MathML:
     ```javascript
     socket.on('display_step', function(data) {
         if (data.mathml) {
             renderMathML(data.mathml);
         } else {
             renderLegacyLatex(data.latex);
         }
     });
     ```
   - Add format detection and handling
   - Implement graceful fallback

2. **Integration Testing**
   - End-to-end testing with WebSocket communication
   - Verify MathML flows correctly from backend to frontend
   - Test format detection and fallback
   - Monitor performance and error handling

### Phase 6: Deployment & Transition
1. **Feature Flags**
   - Implement toggle for MathML/LaTeX rendering
   - Add configuration for gradual rollout
   - Create monitoring dashboard

2. **Documentation Updates**
   - Update API documentation
   - Create MathML style guide
   - Update troubleshooting guides
   - Add migration guide for custom integrations

3. **Performance Optimization**
   - Implement MathML caching strategy
   - Optimize rendering pipeline
   - Add lazy loading for complex expressions
   - Implement batch processing for large sets

### Phase 7: Cleanup & Finalization
1. **Code Cleanup**
   - Remove LaTeX-specific code
   - Clean up transition helpers
   - Update naming conventions
   - Remove deprecated features

2. **Final Validation**
   - Full regression testing
   - Performance validation
   - Security audit
   - Accessibility testing

## Migration Progress Tracking

### Completed Tasks ✓
1. Phase 1.1: MathJax Configuration Update
2. Phase 1.2: Helper Functions Refactor
3. Phase 1.3: UI Component Updates
4. Phase 2.1: Math Utilities Refactor
5. Phase 2.2: CrewAI Tools Update
6. Phase 3.1: Update Task Descriptions
7. Phase 4.1: Independent Test Implementation
8. Phase 5.1: WebSocket Handler Updates

### In Progress
1. Phase 5.2: Integration Testing

### Pending
1. Phase 6-7: Deployment, Transition, and Cleanup

## Dependencies to Update
1. Replace tex-svg.js with mml-svg.js ✓
2. Add any required MathML validation libraries
3. Update testing dependencies if needed

## Backward Compatibility
1. Maintain LaTeX-to-MathML conversion utility
2. Keep support for LaTeX input temporarily
3. Add format detection for smooth transition

## Risks and Mitigations
1. **Risk**: MathML syntax complexity
   - Mitigation: Comprehensive validation
   
2. **Risk**: Rendering inconsistencies
   - Mitigation: Thorough testing across browsers

3. **Risk**: Performance impact
   - Mitigation: Performance testing before deployment

## Success Criteria
1. All mathematical expressions render correctly
2. Agent generates valid MathML
3. No degradation in performance
4. Maintains current functionality
5. Clean error handling

## Future Considerations
1. Phase out LaTeX support
2. Enhance MathML capabilities
3. Optimize rendering performance
4. Add advanced MathML features
