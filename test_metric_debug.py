"""
Debug individual metrics in bulk creation
"""

import requests
from datetime import datetime, timedelta

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_individual_metrics():
    session = requests.Session()
    
    # Register and login
    timestamp = int(datetime.now().timestamp())
    email = f"debug_test_{timestamp}@example.com"
    
    user_data = {
        "username": f"debug_user_{timestamp}",
        "email": email,
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Debug",
        "last_name": "Tester",
        "phone_number": "+14155552675",
        "date_of_birth": "1990-01-01",
        "gender": "MALE"
    }
    
    # Register
    response = session.post(f"{API_BASE}/auth/register/", json=user_data)
    if response.status_code != 201:
        print(f"❌ Registration failed: {response.status_code}")
        return
    
    # Login
    response = session.post(f"{API_BASE}/auth/login/", {
        "email": email,
        "password": "testpass123"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json()['tokens']['access']
    session.headers.update({'Authorization': f'Bearer {token}'})
    print(f"✅ Authenticated as {email}")
    
    # Register a device
    device_data = {
        "name": "Debug Test Device",
        "device_type": "SMARTWATCH",
        "manufacturer": "DebugInc",
        "supported_metrics": ["heart_rate", "weight", "blood_pressure"]
    }
    
    response = session.post(f"{API_BASE}/iot-devices/register/", json=device_data)
    if response.status_code != 201:
        print(f"❌ Device registration failed: {response.status_code}")
        return
    
    device_id = response.json()['device_id']
    print(f"✅ Registered device: {device_id}")
    
    # Test each metric individually
    metrics = [
        {
            "metric_type": "heart_rate",
            "value": 75.0,
            "unit": "bpm",
            "recorded_at": (datetime.now() - timedelta(hours=1)).isoformat()
        },
        {
            "metric_type": "weight",
            "value": 70.5,
            "unit": "kg",
            "recorded_at": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            "metric_type": "blood_pressure",
            "systolic_value": 120.0,
            "diastolic_value": 80.0,
            "unit": "mmHg",
            "recorded_at": datetime.now().isoformat()
        }
    ]
    
    for i, metric in enumerate(metrics):
        print(f"\nTesting metric {i+1}: {metric['metric_type']}")
        bulk_data = {
            "device_id": device_id,
            "metrics": [metric]
        }
        
        response = session.post(f"{API_BASE}/health-metrics/bulk-create/", json=bulk_data)
        print(f"Response: {response.status_code}")
        if response.status_code != 201:
            print(f"Error: {response.text}")
        else:
            print("✅ Success")

if __name__ == "__main__":
    test_individual_metrics()
