import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def get_error():
    payload = {
        "fullName": "Fatima Zahra",
        "phoneNumber": "03339988776",
        "pickupDateTime": "2026-03-05 09:00",
        "returnDateTime": "2026-03-07 18:00",
        "pickupLocation": "Gulshan",
        "dropoffLocation": "Defense",
        "carCategory": "Sedan",
        "notes": "Production-ready unmasked test"
    }
    resp = requests.post(f"{BASE_URL}/create-booking", json=payload)
    with open("debug_resp.json", "w") as f:
        json.dump(resp.json(), f, indent=2)
    print("Response saved to debug_resp.json")

if __name__ == "__main__":
    get_error()
