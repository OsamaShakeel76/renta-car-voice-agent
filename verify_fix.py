import requests
import os
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_KEY = "RENTACAR_ELITE_2026"

def test_data_accuracy():
    # 1. Create a booking with specific details
    print("Creating booking...")
    payload = {
        "fullName": "Muhammad Ali",
        "phoneNumber": "03001122334",
        "pickupDateTime": "2026-03-01 10:00",
        "returnDateTime": "2026-03-03 15:00",
        "pickupLocation": "Karachi Airport",
        "dropoffLocation": "Clifton",
        "carCategory": "SUV",
        "notes": "Testing final fix"
    }
    
    resp = requests.post(f"{BASE_URL}/create-booking", json=payload)
    data = resp.json()
    print(f"Create Response: {data}")
    
    assert data["success"] is True
    assert data["fullName"] == "Muhammad A."
    assert data["phoneNumber"] == "0300****334"
    # Verify ISO format in response (check for T and +05:00)
    assert "T" in data["pickupDateTime"]
    assert "+05:00" in data["pickupDateTime"]
    
    # 2. Verify in get-all-bookings
    print("\nVerifying in get-all-bookings...")
    resp = requests.get(f"{BASE_URL}/get-all-bookings", headers={"X-Admin-Key": ADMIN_KEY})
    bookings = resp.json()["bookings"]
    
    # Find our booking
    target = None
    for b in bookings:
        if b["customerPhone"] == "0300****334":
            target = b
            break
            
    assert target is not None
    assert target["customerName"] == "Muhammad A."
    assert target["pickupLocation"] == "Karachi Airport"
    assert target["dropoffLocation"] == "Clifton"
    assert target["carCategory"] == "SUV"
    print("Verification Successful: Masking and Data Accuracy confirmed.")

if __name__ == "__main__":
    import traceback
    try:
        test_data_accuracy()
    except Exception as e:
        print(f"Test Failed: {e}")
        traceback.print_exc()
