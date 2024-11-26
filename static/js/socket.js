class MathboardSocket {
    constructor(elements) {
        this.socket = io();
        this.stepQueue = [];
        this.currentRequestId = null;
        this.elements = elements;
        this.setupSocketListeners();
        console.log('[Socket] Initialized MathboardSocket');
    }

    setupSocketListeners() {
        // Handle connection errors
        this.socket.on('connect_error', (error) => {
            this.showError('Connection error. Please try again later.');
            console.log('[Socket Error] Connection error:', error);
        });

        // Handle receiving steps from the server
        this.socket.on('display_step', (data) => {
            console.log(`[Socket] Received step for request ${data.requestId}:`, {
                currentRequestId: this.currentRequestId,
                queueLength: this.stepQueue.length,
                stepData: data,
                hasAudio: data.hasAudio,
                audioLength: data.audioLength,
                audioDataPresent: !!data.audio,
                audioDataLength: data.audio ? data.audio.length : 0
            });
            
            // Only process steps for current request
            if (data.requestId === this.currentRequestId) {
                this.addStepToQueue(data);
            } else {
                console.log(`[Socket] Ignoring step from old request ${data.requestId}`);
            }
        });

        this.socket.on('error', (error) => {
            console.error('[Socket] Error:', error);
            this.showError('An error occurred. Please try again.');
        });
    }

    addStepToQueue(data) {
        console.log('[Queue] Adding step to queue:', {
            queueLengthBefore: this.stepQueue.length,
            newStep: data
        });
        
        this.stepQueue.push(data);
        
        // If this is the first step, display it immediately
        if (this.stepQueue.length === 1) {
            console.log('[Queue] First step - displaying immediately');
            this.displayCurrentStep();
        }
        
        // Enable the next step button if there are more steps
        this.updateNextStepButton();
        
        console.log('[Queue] Queue state after add:', {
            queueLength: this.stepQueue.length,
            currentStep: this.stepQueue[0]
        });
    }

    playAudio(base64Audio) {
        return new Promise((resolve, reject) => {
            if (!base64Audio) {
                console.log('No audio data provided');
                resolve();
                return;
            }

            try {
                console.log('Starting audio playback, base64 length:', base64Audio.length);
                
                // Validate base64 string
                try {
                    atob(base64Audio.slice(0, 100));
                    console.log('Validated base64 encoding');
                } catch (e) {
                    console.error('Invalid base64 encoding:', e);
                    resolve();
                    return;
                }
                
                // Convert base64 to blob
                const byteCharacters = atob(base64Audio);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: 'audio/mp3' });
                console.log('Created audio blob of size:', blob.size);
                
                // Create audio element
                const audio = new Audio(URL.createObjectURL(blob));
                
                audio.oncanplay = () => {
                    console.log('Audio ready to play, duration:', audio.duration);
                };
                
                audio.onended = () => {
                    console.log('Audio playback completed');
                    URL.revokeObjectURL(audio.src); // Clean up the blob URL
                    resolve();
                };

                audio.onerror = (error) => {
                    console.error('Audio playback error:', error);
                    URL.revokeObjectURL(audio.src);
                    resolve();
                };

                console.log('Starting audio playback');
                audio.play().catch(error => {
                    console.error('Error playing audio:', error);
                    resolve();
                });
            } catch (error) {
                console.error('Error in audio playback:', error);
                resolve();
            }
        });
    }

    async displayCurrentStep() {
        if (this.stepQueue.length === 0) {
            console.log('[Display] No steps to display');
            return;
        }

        const data = this.stepQueue[0];
        console.log('[Display] Displaying step:', data);

        const { mathWhiteboard, explanationDisplay } = this.elements;
        const loadingSpinner = document.querySelector('.loading-spinner');
        
        // Hide loading spinner
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        
        // Display math in whiteboard
        if (data.math && mathWhiteboard) {
            console.log('[Display] Updating math content');
            try {
                mathWhiteboard.innerHTML = '';
                const mathElement = document.createElement('div');
                mathElement.textContent = data.math;
                mathWhiteboard.appendChild(mathElement);
                
                // Trigger MathJax processing
                if (window.MathJax) {
                    console.log('[MathJax] Starting typeset');
                    await window.MathJax.typesetPromise([mathWhiteboard]);
                    console.log('[MathJax] Completed typeset');
                } else {
                    console.error('[MathJax] Not loaded');
                    this.showError('Error displaying mathematical content');
                }
            } catch (error) {
                console.error('[Display] Error displaying math:', error);
                this.showError('Error displaying mathematical content');
            }
        }
        
        // Display explanation
        if (data.natural && explanationDisplay) {
            console.log('[Display] Updating explanation');
            explanationDisplay.textContent = data.natural;
        }

        // Play audio if available
        if (data.hasAudio && data.audio) {
            console.log('Attempting to play audio');
            try {
                await this.playAudio(data.audio);
            } catch (error) {
                console.error('Error during audio playback:', error);
            }
        } else {
            console.log('No audio data available for this step');
        }
    }

    nextStep() {
        console.log('[Navigation] Next step requested', {
            queueLengthBefore: this.stepQueue.length,
            currentStep: this.stepQueue[0]
        });
        
        // Remove the current step and show the next one
        if (this.stepQueue.length > 0) {
            this.stepQueue.shift();
            console.log('[Navigation] Moved to next step', {
                queueLengthAfter: this.stepQueue.length,
                newCurrentStep: this.stepQueue[0]
            });
            this.displayCurrentStep();
            this.updateNextStepButton();
        }
    }

    updateNextStepButton() {
        const { nextStepButton } = this.elements;
        if (nextStepButton) {
            // Enable button if there are more steps in the queue
            const shouldEnable = this.stepQueue.length > 1;
            nextStepButton.disabled = !shouldEnable;
            console.log('[UI] Next step button updated:', {
                enabled: shouldEnable,
                queueLength: this.stepQueue.length
            });
        }
    }

    showError(message) {
        console.error('[Error] Displaying error:', message);
        const { errorDisplay } = this.elements;
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

        console.log('[Query] Sending new math query:', query);

        const { mathWhiteboard, explanationDisplay, nextStepButton } = this.elements;
        const loadingSpinner = document.querySelector('.loading-spinner');

        // Generate new request ID
        this.currentRequestId = Date.now().toString();
        console.log('[Query] Generated new request ID:', this.currentRequestId);

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
        console.log('[Query] Clearing step queue');
        this.stepQueue = [];

        // Emit the question to the server
        console.log('[Query] Emitting request_math event', {
            requestId: this.currentRequestId,
            prompt: query
        });
        this.socket.emit('request_math', { 
            prompt: query,
            requestId: this.currentRequestId
        });
    }
}

// Only create a single instance that can be shared
let instance = null;

export default class {
    constructor(elements) {
        if (!instance) {
            instance = new MathboardSocket(elements);
        }
        return instance;
    }
}
