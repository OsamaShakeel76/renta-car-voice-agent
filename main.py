import random
import string
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

import database
from database import Car, Booking, get_db, init_db

app = FastAPI(title="Renta Car Backend")

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# --- Pydantic Models ---
from pydantic import BaseModel, Field

class CarInfo(BaseModel):
    id: int
    plateNumber: Optional[str] = None
    name: str
    category: str

    class Config:
        from_attributes = True
        rename_fields = {
            "plate_number": "plateNumber"
        }

class CreateBookingRequest(BaseModel):
    fullName: str
    phoneNumber: str
    pickupDateTime: str  # YYYY-MM-DD HH:MM
    returnDateTime: str  # YYYY-MM-DD HH:MM
    pickupLocation: str
    dropoffLocation: str
    carCategory: str
    notes: Optional[str] = None

class BookingResponse(BaseModel):
    success: bool
    bookingReference: Optional[str] = None
    status: Optional[str] = None
    assignedCar: Optional[CarInfo] = None
    message: str
    error: Optional[str] = None

class CheckAvailabilityRequest(BaseModel):
    pickupDateTime: str  # YYYY-MM-DD HH:MM
    returnDateTime: str  # YYYY-MM-DD HH:MM
    carCategory: str

class AvailabilityResponse(BaseModel):
    success: bool
    available: bool
    availableCount: int
    cars: List[CarInfo]
    message: str

class GetBookingRequest(BaseModel):
    bookingReference: Optional[str] = None
    phoneNumber: Optional[str] = None
    fullName: Optional[str] = None

class SingleBookingInfo(BaseModel):
    bookingReference: str
    fullName: str
    phoneNumber: str
    pickupDateTime: str
    returnDateTime: str
    pickupLocation: str
    dropoffLocation: str
    carCategory: str
    status: str

class GetBookingResponse(BaseModel):
    success: bool
    booking: Optional[SingleBookingInfo] = None
    error: Optional[str] = None
    message: Optional[str] = None

class CancelBookingRequest(BaseModel):
    bookingReference: Optional[str] = None
    phoneNumber: Optional[str] = None

class CancelBookingResponse(BaseModel):
    success: bool
    message: str
    bookingReference: Optional[str] = None
    error: Optional[str] = None

# --- Helpers ---

def generate_reference():
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"RB-{date_str}-{random_str}"

def is_car_available(db: Session, car_id: int, pickup_dt_str: str, return_dt_str: str):
    # Overlap Rule: new_start < existing_end AND new_end > existing_start
    # date_time format: YYYY-MM-DD HH:MM
    
    # Check for overlapping confirmed bookings
    overlapping_booking = db.query(Booking).filter(
        Booking.assigned_car_id == car_id,
        Booking.status == "confirmed",
        and_(
            Booking.pickup_date_time < return_dt_str,
            Booking.return_date_time > pickup_dt_str
        )
    ).first()
    
    return overlapping_booking is None

# --- Endpoints ---

