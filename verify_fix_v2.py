import requests
import os
import json

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_KEY = "RENTACAR_ELITE_2026"

def test_data_accuracy():
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
    
    print("--- Creating Booking ---")
    try:
        resp = requests.post(f"{BASE_URL}/create-booking", json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if not data.get("success"):
            print("FAILED: create-booking success is False")
            return
            
        print("\n--- Verifying Field Names and Masking ---")
        errors = []
        if data.get("fullName") != "Muhammad A.":
            errors.append(f"fullName mismatch: expected 'Muhammad A.', got '{data.get('fullName')}'")
        if data.get("phoneNumber") != "0300****334":
            errors.append(f"phoneNumber mismatch: expected '0300****334', got '{data.get('phoneNumber')}'")
            
        print("\n--- Listing All Bookings ---")
        resp = requests.get(f"{BASE_URL}/get-all-bookings", headers={"X-Admin-Key": ADMIN_KEY})
        resp.raise_for_status()
        all_bookings = resp.json()
        print(f"Total bookings: {all_bookings.get('total')}")
        
        found = False
        for b in all_bookings.get("bookings", []):
            if b.get("customerPhone") == "0300****334":
                found = True
                print(f"Found booking: {json.dumps(b, indent=2)}")
                if b.get("customerName") != "Muhammad A.":
                    errors.append(f"Dashboard customerName mismatch: {b.get('customerName')}")
                break
        
        if not found:
            errors.append("Booking not found in get-all-bookings")
            
        if errors:
            print("\nVERIFICATION FAILED:")
            for e in errors:
                print(f" - {e}")
        else:
            print("\nVERIFICATION SUCCESSFUL")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_data_accuracy()
