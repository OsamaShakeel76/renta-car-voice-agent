import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_KEY = "RENTACAR_ELITE_2026"

def test_elite_logic():
    print("--- Starting Elite Verification ---")
    
    # 1. Create first booking
    payload1 = {
        "fullName": "Ijaz Ahmad",
        "phoneNumber": "+923001234567",
        "pickupLocation": "Airport",
        "dropoffLocation": "Home",
        "carCategory": "SUV",
        "pickupDateTime": "2026-03-10 12:00",
        "returnDateTime": "2026-03-12 10:00"
    }
    
    print("Creating first booking...")
    r1 = requests.post(f"{BASE_URL}/create-booking", json=payload1)
    d1 = r1.json()
    assert d1["success"] is True
    assert d1["status"] == "booked"
    print(f"Ref1: {d1['bookingReference']}")
    assert d1["fullName"] == "I*** A***"
    assert d1["phoneNumber"] == "+9***67"
    
    # 2. Create second booking and check sequence
    print("\nCreating second booking...")
    r2 = requests.post(f"{BASE_URL}/create-booking", json=payload1)
    d2 = r2.json()
    assert d2["success"] is True
    print(f"Ref2: {d2['bookingReference']}")
    
    ref1_num = int(d1["bookingReference"].split("-")[-1])
    ref2_num = int(d2["bookingReference"].split("-")[-1])
    assert ref2_num == ref1_num + 1
    
    # 3. Check Dashboard (All Bookings)
    print("\nChecking Dashboard...")
    r3 = requests.get(f"{BASE_URL}/get-all-bookings?status=booked", headers={"X-Admin-Key": ADMIN_KEY})
    d3 = r3.json()
    assert d3["success"] is True
    assert len(d3["bookings"]) >= 2
    
    target = d3["bookings"][0] # Latest
    assert target["customerName"] == "I*** A***"
    assert target["customerPhone"] == "+9***67"
    assert target["status"] == "booked"
    
    print("\nElite Verification Successful!")

if __name__ == "__main__":
    try:
        test_elite_logic()
    except Exception as e:
        print(f"\nVerification Failed: {e}")
        import traceback
        traceback.print_exc()
