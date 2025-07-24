// static/js/script.js
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');
    const micStatus = document.getElementById('mic-status');
    const voiceToggle = document.createElement('button'); // Create voice toggle button dynamically

    // Voice Control State
    let recognition = null;
    let isListening = false;
    let voiceEnabled = true;
    let synth = window.speechSynthesis;
    let voices = [];
    let currentUtterance = null;

    // Add Voice Toggle Button to DOM
    voiceToggle.id = 'voice-toggle';
    voiceToggle.title = 'Toggle Voice Response';
    voiceToggle.innerHTML = '<i class="bx bxs-volume-full"></i>';
    document.querySelector('.input-area').appendChild(voiceToggle);

    // --- Initialize Speech Recognition ---
    function initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = () => {
                isListening = true;
                micButton.classList.add('listening');
                micStatus.textContent = 'Listening...';
                micStatus.style.display = 'block';
                userInput.placeholder = "Listening...";
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
                sendMessage(transcript);
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                let errorMessage = 'Speech recognition error';
                if (event.error === 'no-speech') {
                    errorMessage = 'No speech detected';
                } else if (event.error === 'audio-capture') {
                    errorMessage = 'Microphone not available';
                } else if (event.error === 'not-allowed') {
                    errorMessage = 'Microphone access denied';
                }
                showTemporaryMessage(errorMessage, 3000);
            };

            recognition.onend = () => {
                isListening = false;
                micButton.classList.remove('listening');
                micStatus.style.display = 'none';
                userInput.placeholder = "Type your message or use the mic...";
            };
        } else {
            micButton.disabled = true;
            micButton.title = 'Voice input not supported';
            showTemporaryMessage('Voice input not supported in this browser', 3000);
        }
    }

    // --- Initialize Speech Synthesis ---
    function initSpeechSynthesis() {
        if (typeof synth === 'undefined') {
            voiceToggle.disabled = true;
            voiceToggle.title = 'Voice output not supported';
            showTemporaryMessage('Voice output not supported in this browser', 3000);
            return;
        }

        function populateVoices() {
            voices = synth.getVoices();
            // Optional: You could set a default voice here
        }

        populateVoices();
        if (synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = populateVoices;
        }
    }

    // --- Voice Output Control ---
    function speakText(text) {
        if (!voiceEnabled || !synth || !text) return;

        if (synth.speaking) {
            synth.cancel();
        }

        currentUtterance = new SpeechSynthesisUtterance(text);
        currentUtterance.voice = voices.find(v => v.lang.includes('en')) || voices[0];
        currentUtterance.pitch = 1;
        currentUtterance.rate = 1;
        currentUtterance.volume = 1;

        currentUtterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            showTemporaryMessage('Error with voice output', 2000);
        };

        synth.speak(currentUtterance);
    }

    function toggleVoiceOutput() {
        voiceEnabled = !voiceEnabled;
        voiceToggle.classList.toggle('muted');
        voiceToggle.innerHTML = voiceEnabled ? 
            '<i class="bx bxs-volume-full"></i>' : 
            '<i class="bx bxs-volume-mute"></i>';
        
        if (!voiceEnabled && synth.speaking) {
            synth.cancel();
        }
        
        showTemporaryMessage(`Voice response ${voiceEnabled ? 'ON' : 'OFF'}`, 1500);
        localStorage.setItem('voiceEnabled', voiceEnabled);
    }

    // --- Helper Functions ---
    function showTemporaryMessage(message, duration) {
        const statusElement = document.createElement('div');
        statusElement.className = 'message status-message';
        statusElement.textContent = message;
        chatHistory.appendChild(statusElement);
        
        setTimeout(() => {
            statusElement.remove();
        }, duration);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function displayMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        messageElement.appendChild(paragraph);

        chatHistory.appendChild(messageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // --- Event Listeners ---
    voiceToggle.addEventListener('click', toggleVoiceOutput);
    
    sendButton.addEventListener('click', () => {
        const messageText = userInput.value.trim();
        if (messageText) sendMessage(messageText);
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && userInput.value.trim()) {
            sendMessage(userInput.value.trim());
        }
    });

    micButton.addEventListener('click', () => {
        if (!recognition) return;
        
        if (isListening) {
            recognition.stop();
        } else {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(() => recognition.start())
                .catch(err => {
                    console.error("Microphone access denied:", err);
                    showTemporaryMessage('Microphone access denied', 3000);
                });
        }
    });

    // --- Main Chat Function ---
    async function sendMessage(messageText) {
        displayMessage(messageText, 'user');
        userInput.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.message || 'Request failed');
            }

            const data = await response.json();
            if (data.response) {
                displayMessage(data.response, 'bot');
                speakText(data.response);
            }
        } catch (error) {
            console.error('Chat error:', error);
            displayMessage(`Error: ${error.message || 'Failed to get response'}`, 'error');
        }
    }

    // --- Initialize ---
    function init() {
        // Load voice preference
        if (localStorage.getItem('voiceEnabled') !== null) {
            voiceEnabled = localStorage.getItem('voiceEnabled') === 'true';
            if (!voiceEnabled) {
                voiceToggle.classList.add('muted');
                voiceToggle.innerHTML = '<i class="bx bxs-volume-mute"></i>';
            }
        }

        initSpeechRecognition();
        initSpeechSynthesis();
    }

    init();
});