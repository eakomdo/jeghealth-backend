"""
Simple test for bulk metrics creation debugging
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_bulk_metrics():
    session = requests.Session()
    
    # Register and login
    timestamp = int(datetime.now().timestamp())
    email = f"bulk_test_{timestamp}@example.com"
    
    user_data = {
        "username": f"bulk_user_{timestamp}",
        "email": email,
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Bulk",
        "last_name": "Tester",
        "phone_number": "+14155552674",
        "date_of_birth": "1990-01-01",
        "gender": "MALE"
    }
    
    # Register
    response = session.post(f"{API_BASE}/auth/register/", json=user_data)
    if response.status_code != 201:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)
        return
    
    # Login
    response = session.post(f"{API_BASE}/auth/login/", {
        "email": email,
        "password": "testpass123"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()['tokens']['access']
    session.headers.update({'Authorization': f'Bearer {token}'})
    print(f"✅ Authenticated as {email}")
    
    # Register a device
    device_data = {
        "name": "Bulk Test Device",
        "device_type": "SMARTWATCH",
        "manufacturer": "BulkInc",
        "supported_metrics": ["heart_rate"]
    }
    
    response = session.post(f"{API_BASE}/iot-devices/register/", json=device_data)
    if response.status_code != 201:
        print(f"❌ Device registration failed: {response.status_code}")
        print(response.text)
        return
    
    device_id = response.json()['device_id']
    print(f"✅ Registered device: {device_id}")
    
    # Test bulk metrics
    bulk_data = {
        "device_id": device_id,
        "metrics": [
            {
                "metric_type": "heart_rate",
                "value": 75.0,
                "unit": "bpm",
                "recorded_at": datetime.now().isoformat()
            }
        ]
    }
    
    response = session.post(f"{API_BASE}/health-metrics/bulk-create/", json=bulk_data)
    print(f"Bulk create response: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_bulk_metrics()
