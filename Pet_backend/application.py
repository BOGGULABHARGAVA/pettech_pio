from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import schemas
import fsd_backend_db as fsd_db
from fastapi import  UploadFile, File, Depends
from fastapi.security import OAuth2PasswordBearer
import shutil
import os
import cv2
import numpy as np
import tensorflow as tf
from fastapi.staticfiles import StaticFiles
import tensorflow.lite as tflite



# Initialize FastAPI application
app = FastAPI()

# Define allowed origins (you can adjust these based on your frontend's URL)
origins = [
    "http://localhost",  # Localhost for development
    "http://localhost:5000",  # Frontend running on port 3000 (React, Vue, etc.)
    # Add any other domains or ports that need to access the backend
]

# Add CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all origins specified in the list
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.post("/save_user_registration_details")
async def save_user_registration_details(reg_details: schemas.UserRegistration):
    """
    Handles the user registration by validating input data 
    and saving the details into the database.

    Args:
        reg_details (schemas.UserRegistration): Validated registration details from the request.

    Returns:
        dict: A success message with registration details or error message.
    """
    try:
        # Print received registration details (for debugging purposes)
        print(f"Received registration details: {reg_details}")

        # Save registration details to the database
        result = fsd_db.save_user_registration_details(reg_details)

        # Check if result is successful (optional, depending on your db function)
        if result:
            return {"message": "Registration successful", "details": result}
        else:
            raise HTTPException(status_code=400, detail="Failed to save registration details")

    except Exception as e:
        # Handle exceptions and return HTTP error with detailed message
        print(f"Error: {str(e)}")  # Logging the error for debugging
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/verify_login")
async def verify_login(login_data: schemas.LoginRequest):
    try:
        # Print received registration details (for debugging purposes)
        print(f"Received login details: {login_data}")

        # Save registration details to the database
        result = fsd_db.verify_user_login_details(login_data)

        # Check if result is successful (optional, depending on your db function)
        if result:
            return {"message": "login successful", "details": result}
        else:
            raise HTTPException(status_code=400, detail="Failed to save registration details")

    except Exception as e:
        # Handle exceptions and return HTTP error with detailed message
        print(f"Error: {str(e)}")  # Logging the error for debugging
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/save_appointment/")
def save_appointment(appointment: schemas.AppointmentRequest):
    try:
    
        # Save registration details to the database
        result = fsd_db.save_appointment(appointment)

        # Check if result is successful (optional, depending on your db function)
        if result:
            return {"success": True, "details": result }
        else:
            raise HTTPException(status_code=400, detail="Failed Appointment saved in the database!")

    except Exception as e:
        # Handle exceptions and return HTTP error with detailed message
        print(f"Error: {str(e)}")  # Logging the error for debugging
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# Upload Directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount Static Files (so the uploaded images can be served)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Load TensorFlow Lite Model
MODEL_PATH = r"C:\Pet_Tech\Pet_backend\model\optimized_model.tflite"
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Disease Classes
CLASSES = ['Bacterial', 'Fungal', 'Healthy']

def preprocess_image(image_path):
    """Load and preprocess image for model inference."""
    img = cv2.imread(image_path)
    # Resize the image to 150x150 (instead of 224x224)
    img = cv2.resize(img, (150, 150))
    img = img.astype(np.float32) / 255.0
    return np.expand_dims(img, axis=0)  # Add batch dimension


@app.post("/upload")
async def upload_and_predict(file: UploadFile = File(...)):
    """
    Upload an image and immediately predict the disease.
    - Saves the uploaded image.
    - Preprocesses the image.
    - Performs inference using the TFLite model.
    - Returns the prediction result.
    """
    # Use the original filename; if it exists, add a suffix.
    filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        base, ext = os.path.splitext(filename)
        filename = f"{base}_old{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

    # Save the uploaded file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Preprocess the image for inference
    img_array = preprocess_image(file_path)

    # Perform inference using the TFLite model
    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    class_idx = int(np.argmax(output_data[0]))
    confidence = round(float(output_data[0][class_idx]) * 100, 2)

    return {
        "message": "Upload successful! Prediction complete.",
        "disease": CLASSES[class_idx],
        "confidence": confidence,
        "image_path": f"http://127.0.0.1:20000/uploads/{filename}",
        "explanation": f"The model detected '{CLASSES[class_idx]}' with {confidence}% confidence."
    }