from Speach import SpeechToText 
id = 34
user_input_value = ""
def user_input():
    clicked = 0  # Not really used here, keeping your logic as is
    if clicked == 1:
        user_input_value = SpeechToText()
    else:
        user_input_value = input("Enter your text: ")
    return user_input_value

if __name__ == "__main__":
    user_input()
from Speach import SpeechToText # Assuming renamed
# id = 34 # This variable 'id' is defined but not used in this file.
# user_input_value = "" # Global variable, generally avoid if possible

def user_input(use_speech=False): # Add a parameter to control speech input
    if use_speech:
        print("Attempting to use speech input...") # For CLI feedback
        user_val = SpeechToText()
        if user_val:
            return user_val
        else:
            print("Speech input failed or was empty, falling back to text input.")
            return input("Enter your text: ") # Fallback
    else:
        return input("Enter your text: ")

if __name__ == "__main__":
    # Example of how to use it:
    # text_input = user_input()
    # print(f"Text input received: {text_input}")

    speech_input_attempt = user_input(use_speech=True)
    print(f"Input received (might be speech or fallback text): {speech_input_attempt}")
'''
This `input.py` is likely for testing `main.py` (the standalone script) and not directly used by the Flask web app, which uses `script.js` for user input.
    
    '''