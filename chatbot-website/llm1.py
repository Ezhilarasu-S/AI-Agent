import google.generativeai as genai
import os
import re
import json
import dict
import logging 
from Voice import speak_with_selected_voice
from dotenv import load_dotenv 

load_dotenv() 

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
OUTPUT_JSON_PATH = 'output.json' # Define path consistently relative to app.py

# --- API Key Setup ---
# It's best practice to load API keys from environment variables.
API_KEY = None
MODEL = None
try:
    # Attempt to get key from environment variable first
    API_KEY = os.environ.get("GEMINI_API_KEY","AIzaSyAQIhHBXknZo1Znv9SAdsNrnVO-JYyJu-o")
    if not API_KEY:
        raise ValueError("Gemini API Key not found in environment variable GEMINI_API_KEY.")

    genai.configure(api_key=API_KEY)
    # Initialize the specific model you want to use
    MODEL = genai.GenerativeModel('gemini-2.5-flash') # Or other suitable model
    logging.info("Google Generative AI configured successfully.")

except ValueError as ve:
     logging.error(f"Configuration Error: {ve}")
     # Application might not function correctly without the LLM.
except Exception as e:
    logging.error(f"FATAL ERROR: Failed to configure Google Generative AI: {e}", exc_info=True)
    # Ensure MODEL remains None if setup fails


os.environ["GEMINI_API_KEY"] = "AIzaSyAQIhHBXknZo1Znv9SAdsNrnVO-JYyJu-o"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')


def configure_and_generate(user_text):
    prompt = generate_prompt(user_text)
    response = model.generate_content(prompt)
    save_response_json(response.text)
    return response

def generate_output_text(output_text, model=None):
    """
    Either directly return a clean response or enhance it using LLM if needed.
    
    Args:
        output_text: The raw output to process (can be str, dict, or other types)
        model: Optional LLM model for enhancement (if None, will skip LLM step)
    
    Returns:
        str: User-friendly formatted text
    """
    prompt = generate_output(output_text)
    
    # Check for already user-friendly formats
    if isinstance(prompt, str) and any(prompt.startswith(emoji) for emoji in ("✅", "❌", "ℹ️", "🔹")):
        return prompt
    
    # Skip LLM enhancement if no model provided
    if model is None:
        return prompt
    
    # Otherwise use LLM to reword it nicely
    try:
        response = model.generate_content(prompt)
        final_text = ""
        
        if hasattr(response, "parts") and response.parts:
            final_text = "".join(part.text for part in response.parts)
        elif hasattr(response, 'text'):
            final_text = response.text
        else:
            final_text = prompt
            
        return final_text.strip()
    
    except Exception as e:
        # Fallback to original prompt if LLM fails
        print(f"LLM enhancement failed: {str(e)}")
        return prompt


def generate_output(output_text):
    """
    Generate a concise, user-friendly output message from various response types.
    
    Args:
        output_text: Raw output (str, dict, list, etc.)
    
    Returns:
        str: Formatted text ready for user or further LLM processing
    """
    if output_text is None:
        return "❌ No output received"
        
    return str(output_text).strip()


