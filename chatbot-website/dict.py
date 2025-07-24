# dict.py (Modified operations function)
import json
from old_mysql import Hospital
import llm1 # Keep this if llm1 is still needed *within* dict.py, otherwise remove

hos = Hospital()
OUTPUT_JSON_PATH = 'output.json' # Define path consistently

def sql_values():
    # ... (keep existing code but ensure file path is correct) ...
    try:
        with open(OUTPUT_JSON_PATH, 'r') as file:
            data = json.load(file)
            print("Read from output.json:", data) # Debug print
            table = data.get("table")
            operation1 = data.get("operation")
            datas = data.get("data")
            print(f"Table: {table}, Operation: {operation1}, Data: {datas}") # Debug print
            if not table or not operation1 or datas is None: # Basic validation
                print("Warning: 'operation' or 'data' missing in output.json")
                return None, None, None
            return table, operation1, datas
    except FileNotFoundError:
        print(f"Error: {OUTPUT_JSON_PATH} not found in sql_values.")
        return None, None, None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {OUTPUT_JSON_PATH}: {e}")
        return None, None, None
    except Exception as e:
        print(f"Unexpected error in sql_values: {e}")
        return None, None, None

def operations(table, operation1, datas):
    result = None # Initialize result
    if not operation1 or datas is None:
         print("Invalid operation or data received in operations function.")
         return "Invalid operation or data provided." # Return error string

    try:
        if table == "patient":

            if operation1 == "insert":
                # Add checks for missing keys
                required_keys = [ "name", "age", "gender", "contact", "address"]
                if not all(key in datas for key in required_keys):
                    return f"Missing required fields for insert. Need: {required_keys}"
                
                if datas.get("gender") is None:
                    datas["gender"] = "Unknown"

                name = datas.get("name")
                age = datas.get("age")
                gender = datas.get("gender")
                contact = datas.get("contact")
                address = datas.get("address")
                result = hos.insert_patient( name, age, gender, contact, address)
                # llm1.generate_output_text(result) # Remove LLM call from here


            elif operation1 == "update":
                id = datas.get("id")
                if id is None:
                    return "Missing 'id' for update operation."
                # Get other fields safely
                name = datas.get("name")
                age = datas.get("age")
                address = datas.get("address")
                contact = datas.get("contact")
                # Pass only non-None values to update_patient
                result = hos.update_patient(id, name=name, age=age, address=address, contact=contact)
                # llm1.generate_output_text(result) # Remove

            elif operation1 == "view":
                id = datas.get("id")
                if id is None:
                    return "Missing 'id' for view operation."
                view_data = hos.view_patient(id)
                if isinstance(view_data, tuple):
                    result = f"Record found: ID={view_data[0]}, Name={view_data[1]}, Age={view_data[2]}, Contact={view_data[4]}, Address={view_data[5]}"
                elif view_data: 
                    result = str(view_data)
                else:
                    result = f"No record found with ID {id}."

            else:
                print(f"Invalid operation received: {operation1}")
                result = f"Invalid operation '{operation1}' requested."
           

        elif table == "doctor":

            if operation1 == "insert":
                required_keys = ["doctor_id", "name", "specialization", "contact", "schedule"]
                if not all(key in datas and datas[key] is not None for key in required_keys):
                    return f"Missing required fields for insert. Need: {required_keys}"
                doctor_id = datas.get("id")
                name = datas.get("name")
                specialization = datas.get("specialization")
                contact = datas.get("contact")
                schedule = datas.get("schedule")
                result = hos.add_doctor(doctor_id, name, specialization, contact, schedule)
                

            elif operation1 == "view":
                id = datas.get("id")
                if id is None:
                    return "Missing 'id' for view operation."
                # view_patient needs to return a user-friendly string or structured data
                view_data = hos.get_doctor(id)
                if isinstance(view_data, tuple): # Assuming it returns a tuple on success
                    # Format the tuple into a readable string
                    result = f"Record found: ID={view_data[0]}, Name={view_data[1]}, Specialization={view_data[2]}, Contact={view_data[4]}, Schedula={view_data[5]}"
                elif view_data: # Handle other non-None return values if necessary
                    result = str(view_data)
                else:
                    result = f"No record found with ID {id}."
                # llm1.generate_output_text(result) # Remove

            else:
                print(f"Invalid operation received: {operation1}")
                result = f"Invalid operation '{operation1}' requested."

        elif table == "bill":

            # Implement bill operations here
            if operation1 == "insert":
                # Add checks for missing keys
                required_keys = ["patient_id", "appointment_id", "amount", "payment_method", "payment_status"]
                if not all(key in datas and datas[key] is not None for key in required_keys):
                    return f"Missing required fields for insert. Need: {required_keys}"
                patient_id = datas.get("patient_id")
                appointment_id = datas.get("appointment_id")
                amount = datas.get("amount")
                payment_method = datas.get("payment_method")
                payment_status = datas.get("payment_status")
            
                result = hos.create_bill(patient_id, appointment_id, amount, payment_method, payment_status)
                # llm1.generate_output_text(result) # Remove LLM call from here


            elif operation1 == "update":
                bill_id = datas.get("bill_id")
                if id is None:
                    return "Missing 'id' for update operation."
                # Get other fields safely
                amount = datas.get("amount")
                payment_method = datas.get("payment_method")
                payment_status = datas.get("payment_status")
                billing_date = datas.get("billing_date")
                # Pass only non-None values to update_patient
                result = hos.update_patient(id,  amount=amount, payment_method = payment_method, payment_status= payment_status, billing_date= billing_date)
                # llm1.generate_output_text(result) # Remove
            elif operation1 == "view":
                patient_id = datas.get("id")  # Better to rename for clarity
                if patient_id is None:
                    return "Missing 'id' for view operation."
    
                response = hos.get_patient_bills(patient_id)

                if response["status"] == "success":
                    bills = response["data"]
                    if bills:
                        result_lines = ["Billing Records:"]
                        for bill in bills:
                            result_lines.append(
                        f"BillingID: {bill['BillingID']}, Amount: {bill['Amount']}, "
                        f"PaymentMethod: {bill['PaymentMethod']}, PaymentStatus: {bill['PaymentStatus']}, "
                        f"BillingDate: {bill['BillingDate']}, AppointmentDate: {bill['AppointmentDate']}, "
                        f"Doctor: {bill['DoctorName']}"
                        )
                        result = "\n".join(result_lines)
                    else:
                        result = f"No billing records found for patient ID {patient_id}."
                else:
                    result = f"Error fetching bills: {response['message']}"

            else:
                print(f"Invalid operation received: {operation1}")
                result = f"Invalid operation '{operation1}' requested."
           
        elif table == "appointment":

            if operation1 == "insert":
                # Add checks for missing keys
                required_keys = [ "patient_id", "doctor_id", "appointment_date", "appointment_time"]

                if not all(key in datas and datas[key] is not None for key in required_keys):
                    return f"Missing required fields for insert. Need: {required_keys}"
                patient_id = datas.get("patient_id")
                doctor_id = datas.get("doctor_id")
                appointment_date = datas.get("appointment_date")
                appointment_time = datas.get("appointment_time")
                
                result = hos.create_appointment( patient_id, doctor_id, appointment_date, appointment_time)
                # llm1.generate_output_text(result) # Remove LLM call from here

            elif operation1 == "update":
                appointment_id = datas.get("appointment_id")
                if id is None:
                    return "Missing 'id' for update operation."
                # Get other fields safely
                appointment_date = datas.get("appointment_date")
                appointment_time = datas.get("appointment_time")
                appointment_status = datas.get("appointment_status")
                # Pass only non-None values to update_patient
                result = hos.update_appointment(appointment_id, appointment_date=appointment_date, appointment_time=appointment_time, appointment_status=appointment_status)
                # llm1.generate_output_text(result) # Remove

            elif operation1 == "view":
                id = datas.get("appointment_id")
                if id is None:
                    return "Missing 'id' for view operation."
                view_data = hos.get_appointments(id)
                if isinstance(view_data, tuple):
                    result = f"Record found: ID={view_data[0]}, Name={view_data[1]}, Age={view_data[2]}, Contact={view_data[4]}, Address={view_data[5]}"
                elif view_data: 
                    result = str(view_data)
                else:
                    result = f"No record found with ID {id}."

            else:
                print(f"Invalid operation received: {operation1}")
                result = f"Invalid operation '{operation1}' requested."

        else:

            print(f"Invalid operation received: {table}")
            result = f"Invalid operation '{table}' requested."

        return result # RETURN the result string

    except Exception as e:
        print(f"Error during database operation '{operation1}': {e}")
        import traceback
        traceback.print_exc()
        return f"An error occurred while performing the '{operation1}' operation."


# Remove the __main__ block if it calls functions directly,
# as app.py will now orchestrate the calls.
# if __name__ == "__main__":
#     operation1, datas = sql_values()
#     if operation1 and datas:
#        operations(operation1, datas)