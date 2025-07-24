# mysql_helpers.py
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

def connect_db():
    try:
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD"), # Ensure this is set
            database=os.environ.get("DB_NAME")    # Ensure this is set
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        # Depending on your app's needs, you might want to raise the error
        # or handle it more gracefully (e.g., return None and check in caller)
        raise # Re-raise the error to be caught by the calling function

# Remove the connect_db() call from the global scope of this file
# connect_db()