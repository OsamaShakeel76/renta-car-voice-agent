import sqlite3

def audit_db():
    conn = sqlite3.connect("rentacar.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM cars")
    car_count = cursor.fetchone()[0]
    print(f"Total Cars: {car_count}")
    
    cursor.execute("SELECT category, COUNT(*) FROM cars GROUP BY category")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
        
    cursor.execute("SELECT COUNT(*) FROM bookings")
    booking_count = cursor.fetchone()[0]
    print(f"Total Bookings: {booking_count}")
    
    cursor.execute("SELECT status, COUNT(*) FROM bookings GROUP BY status")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
        
    conn.close()

if __name__ == "__main__":
    audit_db()
