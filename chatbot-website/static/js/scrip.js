// static/js/script.js
document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');
    const micStatus = document.getElementById('mic-status');

    let recognition = null;
    let isListening = false;

    // --- Initialize Speech Recognition ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false; // Process single utterance
        recognition.lang = 'en-US';     // Set language
        recognition.interimResults = false; // We only want final results
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            isListening = true;
            micButton.classList.add('listening');
            micStatus.textContent = 'Listening...';
            micStatus.style.display = 'block';
            micButton.disabled = true; // Disable while listening
            userInput.placeholder = "Listening...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript; // Put recognized text in input field
            // Automatically send the message after recognition
            sendMessage(transcript); 
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            let errorMessage = 'Speech recognition error';
            if (event.error === 'no-speech') {
                errorMessage = 'No speech detected. Please try again.';
            } else if (event.error === 'audio-capture') {
                errorMessage = 'Microphone error. Please check permissions.';
            } else if (event.error === 'not-allowed') {
                errorMessage = 'Microphone access denied. Please allow access in browser settings.';
            }
            micStatus.textContent = errorMessage;
            micStatus.style.display = 'block';
            // Keep status visible for a bit longer on error
            setTimeout(() => {
                 if (!isListening) micStatus.style.display = 'none';
            }, 3000);
        };

        recognition.onend = () => {
            isListening = false;
            micButton.classList.remove('listening');
            micStatus.style.display = 'none'; // Hide status when done
            micButton.disabled = false; // Re-enable button
            userInput.placeholder = "Type your message or use the mic...";
        };

    } else {
        console.warn('Speech Recognition API not supported in this browser.');
        micButton.disabled = true;
        micButton.title = 'Voice input not supported by your browser';
    }

    // --- Initialize Speech Synthesis ---
    const synth = window.speechSynthesis;
    let voices = [];

    function populateVoiceList() {
        if(typeof speechSynthesis === 'undefined') {
           console.warn('Speech Synthesis API not supported.');
           return;
        }
        voices = synth.getVoices();
        // You could add logic here to select a specific voice if desired
        // console.log("Available voices:", voices);
    }

    populateVoiceList();
    if (typeof speechSynthesis !== 'undefined' && speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = populateVoiceList;
    }

    function speakText(text) {
        if (!synth || !text) return; // Don't speak if API not supported or text is empty

        // Cancel any previous speech
        if (synth.speaking) {
            console.log("Cancelling previous speech");
            synth.cancel();
        }

        const utterThis = new SpeechSynthesisUtterance(text);

        utterThis.onerror = (event) => {
            console.error('SpeechSynthesis Error:', event);
        };

        // Optional: Select a specific voice (e.g., the first English voice)
        const englishVoice = voices.find(voice => voice.lang.includes('en') && voice.name.includes('Google') ) || voices.find(voice => voice.lang.includes('en')); // Fallback
        if (englishVoice) {
            utterThis.voice = englishVoice;
            // console.log("Using voice:", englishVoice.name);
        } else {
            // console.log("Using default voice");
        }

        utterThis.pitch = 1;
        utterThis.rate = 1; // Adjust speed (0.1 to 10)

        // Ensure speaking happens after a very short delay, sometimes helps with interruptions
        setTimeout(() => synth.speak(utterThis), 50); 
    }


    // --- Event Listeners ---
    sendButton.addEventListener('click', () => {
        const messageText = userInput.value.trim();
        if (messageText) {
            sendMessage(messageText);
        }
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const messageText = userInput.value.trim();
            if (messageText) {
                sendMessage(messageText);
            }
        }
    });

    micButton.addEventListener('click', () => {
        if (!recognition) return;

        if (isListening) {
            recognition.stop(); // Manually stop if already listening
        } else {
            // Request microphone permission explicitly if needed (good practice)
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(() => {
                    recognition.start();
                })
                .catch(err => {
                    console.error("Microphone access denied:", err);
                    micStatus.textContent = 'Microphone access denied. Please allow access.';
                    micStatus.style.display = 'block';
                    setTimeout(() => micStatus.style.display = 'none', 3000);
                });
        }
    });

    // --- Core Functions ---
    function displayMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        messageElement.appendChild(paragraph);

        chatHistory.appendChild(messageElement);
        // Scroll to the bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    async function sendMessage(messageText) {
        if (!messageText) return;

        // Display user message immediately
        displayMessage(messageText, 'user');
        userInput.value = ''; // Clear input field

        // Optional: Show a thinking indicator for the bot
        // displayMessage("...", 'bot-thinking'); // You'd need CSS for .bot-thinking

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText }),
            });

            // Remove thinking indicator if you added one
            // const thinkingIndicator = chatHistory.querySelector('.bot-thinking');
            // if (thinkingIndicator) thinkingIndicator.remove();

            if (!response.ok) {
                // Handle HTTP errors (like 401 Unauthorized, 500 Internal Server Error)
                let errorMsg = `Error: ${response.status} ${response.statusText}`;
                 try { // Try to get more specific error from JSON body
                     const errorData = await response.json();
                     errorMsg = errorData.error || errorData.response || errorMsg;
                 } catch (e) { /* Ignore if body isn't JSON */ }
                console.error('Chat API error:', errorMsg);
                displayMessage(`Sorry, I encountered an error: ${errorMsg}`, 'error'); // Use 'error' class
                return; // Stop processing on error
            }

            const data = await response.json();
            const botResponse = data.response;

            if (botResponse) {
                displayMessage(botResponse, 'bot');
                speakText(botResponse); // Speak the bot's response
            } else if (data.error) {
                 displayMessage(`Error: ${data.error}`, 'error');
            }


        } catch (error) {
            // Handle network errors or other fetch issues
            console.error('Failed to send message:', error);
            // Remove thinking indicator if it exists
            // const thinkingIndicator = chatHistory.querySelector('.bot-thinking');
            // if (thinkingIndicator) thinkingIndicator.remove();
            displayMessage('Sorry, I couldn\'t connect to the server. Please check your connection.', 'error');
        }
    }

     // --- Initial bot message ---
     // Moved the initial message to the HTML template for simplicity
     // speakText("Hello! How can I help you manage the hospital records today?"); // Optional: Speak initial greeting
});