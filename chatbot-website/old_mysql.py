# old_mysql.py (Updated for HospitalDB schema)
import mysql_helpers as db_connect

class Hospital:
    def insert_patient(self,  name, age, gender=None, contact=None, address=None):
        """Insert a new patient record"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Patients 
                (PatientName, Age, Gender, Contact, Address) 
                VALUES ( %s, %s, %s, %s, %s)
            """
            cursor.execute(query, ( name, age, gender, contact, address))
            conn.commit()
            patient_id = cursor.lastrowid
            return {"status": "success", "patient_id": patient_id}
        except Exception as e:
            print(f"Database Error (insert_patient): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    def update_patient(self, PatientID, name=None, age=None, gender=None, 
                      contact=None, address=None, email=None):
        """Update patient information"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name is not None:
                updates.append("Name = %s")
                params.append(name)
            if age is not None:
                updates.append("Age = %s")
                params.append(age)
            if gender is not None:
                updates.append("Gender = %s")
                params.append(gender)
            if contact is not None:
                updates.append("Contact = %s")
                params.append(contact)
            if address is not None:
                updates.append("Address = %s")
                params.append(address)
            if email is not None:
                updates.append("Email = %s")
                params.append(email)
                
            if not updates:
                return {"status": "error", "message": "No fields to update"}
                
            params.append(PatientID)
            query = f"UPDATE Patients SET {', '.join(updates)} WHERE PatientID = %s"
            cursor.execute(query, tuple(params))
            conn.commit()
            
            if cursor.rowcount > 0:
                return {"status": "success", "message": f"Updated patient {PatientID}"}
            return {"status": "error", "message": "Patient not found"}
        except Exception as e:
            print(f"Database Error (update_patient): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def view_patient(self, patient_id):
        """Get patient details by ID"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT PatientID, PatientName, Age, Gender, Contact, Address
                FROM Patients WHERE PatientID = %s
            """
            cursor.execute(query, (patient_id,))
            patient = cursor.fetchone()
            
            if patient:
                return {"status": "success", "data": patient}
            return {"status": "error", "message": "Patient not found"}
        except Exception as e:
            print(f"Database Error (view_patient): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def create_appointment(self, patient_id, doctor_id, appointment_date, 
                         appointment_time, status="Scheduled"):
        """Create a new appointment"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Appointments 
                ( PatientID, DoctorID, AppointmentDate, AppointmentTime, AppointmentStatus) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_id, doctor_id, appointment_date, 
                                appointment_time, status))
            conn.commit()
            appointment_id = cursor.lastrowid
            return {"status": "success", "appointment_id": appointment_id}
        except Exception as e:
            print(f"Database Error (create_appointment): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def update_appointment(self, appointment_id, status=None, appointment_date=None,appointment_time=None):
        """Update appointment details"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if status is not None:
                updates.append("AppointmentStatus = %s")
                params.append(status)
            if appointment_date is not None:
                updates.append("AppointmentDate = %s")
                params.append(appointment_date)
            if appointment_time is not None:
                updates.append("AppointmentTime = %s")
                params.append(appointment_time)
                
            if not updates:
                return {"status": "error", "message": "No fields to update"}
                
            params.append(appointment_id)
            query = f"UPDATE Appointments SET {', '.join(updates)} WHERE AppointmentID = %s"
            cursor.execute(query, tuple(params))
            conn.commit()
            
            if cursor.rowcount > 0:
                return {"status": "success", "message": f"Updated appointment {appointment_id}"}
            return {"status": "error", "message": "Appointment not found"}
        except Exception as e:
            print(f"Database Error (update_appointment): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def get_appointments(self, patient_id=None, doctor_id=None, appointment_id=None):
        """Get appointments with optional filters"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT a.AppointmentID, a.AppointmentDate, a.AppointmentTime, a.AppointmentStatus,
                       p.PatientName, d.DoctorName, d.Specialization
                FROM Appointments a
                JOIN Patients p ON a.PatientID = p.PatientID
                JOIN Doctors d ON a.DoctorID = d.DoctorID
            """
            conditions = []
            params = []
            
            if patient_id:
                conditions.append("a.PatientID = %s")
                params.append(patient_id)
            if doctor_id:
                conditions.append("a.DoctorID = %s")
                params.append(doctor_id)
            if appointment_id:
                conditions.append("a.AppointmentID = %s")
                params.append(appointment_id)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            cursor.execute(query, tuple(params))
            appointments = cursor.fetchall()
            return {"status": "success", "data": appointments}
        except Exception as e:
            print(f"Database Error (get_appointments): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

      # DOCTOR OPERATIONS
    def add_doctor(self, doctor_id, name, specialization, contact, schedule=None):
        """Add a new doctor to the system"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Doctors 
                (DoctorID, DoctorName, Specialization, Contact, Scheduled) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (doctor_id, name, specialization, contact, schedule))
            conn.commit()
            doctor_id = cursor.lastrowid
            return {"status": "success", "doctor_id": doctor_id}
        except Exception as e:
            print(f"Database Error (add_doctor): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def get_doctor(self, doctor_id):
        """Get doctor details by ID"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT DoctorID, DoctorName, Specialization, Contact, Scheduled
                FROM Doctors WHERE DoctorID = %s
            """
            cursor.execute(query, (doctor_id,))
            doctor = cursor.fetchone()
            if doctor:
                return {"status": "success", "data": doctor}
            return {"status": "error", "message": "Doctor not found"}
        except Exception as e:
            print(f"Database Error (get_doctor): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    # BILLING OPERATIONS
    def create_bill(self, patient_id, appointment_id, amount, 
                   payment_method, payment_status="Pending"):
        """Create a new billing record"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Billing 
                (PatientID, AppointmentID, Amount, PaymentMethod, PaymentStatus) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_id, appointment_id, amount, 
                                payment_method, payment_status))
            conn.commit()
            bill_id = cursor.lastrowid
            return {"status": "success", "bill_id": bill_id}
        except Exception as e:
            print(f"Database Error (create_bill): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def get_patient_bills(self, patient_id):
        """Get all bills for a specific patient"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor(dictionary=True)
            query = """
    SELECT b.BillingID, b.Amount, b.PaymentMethod, b.PaymentStatus, b.BillingDate,
           a.AppointmentDate, d.DoctorName AS DoctorName
    FROM Billing b
    LEFT JOIN Appointments a ON b.AppointmentID = a.AppointmentID
    LEFT JOIN Doctors d ON a.DoctorID = d.DoctorID
    WHERE b.PatientID = %s
    ORDER BY b.BillingDate DESC
"""

            cursor.execute(query, (patient_id,))
            bills = cursor.fetchall()
            return {"status": "success", "data": bills}
        except Exception as e:
            print(f"Database Error (get_patient_bills): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def update_bill_status(self, bill_id, new_status,new_date):
        """Update payment status of a bill"""
        conn = None
        try:
            conn = db_connect.connect_db()
            cursor = conn.cursor()
            query = "UPDATE Billing SET PaymentStatus = %s , BillingDate = %s WHERE BillingID = %s"
            cursor.execute(query, (new_status, new_date, bill_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                return {"status": "success", "message": "Bill status updated"}
            return {"status": "error", "message": "Bill not found"}
        except Exception as e:
            print(f"Database Error (update_bill_status): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
