# app.py - Backend with Registration and Password Reset

import os
import json
import logging
import secrets # For generating secure tokens
from datetime import datetime, timedelta # For token expiration
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing

# --- Import your custom modules ---
try:
    import llm1
    import dict as dict_logic
    # from old_mysql import Hospital # Assuming this might be used elsewhere or by dict_logic
    # import mysql_helpers         # Assuming this might be used elsewhere or by dict_logic
except ImportError as e:
    print(f"FATAL ERROR: Could not import required modules: {e}")
    # print("Please ensure llm1.py, dict.py, old_mysql.py, and mysql_helpers.py are present.") # Keep if these are critical
    exit(1)

# --- Flask App Configuration ---
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key_replace_me_123!')
if app.secret_key == 'dev_secret_key_replace_me_123!':
    print("WARNING: Using default development secret key. Set FLASK_SECRET_KEY environment variable for production.")

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)

# --- Global Variables / Constants ---
OUTPUT_JSON_PATH = 'output.json'
# Token validity duration (e.g., 1 hour)
PASSWORD_RESET_TIMEOUT = timedelta(hours=1)

# --- Placeholder User Data Store ---
# !!! WARNING: Storing data like this is INSECURE and NOT for production !!!
# Use a proper database (SQLAlchemy, etc.) in a real application.
# Structure: { 'username': {'password_hash': '...', 'role': '...', 'email': '...',
#                           'reset_token': '...', 'reset_token_expiry': datetime_object } }
users_db = {
    # Add initial admin/user with hashed passwords
    "admin": {
        "password_hash": generate_password_hash("adminpass"), # Hash the password
        "role": "admin",
        "email": "admin@example.com", # Add email
        "reset_token": None,
        "reset_token_expiry": None
    },
    "doctor": {
        "password_hash": generate_password_hash("doctor"), # Hash the password
        "role": "doctor",
        "email": "doctor@example.com", # Add email
        "reset_token": None,
        "reset_token_expiry": None
    },
    "user": {
        "password_hash": generate_password_hash("password"), # Hash the password
        "role": "non-admin", # Changed from 'standard_user' to 'non-admin' to match your register route default
        "email": "user@example.com", # Add email
        "reset_token": None,
        "reset_token_expiry": None
    }
}

