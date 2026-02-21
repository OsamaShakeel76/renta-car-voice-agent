import random
import string
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dateutil import parser as dtparser
from typing import List, Optional, Tuple
from fastapi import FastAPI, Depends, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

import database
from database import Car, Booking, get_db, init_db, SessionLocal
import calendar_service

KHI_TZ = ZoneInfo("Asia/Karachi")

app = FastAPI(title="Renta Car Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# --- Pydantic Models ---
from pydantic import BaseModel, Field

class CarInfo(BaseModel):
    id: int
    plate_number: Optional[str] = Field(None, alias="plateNumber")
    name: str
    category: str

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class CreateBookingRequest(BaseModel):
    full_name: str = Field(..., alias="fullName")
    phone_number: str = Field(..., alias="phoneNumber")
    pickup_date_time: str = Field(..., alias="pickupDateTime")
    return_date_time: str = Field(..., alias="returnDateTime")
    pickup_location: str = Field(..., alias="pickupLocation")
    dropoff_location: str = Field(..., alias="dropoffLocation")
    car_category: str = Field(..., alias="carCategory")
    notes: Optional[str] = None

    model_config = {
        "populate_by_name": True
    }

class BookingResponse(BaseModel):
    success: bool
    booking_reference: Optional[str] = Field(None, alias="bookingReference")
    status: Optional[str] = None
    assigned_car: Optional[CarInfo] = Field(None, alias="assignedCar")
    message: str
    error: Optional[str] = None
    pickup_date_time: Optional[str] = Field(None, alias="pickupDateTime")
    return_date_time: Optional[str] = Field(None, alias="returnDateTime")
    pickup_location: Optional[str] = Field(None, alias="pickupLocation")
    dropoff_location: Optional[str] = Field(None, alias="dropoffLocation")
    car_category: Optional[str] = Field(None, alias="carCategory")
    full_name: Optional[str] = Field(None, alias="fullName")
    phone_number: Optional[str] = Field(None, alias="phoneNumber")
    calendar_status: Optional[str] = Field(None, alias="calendarStatus")

    model_config = {
        "populate_by_name": True
    }

class CheckAvailabilityRequest(BaseModel):
    pickup_date_time: str = Field(..., alias="pickupDateTime")
    return_date_time: str = Field(..., alias="returnDateTime")
    car_category: str = Field(..., alias="carCategory")

    model_config = {
        "populate_by_name": True
    }

class AvailabilityResponse(BaseModel):
    success: bool
    available: bool
    available_count: int = Field(..., alias="availableCount")
    cars: List[CarInfo]
    message: str

    model_config = {
        "populate_by_name": True
    }

class GetBookingRequest(BaseModel):
    booking_reference: Optional[str] = Field(None, alias="bookingReference")
    phone_number: Optional[str] = Field(None, alias="phoneNumber")
    full_name: Optional[str] = Field(None, alias="fullName")

    model_config = {
        "populate_by_name": True
    }

class SingleBookingInfo(BaseModel):
    id: Optional[int] = None
    customer_name: str = Field(..., alias="customerName")
    customer_phone: str = Field(..., alias="customerPhone")
    pickup_date_time: str = Field(..., alias="pickupDateTime")
    return_date_time: str = Field(..., alias="returnDateTime")
    pickup_location: str = Field(..., alias="pickupLocation")
    dropoff_location: str = Field(..., alias="dropoffLocation")
    car_category: str = Field(..., alias="carCategory")
    status: str
    duration: Optional[str] = None
    calendar_status: Optional[str] = Field(None, alias="calendarStatus")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class AllBookingsResponse(BaseModel):
    success: bool
    bookings: List[SingleBookingInfo]
    message: str
    total: int = 0

    model_config = {
        "populate_by_name": True
    }

def is_car_available(db: Session, car_id: int, pickup_dt_str: str, return_dt_str: str):
    # Overlap Rule: new_start < existing_end AND new_end > existing_start
    with open("debug_log.txt", "a") as f:
        f.write(f"DEBUG: Checking car_id={car_id}, req {pickup_dt_str} to {return_dt_str}\n")
        overlapping_booking = db.query(Booking).filter(
            Booking.assigned_car_id == car_id,
            Booking.status == "confirmed",
            and_(
                Booking.pickup_date_time < return_dt_str,
                Booking.return_date_time > pickup_dt_str
            )
        ).first()
        if overlapping_booking:
            f.write(f"DEBUG: Found overlap id={overlapping_booking.id}, {overlapping_booking.pickup_date_time} to {overlapping_booking.return_date_time}\n")
        else:
            f.write(f"DEBUG: No overlap found for car_id={car_id}\n")
    return overlapping_booking is None

def safe_calendar_sync(booking_id: int) -> None:
    """Background: sync booking to Google Calendar."""
    import logging
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return
        try:
            result = calendar_service.create_calendar_event(booking)
            booking.calendar_status = "synced" if result else "failed"
        except Exception as e:
            logging.getLogger(__name__).exception("Calendar sync failed for booking_id=%s: %s", booking_id, e)
            booking.calendar_status = "failed"
        db.commit()
    except Exception:
        logging.getLogger(__name__).exception("Calendar sync error for booking_id=%s", booking_id)
    finally:
        db.close()

# --- Helpers ---

def mask_name(full_name: str) -> str:
    parts = full_name.strip().split()
    if not parts:
        return ""
    first = parts[0]
    last_initial = f" {parts[-1][0].upper()}." if len(parts) > 1 else ""
    return f"{first}{last_initial}"

def mask_phone(phone: str) -> str:
    p = phone.strip()
    if len(p) <= 7:
        return p
    return f"{p[:4]}****{p[-3:]}"

def normalize_datetime_to_iso_with_tz(dt_str: str):
    dt = dtparser.parse(dt_str.strip())
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KHI_TZ)
    return dt.isoformat(timespec="seconds"), dt

