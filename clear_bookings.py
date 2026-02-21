from database import SessionLocal, Booking
db = SessionLocal()
db.query(Booking).delete()
db.commit()
db.close()
print("Bookings cleared.")
