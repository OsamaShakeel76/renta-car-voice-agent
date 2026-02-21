import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_KEY = "RENTACAR_ELITE_2026"

def test_new_information():
    print("--- Testing with New Information ---")
    
    # Using a completely different name and phone
    payload = {
        "fullName": "Sarah Johnson",
        "phoneNumber": "03335556677",
        "pickupLocation": "Clifton Block 5",
        "dropoffLocation": "Bahria Town",
        "carCategory": "Sedan", # Using existing category
        "pickupDateTime": "2026-04-05 09:00",
        "returnDateTime": "2026-04-10 18:00"
    }
    
    print(f"Creating booking for: {payload['fullName']} ({payload['phoneNumber']})")
    resp = requests.post(f"{BASE_URL}/create-booking", json=payload)
    data = resp.json()
    
    assert data["success"] is True
    print(f"Booking Created! Reference: {data['bookingReference']}")
    print(f"Masked Name: {data['fullName']}")
    print(f"Masked Phone: {data['phoneNumber']}")
    
    # Expected masking Sarah Johnson -> S*** J***
    assert data["fullName"] == "S*** J***"
    # Expected masking 03335556677 -> 03***77
    assert data["phoneNumber"] == "03***77"
    
    print("\nVerifying on Dashboard...")
    dash_resp = requests.get(f"{BASE_URL}/get-all-bookings", headers={"X-Admin-Key": ADMIN_KEY})
    dash_data = dash_resp.json()
    
    latest = dash_data["bookings"][0]
    print(f"Latest on Dashboard: {latest['customerName']} | {latest['customerPhone']} | {latest['carCategory']}")
    
    assert latest["customerName"] == "S*** J***"
    assert latest["carCategory"] == "Luxury"
    
    print("\nResult: System works perfectly with new information!")

if __name__ == "__main__":
    try:
        test_new_information()
    except Exception as e:
        print(f"Test Failed: {e}")
