import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_KEY = "RENTACAR_ELITE_2026"

def test_overlap_and_analytics():
    print("--- Starting Overlap & Analytics Verification ---")
    
    # 1. Check Analytics
    print("Checking Analytics...")
    r_ana = requests.get(f"{BASE_URL}/admin/analytics", headers={"X-Admin-Key": ADMIN_KEY})
    d_ana = r_ana.json()
    assert d_ana["ok"] is True
    print(f"Total Bookings: {d_ana['total_bookings']}")
    
    # 2. Create first booking
    print("\nCreating first booking (Toyota Prado | SUV)...")
    payload1 = {
        "fullName": "Overlap Tester 1",
        "phoneNumber": "12345678",
        "pickupLocation": "Point A",
        "dropoffLocation": "Point B",
        "carCategory": "SUV",
        "pickupDateTime": "2026-07-01 10:00",
        "returnDateTime": "2026-07-01 12:00"
    }
    r1 = requests.post(f"{BASE_URL}/create-booking", json=payload1)
    d1 = r1.json()
    assert d1["success"] is True
    car1_id = d1["assignedCar"]["id"]
    print(f"Booking 1 Created. Car ID: {car1_id} | Ref: {d1['bookingReference']}")
    
    # 3. Try to overlap exactly
    print("\nAttempting to create overlapping booking for same category/time...")
    # Since we only have two SUVs (Toyota Prado, Kia Sportage), and one is taken, the next one should be auto-assigned.
    payload2 = {
        "fullName": "Overlap Tester 2",
        "phoneNumber": "87654321",
        "pickupLocation": "Point C",
        "dropoffLocation": "Point D",
        "carCategory": "SUV",
        "pickupDateTime": "2026-07-01 11:00", # Overlaps with 10:00-12:00
        "returnDateTime": "2026-07-01 13:00"
    }
    r2 = requests.post(f"{BASE_URL}/create-booking", json=payload2)
    d2 = r2.json()
    assert d2["success"] is True
    car2_id = d2["assignedCar"]["id"]
    print(f"Booking 2 Created. Assigned different car ID: {car2_id} | Ref: {d2['bookingReference']}")
    assert car1_id != car2_id
    
    # 4. Try to overlap when ALL cars are taken
    print("\nAttempting to overlap when ALL category cars are busy...")
    payload3 = {
        "fullName": "Overlap Tester 3",
        "phoneNumber": "99999999",
        "pickupLocation": "Point E",
        "dropoffLocation": "Point F",
        "carCategory": "SUV",
        "pickupDateTime": "2026-07-01 11:30", # Overlaps with both
        "returnDateTime": "2026-07-01 12:30"
    }
    r3 = requests.post(f"{BASE_URL}/create-booking", json=payload3)
    d3 = r3.json()
    assert d3["success"] is False
    assert d3["error"] == "NO_AVAILABILITY"
    print(f"✓ No availability correctly returned: {d3['message']}")
    
    print("\nOverlap & Analytics Verification Successful!")

if __name__ == "__main__":
    try:
        test_overlap_and_analytics()
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