def calculate_duration_str(start_str: str, end_str: str) -> str:
    try:
        start = dtparser.parse(start_str)
        end = dtparser.parse(end_str)
        diff = end - start
        days = diff.days
        hours = diff.seconds // 3600
        parts = []
        if days > 0: parts.append(f"{days}d")
        if hours > 0: parts.append(f"{hours}h")
        return " ".join(parts) if parts else "< 1h"
    except:
        return "Unknown"

@app.post("/api/create-booking", response_model=BookingResponse)
def create_booking(payload: CreateBookingRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        pickup_iso, pickup_dt = normalize_datetime_to_iso_with_tz(payload.pickup_date_time)
        return_iso, return_dt = normalize_datetime_to_iso_with_tz(payload.return_date_time)
    except Exception as e:
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": f"Invalid date format: {str(e)}",
        }

    if return_dt <= pickup_dt:
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Return time must be after pickup.",
        }

    # Overlap check
    available_cars = db.query(Car).filter(
        Car.category == payload.car_category,
        or_(Car.status == "active", Car.status == "available"),
    ).all()

    assigned_car = None
    for car in available_cars:
        if is_car_available(db, car.id, pickup_iso, return_iso):
            assigned_car = car
            break

    if not assigned_car:
        return {
            "success": False,
            "error": "NO_AVAILABILITY",
            "message": "No cars available for selected dates.",
        }

    booking = Booking(
        full_name=payload.full_name.strip(),
        phone_number=payload.phone_number.strip(),
        pickup_location=payload.pickup_location.strip(),
        dropoff_location=payload.dropoff_location.strip(),
        car_category=payload.car_category.strip(),
        notes=payload.notes,
        pickup_date_time=pickup_iso,
        return_date_time=return_iso,
        assigned_car_id=assigned_car.id,
        status="confirmed",
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    background_tasks.add_task(safe_calendar_sync, booking.id)

    return {
        "success": True,
        "message": "Booking created successfully.",
        "status": "confirmed",
        "assignedCar": {
            "id": assigned_car.id,
            "plateNumber": assigned_car.plate_number,
            "name": assigned_car.name,
            "category": assigned_car.category,
        },
        "pickupDateTime": booking.pickup_date_time,
        "returnDateTime": booking.return_date_time,
        "carCategory": booking.car_category,
        "pickupLocation": booking.pickup_location,
        "dropoffLocation": booking.dropoff_location,
        "fullName": booking.full_name,
        "phoneNumber": booking.phone_number,
        "calendarStatus": booking.calendar_status or "pending",
    }

@app.post("/api/check-availability", response_model=AvailabilityResponse)
def check_availability(req: CheckAvailabilityRequest, db: Session = Depends(get_db)):
    try:
        pickup_iso, _ = normalize_datetime_to_iso_with_tz(req.pickup_date_time)
        return_iso, _ = normalize_datetime_to_iso_with_tz(req.return_date_time)
    except Exception as e:
        return {
            "success": False,
            "available": False,
            "availableCount": 0,
            "cars": [],
            "message": f"Invalid date format: {str(e)}"
        }
    
    all_cars_in_cat = db.query(Car).filter(
        Car.category == req.car_category,
        or_(Car.status == "active", Car.status == "available")
    ).all()
    
    available_cars = []
    for car in all_cars_in_cat:
        if is_car_available(db, car.id, pickup_iso, return_iso):
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

class GetBookingResponse(BaseModel):
    success: bool
    booking: Optional[SingleBookingInfo] = None
    error: Optional[str] = None
    message: Optional[str] = None

@app.post("/api/get-booking", response_model=GetBookingResponse)
def get_booking(req: GetBookingRequest, db: Session = Depends(get_db)):
    query = db.query(Booking)
    
    if req.phone_number:
        query = query.filter(Booking.phone_number == req.phone_number)
        if req.full_name:
            query = query.filter(Booking.full_name == req.full_name)
    else:
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Phone number is required."
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
            "id": booking.id,
            "customerName": booking.full_name,
            "customerPhone": booking.phone_number,
            "pickupDateTime": booking.pickup_date_time,
            "returnDateTime": booking.return_date_time,
            "pickupLocation": booking.pickup_location,
            "dropoffLocation": booking.dropoff_location,
            "carCategory": booking.car_category,
            "status": booking.status,
            "calendarStatus": booking.calendar_status or "pending",
        },
    }

class CancelBookingResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None

class CancelBookingRequest(BaseModel):
    phone_number: Optional[str] = Field(None, alias="phoneNumber")
    full_name: Optional[str] = Field(None, alias="fullName")

@app.post("/api/cancel-booking", response_model=CancelBookingResponse)
def cancel_booking(req: CancelBookingRequest, db: Session = Depends(get_db)):
    if not req.phone_number:
        return {"success": False, "error": "VALIDATION_ERROR", "message": "Phone number is required."}
    
    query = db.query(Booking).filter(Booking.phone_number == req.phone_number)
    if req.full_name:
        query = query.filter(Booking.full_name == req.full_name)
    
    booking = query.order_by(Booking.created_at.desc()).first()
    if not booking:
        return {"success": False, "error": "NOT_FOUND", "message": "Booking not found."}
    
    if booking.status == "cancelled":
         return {"success": True, "message": "Booking already cancelled."}
         
    booking.status = "cancelled"
    booking.cancelled_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Booking cancelled successfully."}

@app.get("/api/get-all-bookings", response_model=AllBookingsResponse)
def get_all_bookings(
    limit: int = 50, 
    offset: int = 0, 
    carCategory: Optional[str] = None, 
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"), 
    db: Session = Depends(get_db)
):
    # Security: Verify Admin Key
    env_admin_key = os.getenv("ADMIN_KEY", "RENTACAR_ELITE_2026")
    if x_admin_key != env_admin_key:
        raise HTTPException(status_code=403, detail="Forbidden: Valid Admin Key required.")

    query = db.query(Booking).filter(Booking.status == "confirmed")
    if carCategory:
        query = query.filter(Booking.car_category == carCategory)
    
    total_count = query.count()
    bookings = query.order_by(Booking.created_at.desc()).offset(offset).limit(limit).all()
    
    booking_list = []
    for b in bookings:
        booking_list.append({
            "id": b.id,
            "customerName": b.full_name,
            "customerPhone": b.phone_number,
            "pickupDateTime": b.pickup_date_time,
            "returnDateTime": b.return_date_time,
            "duration": calculate_duration_str(b.pickup_date_time, b.return_date_time),
            "pickupLocation": b.pickup_location,
            "dropoffLocation": b.dropoff_location,
            "carCategory": b.car_category,
            "status": b.status,
            "calendarStatus": b.calendar_status or "pending",
        })
        
    return {
        "success": True,
        "bookings": booking_list,
        "total": total_count,
        "message": f"Retrieved {len(booking_list)} bookings."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

