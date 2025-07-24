
import llm1
import input as cli_input # Renamed to avoid conflict with built-in input
import dict as dict_logic # Renamed to avoid conflict

# This main.py is a Command Line Interface (CLI) test script.
# It does not run the Flask web application.

# Define a function to identify user roles for CLI
def identify_user_role_cli():
    print("Please identify yourself for this CLI test:")
    print("1. Admin")
    print("2. Non-admin")
    while True:
        role_choice = input("Enter 1 for Admin or 2 for Non-admin: ").strip()
        if role_choice == "1":
            return "admin"
        elif role_choice == "2":
            return "non-admin"
        else:
            print("Invalid input. Please enter 1 or 2.")

def run_cli_test():
    print("--- CLI Hospital Bot Test ---")
    user_role = identify_user_role_cli()
    print(f"CLI Test Role: {user_role}")

    # Get user input (can be speech if configured in cli_input.py and mic is available)
    # Forcing text input for simpler CLI test by default:
    user_text_query = cli_input.user_input(use_speech=False) # Set use_speech=True to test mic
    if not user_text_query:
        print("No input received. Exiting.")
        return

    print(f"\nUser query: '{user_text_query}'")

    # 1. LLM processes query to extract operation and data
    if not llm1.MODEL:
        print("LLM Model not initialized. Cannot proceed. Check API Key and llm1.py setup.")
        return

    print("\nStep 1: LLM extracting operation/data...")
    llm_extraction_success = llm1.configure_and_generate(user_text_query)

    if not llm_extraction_success:
        print(f"LLM data extraction failed. Check '{llm1.OUTPUT_JSON_PATH}' for error details from LLM.")
        # Try to get a user-friendly message from the LLM if possible for this failure
        error_explanation = llm1.generate_output_text(f"LLM failed to understand the query structure. Raw query: {user_text_query}")
        print(f"Bot says: {error_explanation}")
        return
    print("LLM extraction seems successful.")

    # 2. Read extracted operation and data
    print("\nStep 2: Reading extracted data...")
    table, operation, datas = dict_logic.sql_values()

    if operation is None or datas is None:
        print(f"Failed to read valid operation/data from '{llm1.OUTPUT_JSON_PATH}'.")
        error_content = "Could not determine the action or data from the LLM's output."
        if llm1.OUTPUT_JSON_PATH:
            try:
                with open(llm1.OUTPUT_JSON_PATH, 'r') as f_err:
                    error_content += f" Contents of {llm1.OUTPUT_JSON_PATH}: {f_err.read()}"
            except Exception:
                pass # Ignore if reading error file also fails
        print(f"Bot says: {llm1.generate_output_text(error_content)}")
        return
    print(f"Operation: '{operation}', Data: {datas}")

    # 3. CLI Role-Based Access Control (simplified for CLI)
    print("\nStep 3: Checking permissions (CLI context)...")
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
            print(f"Access Denied (CLI): Role '{user_role}' cannot perform '{operation}'.")
            print(f"Bot says: {llm1.generate_output_text(f'Access Denied: Your role does not permit the {operation} operation for CLI testing.')}")
            return
    elif user_role == 'non-admin':
        if operation == 'view': # Example: non-admin can only view
            permission_granted = True
        else:
            permission_granted = False
            print(f"Access Denied (CLI): Role '{user_role}' cannot perform '{operation}'.")
            print(f"Bot says: {llm1.generate_output_text(f'Access Denied: Your role does not permit the {operation} operation for CLI testing.')}")
            return
    
    if not permission_granted: # Should not happen if logic above is correct
         print("Permission check failed unexpectedly.")
         return
    print("Permission granted.")

    # 4. Perform DB operation
    print(f"\nStep 4: Performing database operation '{operation}'...")
    db_result_string = dict_logic.operations(table,operation, datas)
    print(f"DB operation result: {db_result_string}")

    # 5. LLM generates final friendly response
    print("\nStep 5: LLM generating final response...")
    final_response = llm1.generate_output_text(db_result_string)
    print(f"\n---------------------------------")
    print(f"Bot's final response: {final_response}")
    print(f"---------------------------------")

if __name__ == "__main__":
    run_cli_test()
