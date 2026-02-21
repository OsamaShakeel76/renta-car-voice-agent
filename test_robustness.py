import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_KEY = "RENTACAR_ELITE_2026"

def test_robustness():
    print("--- Starting Robustness Verification ---")
    
    # 1. Test Optional returnDateTime
    print("Testing Optional returnDateTime...")
    payload_no_return = {
        "fullName": "Optional Return User",
        "phoneNumber": "00000000",
        "pickupLocation": "Airport",
        "dropoffLocation": "Home",
        "carCategory": "Sedan",
        "pickupDateTime": "2026-05-01 10:00"
        # returnDateTime omitted
    }
    r = requests.post(f"{BASE_URL}/create-booking", json=payload_no_return)
    d = r.json()
    assert d["success"] is True
    assert d["returnDateTime"] is None
    print("✓ Optional returnDateTime works.")
    
    # 2. Test UTC Normalization
    print("\nTesting UTC Normalization (-05:00 offset)...")
    payload_tz = {
        "fullName": "TZ User",
        "phoneNumber": "11111111",
        "pickupLocation": "Airport",
        "dropoffLocation": "Home",
        "carCategory": "Sedan",
        "pickupDateTime": "2026-06-01T10:00:00-05:00",
        "returnDateTime": "2026-06-03T15:00:00Z"
    }
    r = requests.post(f"{BASE_URL}/create-booking", json=payload_tz)
    d = r.json()
    assert d["success"] is True
    # 2026-06-01T10:00:00-05:00 normalized to UTC is 15:00
    assert "T15:00:00" in d["pickupDateTime"]
    print("✓ UTC Normalization works (normalized to UTC naive).")
    
    print("\nRobustness Verification Successful!")

if __name__ == "__main__":
    try:
        test_robustness()
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
