from pydantic import BaseModel
from datetime import date
from typing import Optional

# Pydantic model for data validation
class UserRegistration(BaseModel):
    owner_name: str
    owner_mobile: str
    animal_type: str
    animal_age: int
    owner_email: str
    password: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class LoginRequest(BaseModel):
    owner_email: str
    password: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# Appointment Data Model
class AppointmentRequest(BaseModel):
    name: str
    email: str
    mobile: str
    date: str
    time: str
    message: str
    appointment_id: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
    