# --- Authentication Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login, checking hashed passwords."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # role_selected variable is removed as it's not submitted from login form

        app.logger.info(f"Login attempt: username='{username}'") # Updated log

        user_data = users_db.get(username)

        # 1. Check user exists and password hash matches
        if user_data and check_password_hash(user_data.get('password_hash', ''), password):
            # Password matches
            user_actual_role = user_data.get('role') # Get the user's role from the database

            # Role validation based on form selection is removed here

            # --- Login Successful ---
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user_actual_role  # Store the role retrieved from the database
            app.logger.info(f"User '{username}' logged in successfully with role '{user_actual_role}'.")
            return redirect(url_for('index'))
        else:
            # User not found or password incorrect
            app.logger.warning(f"Failed login attempt for username '{username}': Invalid credentials")
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

    # --- Handle GET Request ---
    if session.get('logged_in'): # If already logged in, redirect to index
         return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'non-admin') # Default to non-admin if not provided

        # --- Basic Validation ---
        if not all([username, email, password, confirm_password]):
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('register'))

        if username in users_db:
            flash("Username already exists. Please choose another.", "error")
            return redirect(url_for('register'))

        if any(user['email'] == email for user in users_db.values()):
             flash("Email address already registered.", "error")
             return redirect(url_for('register'))

        # --- Create User (in placeholder DB) ---
        users_db[username] = {
            "password_hash": generate_password_hash(password),
            "role": role,
            "email": email,
            "reset_token": None,
            "reset_token_expiry": None
        }
        app.logger.info(f"New user registered: username='{username}', email='{email}', role='{role}'")
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    # --- Handle GET Request ---
    return render_template('register.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handles request to reset password."""
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash("Email address is required.", "error")
            return redirect(url_for('forgot_password'))

        user_to_reset = None
        username_to_reset = None
        for uname, udata in users_db.items():
            if udata.get('email') == email:
                user_to_reset = udata
                username_to_reset = uname
                break

        if user_to_reset:
            token = secrets.token_urlsafe(32)
            expiry_time = datetime.utcnow() + PASSWORD_RESET_TIMEOUT
            user_to_reset['reset_token'] = token
            user_to_reset['reset_token_expiry'] = expiry_time
            app.logger.info(f"Password reset token generated for user '{username_to_reset}' (email: {email})")
            reset_url = url_for('reset_password', token=token, _external=True)
            print("------------------------------------------------------")
            print(f"SIMULATED EMAIL for {email}:")
            print(f"Click here to reset your password: {reset_url}")
            print(f"(Token: {token} - Expires at: {expiry_time.isoformat()} UTC)")
            print("------------------------------------------------------")
            flash("If an account exists for that email, password reset instructions have been sent (check console).", "info")
        else:
            app.logger.warning(f"Password reset attempt for non-existent email: {email}")
            flash("If an account exists for that email, password reset instructions have been sent (check console).", "info")
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handles the actual password reset using a token."""
    user_to_update = None
    username_to_update = None
    is_token_valid = False

    for uname, udata in users_db.items():
        if udata.get('reset_token') == token:
            expiry = udata.get('reset_token_expiry')
            if expiry and expiry > datetime.utcnow():
                user_to_update = udata
                username_to_update = uname
                is_token_valid = True
                break
            else:
                app.logger.warning(f"Expired password reset token used: {token}")
                flash("Password reset link has expired. Please request a new one.", "error")
                return redirect(url_for('forgot_password'))

    if not is_token_valid:
        app.logger.warning(f"Invalid or unknown password reset token used: {token}")
        flash("Invalid or expired password reset link.", "error")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash("Both password fields are required.", "error")
            return render_template('reset_password.html', token=token)
        if password != confirm_password:
            flash("New passwords do not match.", "error")
            return render_template('reset_password.html', token=token)

        user_to_update['password_hash'] = generate_password_hash(password)
        user_to_update['reset_token'] = None
        user_to_update['reset_token_expiry'] = None
        app.logger.info(f"Password successfully reset for user '{username_to_update}'.")
        flash("Your password has been reset successfully! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)


@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    username = session.get('username', 'Unknown User')
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    app.logger.info(f"User '{username}' logged out.")
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# --- Main Application Routes (Index, Chat) ---
@app.route('/')
def index():
    if not session.get('logged_in'):
        flash("Please log in to access the chat.", "info")
        return redirect(url_for('login'))
    username = session.get('username', 'Guest')
    user_role = session.get('role', 'Unknown')
    # Make sure your index.html can use username and user_role
    return render_template('index.html', username=username, user_role=user_role)


@app.route('/chat', methods=['POST'])
def chat():
    """Handles incoming chat messages, processes them, and returns the chatbot response."""
    if not session.get('logged_in'):
        app.logger.warning("Unauthorized chat attempt.")
        return jsonify({"error": "Not authenticated. Please log in again."}), 401

    user_role = session.get('role', 'non-admin')
    username = session.get('username', 'Unknown')
    app.logger.info(f"Chat request received from user: '{username}', role: '{user_role}'")

    try:
        data = request.get_json()
        if not data or 'message' not in data:
             app.logger.warning(f"Chat request from '{username}' missing JSON data or 'message' key.")
             return jsonify({"error": "Invalid request format. 'message' key missing."}), 400
        user_message = data['message'].strip()
        if not user_message:
            app.logger.warning(f"Chat request from '{username}' has empty message.")
            return jsonify({"error": "Message cannot be empty."}), 400
        app.logger.info(f"User '{username}' ({user_role}) message: '{user_message}'")
    except Exception as e:
        app.logger.error(f"Error parsing request JSON from '{username}': {e}", exc_info=True)
        return jsonify({"error": "Invalid request format."}), 400

    try:
        llm_success = llm1.configure_and_generate(user_message) # Assuming llm1.py exists and is setup
        if not llm_success:
             app.logger.error(f"LLM processing failed for message from '{username}'. Check {OUTPUT_JSON_PATH} for details.")
             error_msg = "Sorry, I had trouble understanding the structure of your request."
             return jsonify({"response": error_msg}), 500
        app.logger.info(f"LLM successfully processed input from '{username}'.")
    except Exception as e:
        app.logger.error(f"Unexpected error during LLM processing for '{username}': {e}", exc_info=True)
        return jsonify({"response": "Sorry, an unexpected error occurred while analyzing your request."}), 500

    try:
        table, operation, datas = dict_logic.sql_values() # Assuming dict.py exists and is setup
        if operation is None or datas is None:
             app.logger.error(f"Failed to read valid operation/data from {OUTPUT_JSON_PATH} for request from '{username}'.")
             error_msg = "Sorry, I couldn't determine the specific action or data needed from your request."
             return jsonify({"response": error_msg}), 500
        app.logger.info(f"Identified Operation: '{operation}' with Data: {datas} for user '{username}'")
    except Exception as e:
        app.logger.error(f"Error reading/parsing {OUTPUT_JSON_PATH} in /chat for '{username}': {e}", exc_info=True)
        return jsonify({"response": "Sorry, an internal error occurred while retrieving request details."}), 500

    permission_granted = False
    if user_role == 'admin':
        permission_granted = True
    elif user_role == 'doctor':
        if table == 'doctor':
            permission_granted = True
        elif table == 'appoiment':
            permission_granted = True
        else:
            permission_granted = False
    elif user_role == 'non-admin':
        if operation == 'view': # Example: non-admin can only view
            permission_granted = True
        else:
            permission_granted = False
            app.logger.warning(f"ACCESS DENIED: User '{username}' (role: {user_role}) attempted restricted operation '{operation}'.")
            return jsonify({"response": f"Access Denied: Your role ('{user_role}') does not permit the '{operation}' operation. You can only view records."}), 403 # 403 Forbidden
    else:
        app.logger.warning(f"ACCESS DENIED: User '{username}' has unrecognized role '{user_role}'. Denying operation '{operation}'.")
        return jsonify({"response": "Access Denied: Your user role is unrecognized."}), 403 # 403 Forbidden

    if not permission_granted: # Should be caught above, but as a safeguard
        return jsonify({"response": "Access Denied."}), 403

    try:
        app.logger.info(f"Permission granted for user '{username}' to perform '{operation}'. Proceeding with database action.")
        db_result_string = dict_logic.operations(table, operation, datas)
        if db_result_string is None:
             app.logger.error(f"Database table '{table}' for operation '{operation}' for user '{username}' returned None.")
             db_result_string = "The requested operation could not be completed due to an internal issue."
        else:
             app.logger.info(f"Database table '{table}' for operation '{operation}' for user '{username}' completed. Result: {db_result_string}")
    except Exception as e:
        app.logger.error(f"Error during database table '{table}' for operation operation '{operation}' for user '{username}': {e}", exc_info=True)
        return jsonify({"response": f"Sorry, an error occurred while trying to perform the '{operation}' operation on the database."}), 500

    try:
        final_response_text = llm1.generate_output_text(str(db_result_string))
        app.logger.info(f"Final response generated for user '{username}': '{final_response_text}'")
        return jsonify({"response": final_response_text})
    except Exception as e:
        app.logger.error(f"Error generating final response text for user '{username}': {e}", exc_info=True)
        return jsonify({"response": "Sorry, I encountered an issue while formatting the final response."}), 500


# --- Main Execution Guard ---
if __name__ == '__main__':
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
    app.logger.info(f"Starting Flask server on {host}:{port} (Debug Mode: {debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)