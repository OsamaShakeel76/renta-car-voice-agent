import requests
import time
import subprocess
import os

BASE_URL = "http://127.0.0.1:8000/api"

def test_flow():
    # 1. Check availability
    print("Testing check-availability...")
    resp = requests.post(f"{BASE_URL}/check-availability", json={
        "pickupDateTime": "2026-02-20 10:00",
        "returnDateTime": "2026-02-22 18:00",
        "carCategory": "SUV"
    })
    print(resp.json())
    assert resp.json()["success"] is True
    assert resp.json()["available"] is True

    # 2. Create booking
    print("\nTesting create-booking...")
    resp = requests.post(f"{BASE_URL}/create-booking", json={
        "fullName": "Ali Khan",
        "phoneNumber": "03001234567",
        "pickupDateTime": "2026-02-20 10:00",
        "returnDateTime": "2026-02-22 18:00",
        "pickupLocation": "Airport",
        "dropoffLocation": "City Center",
        "carCategory": "SUV",
        "notes": "Child seat required"
    })
    data = resp.json()
    print(data)
    assert data["success"] is True
    ref = data["bookingReference"]

    # 3. Check availability again (should be true with count 1 since 2 SUVs are seeded)
    print("\nTesting check-availability (partial overlap)...")
    resp = requests.post(f"{BASE_URL}/check-availability", json={
        "pickupDateTime": "2026-02-21 10:00",
        "returnDateTime": "2026-02-21 18:00",
        "carCategory": "SUV"
    })
    data = resp.json()
    print(data)
    assert data["available"] is True
    assert data["availableCount"] == 1

    # 4. Get booking (by reference)
    print("\nTesting get-booking (reference)...")
    resp = requests.post(f"{BASE_URL}/get-booking", json={"bookingReference": ref})
    print(resp.json())
    assert resp.json()["success"] is True

    # 4b. Get booking (by phone)
    print("\nTesting get-booking (phone)...")
    resp = requests.post(f"{BASE_URL}/get-booking", json={"phoneNumber": "03001234567"})
    print(resp.json())
    assert resp.json()["success"] is True

    # 5. Cancel booking (by phone)
    print("\nTesting cancel-booking (phone)...")
    resp = requests.post(f"{BASE_URL}/cancel-booking", json={"phoneNumber": "03001234567"})
    print(resp.json())
    assert resp.json()["success"] is True

    # 6. Check availability again (should be true now)
    print("\nTesting check-availability (after cancellation)...")
    resp = requests.post(f"{BASE_URL}/check-availability", json={
        "pickupDateTime": "2026-02-21 10:00",
        "returnDateTime": "2026-02-21 18:00",
        "carCategory": "SUV"
    })
    print(resp.json())
    assert resp.json()["available"] is True

if __name__ == "__main__":
    test_flow()
