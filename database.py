import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rentacar.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, index=True, nullable=True)
    category = Column(String, index=True)  # Economy / Sedan / SUV / Luxury
    name = Column(String)
    status = Column(String, default="active", index=True)  # active / available / inactive
    daily_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="assigned_car")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(20), unique=True, index=True, nullable=True)

    full_name = Column(String(200), nullable=False)
    phone_number = Column(String(50), nullable=False)

    pickup_location = Column(String(250), nullable=False)
    dropoff_location = Column(String(250), nullable=False)

    car_category = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)

    pickup_date_time = Column(DateTime, nullable=False)
    return_date_time = Column(DateTime, nullable=True)

    assigned_car_id = Column(Integer, ForeignKey("cars.id"), nullable=True)
    status = Column(String(30), nullable=False, default="confirmed")
    
    calendar_status = Column(String(30), nullable=True)
    calendar_event_id = Column(String(120), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)

    assigned_car = relationship("Car", back_populates="bookings")

# Add Indexes
Index("idx_booking_category", Booking.car_category)
Index("idx_booking_status", Booking.status)
Index("idx_booking_phone", Booking.phone_number)
Index("idx_booking_pickup_dt", Booking.pickup_date_time)
Index("idx_booking_return_dt", Booking.return_date_time)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