@app.post("/api/create-booking", response_model=BookingResponse)
def create_booking(req: CreateBookingRequest, db: Session = Depends(get_db)):
    pickup_dt_str = req.pickupDateTime
    return_dt_str = req.returnDateTime
    
    try:
        pickup_dt = datetime.strptime(pickup_dt_str, "%Y-%m-%d %H:%M")
        return_dt = datetime.strptime(return_dt_str, "%Y-%m-%d %H:%M")
        if return_dt <= pickup_dt:
            return {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Return date/time must be after pickup date/time."
            }
    except ValueError:
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Invalid date or time format. Expected YYYY-MM-DD HH:MM."
        }

    # 1. Find available cars in category
    available_car = db.query(Car).filter(
        Car.category == req.carCategory,
        or_(Car.status == "active", Car.status == "available")
    ).all()
    
    assigned_car = None
    for car in available_car:
        if is_car_available(db, car.id, pickup_dt_str, return_dt_str):
            assigned_car = car
            break
            
    if not assigned_car:
        return {
            "success": False,
            "error": "NO_AVAILABILITY",
            "message": "No cars available for selected dates."
        }
    
    # 2. Create booking
    ref = generate_reference()
    new_booking = Booking(
        booking_reference=ref,
        full_name=req.fullName,
        phone_number=req.phoneNumber,
        pickup_date_time=req.pickupDateTime,
        return_date_time=req.returnDateTime,
        pickup_location=req.pickupLocation,
        dropoff_location=req.dropoffLocation,
        car_category=req.carCategory,
        assigned_car_id=assigned_car.id,
        status="confirmed",
        notes=req.notes
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return {
        "success": True,
        "bookingReference": ref,
        "status": "confirmed",
        "assignedCar": {
            "id": assigned_car.id,
            "plateNumber": assigned_car.plate_number,
            "name": assigned_car.name,
            "category": assigned_car.category
        },
        "message": "Booking created successfully."
    }

@app.post("/api/check-availability", response_model=AvailabilityResponse)
def check_availability(req: CheckAvailabilityRequest, db: Session = Depends(get_db)):
    pickup_dt_str = req.pickupDateTime
    return_dt_str = req.returnDateTime
    
    all_cars_in_cat = db.query(Car).filter(
        Car.category == req.carCategory,
        or_(Car.status == "active", Car.status == "available")
    ).all()
    
    available_cars = []
    for car in all_cars_in_cat:
        if is_car_available(db, car.id, pickup_dt_str, return_dt_str):
            available_cars.append({
                "id": car.id,
                "plateNumber": car.plate_number,
                "name": car.name,
                "category": car.category
            })
            
    return {
        "success": True,
        "available": len(available_cars) > 0,
        "availableCount": len(available_cars),
        "cars": available_cars,
        "message": "Cars available." if available_cars else "No cars available."
    }

@app.post("/api/get-booking", response_model=GetBookingResponse)
def get_booking(req: GetBookingRequest, db: Session = Depends(get_db)):
    query = db.query(Booking)
    
    if req.bookingReference:
        query = query.filter(Booking.booking_reference == req.bookingReference)
    elif req.phoneNumber:
        query = query.filter(Booking.phone_number == req.phoneNumber)
        if req.fullName:
            query = query.filter(Booking.full_name == req.fullName)
    else:
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Booking reference or phone number is required."
        }
        
    booking = query.order_by(Booking.created_at.desc()).first()
    
    if not booking:
        return {
            "success": False,
            "error": "NOT_FOUND",
            "message": "Booking not found."
        }
        
    return {
        "success": True,
        "booking": {
            "bookingReference": booking.booking_reference,
            "fullName": booking.full_name,
            "phoneNumber": booking.phone_number,
            "pickupDateTime": booking.pickup_date_time,
            "returnDateTime": booking.return_date_time,
            "pickupLocation": booking.pickup_location,
            "dropoffLocation": booking.dropoff_location,
            "carCategory": booking.car_category,
            "status": booking.status
        }
    }

@app.post("/api/cancel-booking", response_model=CancelBookingResponse)
def cancel_booking(req: CancelBookingRequest, db: Session = Depends(get_db)):
    query = db.query(Booking)
    
    if req.bookingReference:
        query = query.filter(Booking.booking_reference == req.bookingReference)
    elif req.phoneNumber:
        query = query.filter(Booking.phone_number == req.phoneNumber)
    else:
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Booking reference or phone number is required."
        }
    
    booking = query.order_by(Booking.created_at.desc()).first()
    
    if not booking:
        return {
            "success": False,
            "error": "NOT_FOUND",
            "message": "Booking not found."
        }
    
    if booking.status == "cancelled":
         return {
            "success": True,
            "message": "Booking already cancelled.",
            "bookingReference": booking.booking_reference
        }
         
    booking.status = "cancelled"
    booking.cancelled_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Booking cancelled successfully.",
        "bookingReference": booking.booking_reference
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