def generate_prompt(user_text): 
    """
    First identify the SQL table from the text: patient, doctor, appointment, or bill.
    Then identify the operation: insert (also appears as add), update (also appears as change), view (also appears as show, extract, info about).

    Only one operation should be extracted per request.

    Extract the relevant information and return it as JSON based on the table and operation:

    For table: patient
    - Insert: { "operation": "insert", "table": "patient", "data": { "id": ..., "name": ..., "age": ..., "gender": ..., "address": ..., "contact": ... } }    
    For patient insert operations, ensure all required fields (name, age, gender, contact, address)  
    have non-null values. If gender is unspecified, use 'Unknown' as default
    - Update: { "operation": "update", "table": "patient", "data": {"id": ..., {"field"}: {"value"}... } }
    - View:   { "operation": "view", "table": "patient","data": { "id": ... }}


    For table: doctor
    - Insert: { "operation": "insert", "table": "doctor", "data": { "doctor_id": ..., "name": ..., "specialization": ..., "schedule": ..., "contact": ... } }
    - Update: { "operation": "update", "table": "doctor", "data": {"doctor_id": ..., {"field"}: {"value"}... } }
    - View:   { "operation": "view", "table": "doctor", "data": {"id": ... }}

    For table: appointment
    - Insert: { "operation": "insert", "table": "appointment", "data": { "appointment_id": ..., "appointment_date": ..., "appointment_time": ..., "patient_id": ..., "doctor_id": ... } }
    - Update: { "operation": "update", "table": "appointment",  "data": { {"field"}: {"appointment_id": ...,"value"}... } }
    - View:   { "operation": "view", "table": "appointment", "data": {"id": ... }}

    For table: bill
    - Insert: { "operation": "insert", "table": "bill", "data": { "bill_id": ..., "amount": ..., "payment_method": ..., "payment_status": ..., "billing_date": ..., "patient_id": ..., "appointment_id": ... } }
    - Update: { "operation": "update", "table": "bill", "data": { "bill_id": ..., {"field"}: {"value"}... } }
    - View:   { "operation": "view", "table": "bill","data": {"id": ... }}

    Return the output strictly in the above JSON format.

    User input: {user_text}
    """
    return f"""
First identify the SQL table from the text: patient, doctor, appointment, or bill.
Then identify the operation: insert (also appears as add), update (also appears as change), view (also appears as show, extract, info about).

Only one operation should be extracted per request.

Extract the relevant information and return it as JSON based on the table and operation:

For table: patient
- Insert: {{ "operation": "insert", "table": "patient", "data": {{ "id": ..., "name": ..., "age": ..., "gender": ..., "address": ..., "contact": ... }} }}
- Update: {{ "operation": "update", "table": "patient", "data": {{"id": ..., {"field"}: {"value"}... }} }}
- View:   {{ "operation": "view", "table": "patient","data": {{ "id": ... }} }}

For table: doctor
- Insert: {{ "operation": "insert", "table": "doctor", "data": {{ "doctor_id": ..., "name": ..., "specialization": ..., "schedule": ..., "contact": ... }} }}
- Update: {{ "operation": "update", "table": "doctor",  "data": {{ "doctor_id": ..., {"field"}: {"value"}... }} }}
- View:   {{ "operation": "view", "table": "doctor","data": {{"id": ... }} }}

For table: appointment
- Insert: {{ "operation": "insert", "table": "appointment", "data": {{ "appointment_id": ..., "appointment_date": ..., "appointment_time": ..., "patient_id": ..., "doctor_id": ... }} }}
- Update: {{ "operation": "update", "table": "appointment", "data": {{ "appointment_id": ..., {"field"}: {"value"}... }} }}
- View:   {{ "operation": "view", "table": "appointment","data": {{"id": ... }} }}

For table: bill
- Insert: {{ "operation": "insert", "table": "bill", "data": {{ "bill_id": ..., "amount": ..., "payment_method": ..., "payment_status": ..., "billing_date": ..., "patient_id": ..., "appointment_id": ... }} }}
- Update: {{ "operation": "update", "table": "bill", "data": {{ "bill_id": ..., {"field"}: {"value"}... }} }}
- View:   {{ "operation": "view", "table": "bill","data":{{"id": ... }} }}

Return the output strictly in the above JSON format.

User input: {user_text}
"""


def save_response_json(response_text):
    match = re.search(r"\{[\s\S]*\}", response_text)
    if match:
        try:
            data = json.loads(match.group())
            with open("output.json", "w") as file:
                json.dump(data, file, indent=4)
            print("\nParsed and saved JSON to 'output.json'")
            print(data)
            
        except json.JSONDecodeError as e:
            print("JSON parsing error:", e)
    else:
        print("No valid JSON found in response.")


if __name__ == "__main__":
    response = configure_and_generate("Add a doctor with ID D201, name Dr. Smith, specialization is Cardiology, works on weekdays from 10 AM to 5 PM, and contact number is 9123456789.")
    print(response.text)
    table, operation1, datas = dict.sql_values()
    dict.operations(operation1, datas)


