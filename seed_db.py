from database import SessionLocal, Car, init_db

# Ensure tables exist
init_db()

db = SessionLocal()

cars = [
    Car(name="Toyota Corolla", category="Sedan", status="available"),
    Car(name="Honda Civic", category="Sedan", status="available"),
    Car(name="Toyota Prado", category="SUV", status="available"),
    Car(name="Kia Sportage", category="SUV", status="available"),
    Car(name="Suzuki Alto", category="Economy", status="available"),
]

for car in cars:
    db.add(car)

db.commit()
db.close()

print("Cars seeded successfully.")
