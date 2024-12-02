class MathboardSocket {
    constructor(elements) {
        this.socket = io();
        this.stepQueue = [];
        this.stepHistory = [];
        this.currentStepIndex = -1;
        this.currentRequestId = null;
        this.elements = elements;
        this.currentAudioData = null;
        this.isPlayingAudio = false;
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
                format: data.mathml ? 'MathML' : 'LaTeX',
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
        
        // Add to queue
        this.stepQueue.push(data);
        
        // If this is the first step, add it to history and display it
        if (this.stepQueue.length === 1 && this.stepHistory.length === 0) {
            const firstStep = this.stepQueue.shift();
            this.stepHistory.push(firstStep);
            this.currentStepIndex = 0;
            this.displayCurrentStep();
        }
        
        // Update navigation buttons
        this.updateNavigationButtons();
        
        console.log('[Queue] Queue state after add:', {
            queueLength: this.stepQueue.length,
            historyLength: this.stepHistory.length,
            currentIndex: this.currentStepIndex
        });
    }

    parseMathML(mathmlString) {
        // Create a temporary container
        const parser = new DOMParser();
        const doc = parser.parseFromString(mathmlString, 'application/xml');
        
        // Check for parsing errors
        const parseError = doc.querySelector('parsererror');
        if (parseError) {
            console.error('[MathML] Parse error:', parseError);
            return null;
        }
        
        return doc.documentElement;
    }

    async displayCurrentStep() {
        if (this.stepHistory.length === 0 || this.currentStepIndex < 0) {
            console.log('[Display] No steps to display');
            return;
        }

        const data = this.stepHistory[this.currentStepIndex];
        console.log('[Display] Displaying step:', data);

        const { mathWhiteboard } = this.elements;
        const loadingSpinner = document.querySelector('.loading-spinner');
        const replayButton = document.getElementById('replayAudioButton');
        
        // Hide loading spinner
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        
        // Display math in whiteboard
        if (mathWhiteboard) {
            console.log('[Display] Updating math content');
            try {
                mathWhiteboard.innerHTML = '';
                const container = document.createElement('div');

                // Handle MathML content if available, fallback to LaTeX
                if (data.mathml) {
                    console.log('[Display] Using MathML content');
                    const mathmlElement = this.parseMathML(data.mathml);
                    if (mathmlElement) {
                        // Create a math element with proper namespace
                        const mathElement = document.createElementNS('http://www.w3.org/1998/Math/MathML', 'math');
                        // Import the parsed MathML into the current document
                        const importedMathML = document.importNode(mathmlElement, true);
                        mathElement.appendChild(importedMathML);
                        container.appendChild(mathElement);
                    } else {
                        console.error('[Display] Failed to parse MathML, falling back to LaTeX');
                        container.textContent = data.math || 'Error displaying mathematical content';
                    }
                } else if (data.math) {
                    console.log('[Display] Falling back to LaTeX content');
                    container.textContent = data.math;
                }

                mathWhiteboard.appendChild(container);
                
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

        // Store current audio data and update replay button
        this.currentAudioData = data.audio;
        if (replayButton) {
            replayButton.disabled = !data.hasAudio || this.isPlayingAudio;
            replayButton.onclick = () => this.replayCurrentAudio();
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

    async playAudio(base64Audio) {
        return new Promise((resolve, reject) => {
            if (!base64Audio) {
                console.log('No audio data provided');
                resolve();
                return;
            }

            try {
                console.log('Starting audio playback, base64 length:', base64Audio.length);
                this.isPlayingAudio = true;
                this.updateNavigationButtons();
                
                // Validate base64 string
                try {
                    atob(base64Audio.slice(0, 100));
                    console.log('Validated base64 encoding');
                } catch (e) {
                    console.error('Invalid base64 encoding:', e);
                    this.isPlayingAudio = false;
                    this.updateNavigationButtons();
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
                    URL.revokeObjectURL(audio.src);
                    this.isPlayingAudio = false;
                    this.updateNavigationButtons();
                    resolve();
                };

                audio.onerror = (error) => {
                    console.error('Audio playback error:', error);
                    URL.revokeObjectURL(audio.src);
                    this.isPlayingAudio = false;
                    this.updateNavigationButtons();
                    resolve();
                };

                console.log('Starting audio playback');
                audio.play().catch(error => {
                    console.error('Error playing audio:', error);
                    this.isPlayingAudio = false;
                    this.updateNavigationButtons();
                    resolve();
                });
            } catch (error) {
                console.error('Error in audio playback:', error);
                this.isPlayingAudio = false;
                this.updateNavigationButtons();
                resolve();
            }
        });
    }

    async replayCurrentAudio() {
        if (this.currentAudioData && !this.isPlayingAudio) {
            console.log('[Audio] Replaying current step audio');
            const replayButton = document.getElementById('replayAudioButton');
            if (replayButton) {
                replayButton.disabled = true;
            }
            
            try {
                await this.playAudio(this.currentAudioData);
            } catch (error) {
                console.error('Error replaying audio:', error);
            }
            
            if (replayButton) {
                replayButton.disabled = false;
            }
        } else {
            console.log('[Audio] No audio data available to replay or audio is currently playing');
        }
    }

    async nextStep() {
        console.log('[Navigation] Next step requested');
        
        // Don't proceed if audio is still playing
        if (this.isPlayingAudio) {
            console.log('[Navigation] Waiting for audio to complete');
            return;
        }
        
        if (this.stepQueue.length > 0) {
            // Move next step to history
            const step = this.stepQueue.shift();
            this.stepHistory.push(step);
            this.currentStepIndex = this.stepHistory.length - 1;
            
            console.log('[Navigation] Moved to next step', {
                historyLength: this.stepHistory.length,
                currentIndex: this.currentStepIndex
            });
            
            await this.displayCurrentStep();
            this.updateNavigationButtons();
        }
    }

    async prevStep() {
        console.log('[Navigation] Previous step requested');
        
        // Don't proceed if audio is still playing
        if (this.isPlayingAudio) {
            console.log('[Navigation] Waiting for audio to complete');
            return;
        }
        
        if (this.currentStepIndex > 0) {
            this.currentStepIndex--;
            console.log('[Navigation] Moved to previous step', {
                historyLength: this.stepHistory.length,
                currentIndex: this.currentStepIndex
            });
            
            await this.displayCurrentStep();
            this.updateNavigationButtons();
        }
    }

    updateNavigationButtons() {
        const prevButton = document.getElementById('prevStepButton');
        const nextButton = document.getElementById('nextStepButton');
        const replayButton = document.getElementById('replayAudioButton');
        
        if (prevButton) {
            const canGoBack = this.currentStepIndex > 0 && !this.isPlayingAudio;
            prevButton.disabled = !canGoBack;
            if (canGoBack) {
                prevButton.onclick = () => this.prevStep();
            }
        }
        
        if (nextButton) {
            const canGoForward = this.stepQueue.length > 0 && !this.isPlayingAudio;
            nextButton.disabled = !canGoForward;
            if (canGoForward) {
                nextButton.onclick = () => this.nextStep();
            }
        }
        
        if (replayButton) {
            replayButton.disabled = !this.currentAudioData || this.isPlayingAudio;
        }
        
        console.log('[UI] Navigation buttons updated:', {
            prevEnabled: !prevButton?.disabled,
            nextEnabled: !nextButton?.disabled,
            replayEnabled: !replayButton?.disabled,
            historyLength: this.stepHistory.length,
            queueLength: this.stepQueue.length,
            currentIndex: this.currentStepIndex,
            isPlayingAudio: this.isPlayingAudio
        });
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

        const { mathWhiteboard } = this.elements;
        const loadingSpinner = document.querySelector('.loading-spinner');
        const replayButton = document.getElementById('replayAudioButton');

        // Generate new request ID
        this.currentRequestId = Date.now().toString();
        console.log('[Query] Generated new request ID:', this.currentRequestId);

        // Clear previous content and show loading
        if (mathWhiteboard) {
            mathWhiteboard.innerHTML = '';
        }
        if (loadingSpinner) {
            loadingSpinner.style.display = 'block';
        }

        // Reset state
        this.stepQueue = [];
        this.stepHistory = [];
        this.currentStepIndex = -1;
        this.currentAudioData = null;
        this.isPlayingAudio = false;
        this.updateNavigationButtons();
        
        if (replayButton) {
            replayButton.disabled = true;
        }

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
