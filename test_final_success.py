import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_KEY = "RENTACAR_ELITE_2026"

def test_final_success():
    print("--- Starting Final Success Verification ---")
    
    # 1. Test Create with Optional returnDateTime
    print("Testing Optional returnDateTime...")
    payload = {
        "fullName": "Real Name Test",
        "phoneNumber": "+923001234567",
        "pickupLocation": "Airport",
        "dropoffLocation": "Home",
        "carCategory": "sedan", # specifically testing lowercase
        "pickupDateTime": "2026-08-01 10:00"
    }
    r = requests.post(f"{BASE_URL}/create-booking", json=payload)
    d = r.json()
    assert d["success"] is True
    ref = d["bookingReference"]
    print(f"✓ Booking Created: {ref}")
    
    # 2. Test Get-All-Bookings Unmasked
    print("\nTesting Admin Dashboard Unmasking...")
    r_all = requests.get(f"{BASE_URL}/get-all-bookings?status=booked", headers={"X-Admin-Key": ADMIN_KEY})
    d_all = r_all.json()
    assert d_all["success"] is True
    last_booking = d_all["bookings"][0]
    print(f"Customer Name: {last_booking['customerName']}")
    print(f"Customer Phone: {last_booking['customerPhone']}")
    assert last_booking['customerName'] == "Real Name Test"
    assert last_booking['customerPhone'] == "+923001234567"
    print("✓ Admin Data is UNMASKED correctly.")
    
    print("\nFinal Success Verification Complete!")

if __name__ == "__main__":
    try:
        test_final_success()
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
