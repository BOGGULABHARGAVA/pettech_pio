import psycopg2
import json
import psycopg2.extras
from datetime import datetime
from psycopg2.extras import RealDictCursor
from schemas import UserRegistration,LoginRequest,AppointmentRequest  # Import the UserRegistration model
from fastapi import HTTPException

# Database connection settings
DB_NAME = "petTech"
DB_USER = "pet"
DB_PASSWORD = "pet123"
DB_HOST = "localhost"
DB_PORT = "5432"

def connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            cursor_factory=RealDictCursor
        )
        print("Database connection successful!")
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

def save_user_registration_details(request: UserRegistration):
    request_data = request.dict()
    conn = connection()
    cursor = conn.cursor()

    try:
        # Insert Patient Details and retrieve auto-generated ID
        INSERT_QUERY = '''
            INSERT INTO "petTech_schema".patient_data (
                owner_name,
                owner_mobile,
                animal_type,
                animal_age,
                owner_email,
                password
            ) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        '''
        cursor.execute(
            INSERT_QUERY,
            (
                request_data['owner_name'],
                request_data['owner_mobile'],
                request_data['animal_type'],
                request_data['animal_age'],
                request_data['owner_email'],
                request_data['password']
            )
        )
        registration_number = cursor.fetchone()["id"]  # Fetch the generated ID
        conn.commit()

        return {"message": "Registration successful", "registration_number": registration_number}

    except Exception as e:
        conn.rollback()
        print(f"Error: {str(e)} occurred")
        raise HTTPException(status_code=400, detail=f"Error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def verify_user_login_details(request:LoginRequest):
    request_data = request.dict()
    conn = connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Query to check if the user exists with the given email and password
        SELECT_QUERY = '''
            SELECT id, owner_name, owner_email 
            FROM "petTech_schema".patient_data 
            WHERE owner_email = %s AND password = %s;
        '''
        cursor.execute(
            SELECT_QUERY,
            (
                request_data['owner_email'],
                request_data['password']
            )
        )
        user_record = cursor.fetchone()

        # If no record is found, return an error
        if not user_record:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # If the record exists, return a success message and user details
        return {
            "message": "Login successful",
            "details": {
                "id": user_record["id"],
                "owner_name": user_record["owner_name"],
            }
        }

    except Exception as e:
        conn.rollback()
        print(f"Error: {str(e)} occurred")
        raise HTTPException(status_code=400, detail=f"Error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
def save_appointment(request: AppointmentRequest):
    request_data = request.dict()
    conn = connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        INSERT_QUERY = """
            INSERT INTO appointments (appointment_id, name, email, mobile, date, time, message) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(
            INSERT_QUERY,
            (
                request_data['appointment_id'],
                request_data['name'],
                request_data['email'],
                request_data['mobile'],
                request_data['date'],
                request_data['time'],
                request_data['message']
            )
        )
        
        conn.commit()
        appointment_id = cursor.fetchone()["appointment_id"]

        return {
            "message": "Appointment saved successfully",
            "appointment_id": appointment_id
        }

    except Exception as e:
        conn.rollback()
        print(f"Error: {str(e)} occurred")
        raise HTTPException(status_code=400, detail=f"Error occurred: {e}")

    finally:
        cursor.close()
        conn.close()

        
    