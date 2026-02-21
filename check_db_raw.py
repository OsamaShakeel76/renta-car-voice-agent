from database import SessionLocal, Booking
import json

def check_db():
    db = SessionLocal()
    try:
        latest = db.query(Booking).order_by(Booking.id.desc()).first()
        if latest:
            print(f"Latest Booking ID: {latest.id}")
            print(f"Full Name (Raw): {latest.full_name}")
            print(f"Phone Number (Raw): {latest.phone_number}")
            print(f"Pickup: {latest.pickup_date_time}")
            print(f"Return: {latest.return_date_time}")
            print(f"Category: {latest.car_category}")
        else:
            print("No bookings found in DB.")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
