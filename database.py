from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./rentacar.db"

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
    booking_reference = Column(String, unique=True, index=True)
    full_name = Column(String)
    phone_number = Column(String, index=True)
    pickup_date_time = Column(String)  # YYYY-MM-DD HH:MM
    return_date_time = Column(String)  # YYYY-MM-DD HH:MM
    pickup_location = Column(String)
    dropoff_location = Column(String)
    car_category = Column(String, index=True)
    assigned_car_id = Column(Integer, ForeignKey("cars.id"))
    status = Column(String, default="confirmed", index=True)  # confirmed / cancelled
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)

    assigned_car = relationship("Car", back_populates="bookings")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
