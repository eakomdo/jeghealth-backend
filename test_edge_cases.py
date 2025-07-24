"""
JEGHealth Backend - Edge Cases and Advanced Test
Tests edge cases, error handling, and advanced features
"""

import requests
import json
from datetime import datetime, timedelta, date
import uuid

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class EdgeCasesTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.device_ids = []
        
    def authenticate(self):
        """Register a new user and authenticate"""
        timestamp = int(datetime.now().timestamp())
        email = f"edge_test_{timestamp}@example.com"
        
        # Register user
        user_data = {
            "username": f"edge_user_{timestamp}",
            "email": email,
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Edge",
            "last_name": "Tester",
            "phone_number": "+14155552672",
            "date_of_birth": "1990-01-01",
            "gender": "FEMALE"
        }
        
        register_response = self.session.post(f"{API_BASE}/auth/register/", json=user_data)
        if register_response.status_code != 201:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(register_response.text)
            return False
        
        print(f"✅ User {email} registered successfully")
        
        # Login
        response = self.session.post(f"{API_BASE}/auth/login/", {
            "email": email,
            "password": "testpass123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('tokens', {}).get('access')
            self.user_id = data.get('user', {}).get('id')
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            print(f"✅ Authenticated as {email}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.text)
            return False

    def test_invalid_device_operations(self):
        """Test operations with invalid device IDs"""
        print("\n🚫 Testing Invalid Device Operations...")
        
        fake_device_id = str(uuid.uuid4())
        
        # Test getting non-existent device
        response = self.session.get(f"{API_BASE}/iot-devices/{fake_device_id}/")
        if response.status_code == 404:
            print("✅ Non-existent device returns 404")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
        
        # Test updating non-existent device
        response = self.session.patch(f"{API_BASE}/iot-devices/{fake_device_id}/update/", json={
            "name": "Should not work"
        })
        if response.status_code == 404:
            print("✅ Update non-existent device returns 404")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
        
        # Test deleting non-existent device
        response = self.session.delete(f"{API_BASE}/iot-devices/{fake_device_id}/delete/")
        if response.status_code == 404:
            print("✅ Delete non-existent device returns 404")
        else:
            print(f"❌ Expected 404, got {response.status_code}")

    def test_device_validation(self):
        """Test device data validation"""
        print("\n✅ Testing Device Validation...")
        
        # Test invalid device type
        invalid_device = {
            "name": "Invalid Device",
            "device_type": "INVALID_TYPE",
            "manufacturer": "Test",
            "supported_metrics": ["heart_rate"]
        }
        
        response = self.session.post(f"{API_BASE}/iot-devices/register/", json=invalid_device)
        if response.status_code == 400:
            print("✅ Invalid device type rejected")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
        
        # Test invalid supported metrics
        invalid_metrics_device = {
            "name": "Invalid Metrics Device",
            "device_type": "SMARTWATCH",
            "manufacturer": "Test",
            "supported_metrics": ["invalid_metric", "another_invalid"]
        }
        
        response = self.session.post(f"{API_BASE}/iot-devices/register/", json=invalid_metrics_device)
        if response.status_code == 400:
            print("✅ Invalid metrics rejected")
        else:
            print(f"❌ Expected 400, got {response.status_code}")

    def test_device_configuration_edge_cases(self):
        """Test device configuration edge cases"""
        print("\n⚙️ Testing Device Configuration Edge Cases...")
        
        # Register a test device
        device_data = {
            "name": "Config Test Device",
            "device_type": "SMARTWATCH",
            "manufacturer": "EdgeCase Inc",
            "supported_metrics": ["heart_rate", "steps"]
        }
        
        response = self.session.post(f"{API_BASE}/iot-devices/register/", json=device_data)
        if response.status_code != 201:
            print(f"❌ Failed to register device: {response.status_code}")
            return
        
        device_id = response.json()['device_id']
        print(f"✅ Registered device: {device_id}")
        
        # Test complex configuration
        complex_config = {
            "configuration": {
                "sampling_rate": 60,
                "data_format": "json",
                "compression": True,
                "sensors": {
                    "heart_rate": {
                        "enabled": True,
                        "precision": "high",
                        "calibration": {
                            "offset": 0.5,
                            "scale": 1.02
                        }
                    },
                    "accelerometer": {
                        "enabled": False,
                        "sensitivity": "medium"
                    }
                },
                "connectivity": {
                    "wifi": {
                        "enabled": True,
                        "auto_connect": True
                    },
                    "bluetooth": {
                        "enabled": True,
                        "pairing_mode": "manual"
                    }
                },
                "power_management": {
                    "battery_saver": False,
                    "sleep_mode_timeout": 300
                }
            }
        }
        
        response = self.session.post(f"{API_BASE}/iot-devices/{device_id}/configure/", json=complex_config)
        if response.status_code == 200:
            print("✅ Complex configuration applied")
            config_response = response.json()
            if 'configuration' in config_response:
                print("✅ Configuration returned in response")
            else:
                print("❌ Configuration not returned in response")
        else:
            print(f"❌ Configuration failed: {response.status_code}")
            print(response.text)
        
        # Test invalid configuration (not a dict)
        invalid_config = {
            "configuration": "this should be a dict"
        }
        
        response = self.session.post(f"{API_BASE}/iot-devices/{device_id}/configure/", json=invalid_config)
        if response.status_code == 400:
            print("✅ Invalid configuration rejected")
        else:
            print(f"❌ Expected 400, got {response.status_code}")

    def test_bulk_health_metrics(self):
        """Test bulk health metrics operations"""
        print("\n📊 Testing Bulk Health Metrics...")
        
        # First register a device to get a device_id
        device_data = {
            "name": "Metrics Test Device",
            "device_type": "SMARTWATCH",
            "manufacturer": "MetricsInc",
            "supported_metrics": ["heart_rate", "weight", "blood_pressure"]
        }
        
        response = self.session.post(f"{API_BASE}/iot-devices/register/", json=device_data)
        if response.status_code != 201:
            print(f"❌ Failed to register device for metrics test: {response.status_code}")
            return
        
        device_id = response.json()['device_id']
        
        # Create multiple metrics at once
        bulk_metrics = [
            {
                "metric_type": "heart_rate",
                "value": 75.0,
                "unit": "bpm",
                "recorded_at": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                "metric_type": "heart_rate",
                "value": 120.0,
                "unit": "bpm",
                "recorded_at": (datetime.now() - timedelta(minutes=30)).isoformat()
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
        
        response = self.session.post(f"{API_BASE}/health-metrics/bulk-create/", json={
            "device_id": device_id,
            "metrics": bulk_metrics
        })
        if response.status_code == 201:
            result = response.json()
            created = result.get('metrics_created', 0)
            print(f"✅ Created {created} metrics in bulk")
        else:
            print(f"❌ Bulk creation failed: {response.status_code}")
            print(response.text)

    def test_health_metrics_filtering(self):
        """Test advanced health metrics filtering"""
        print("\n🔍 Testing Health Metrics Filtering...")
        
        # Test date range filtering
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'metric_type': 'heart_rate'
        }
        
        response = self.session.get(f"{API_BASE}/health-metrics/", params=params)
        if response.status_code == 200:
            metrics = response.json()
            print(f"✅ Filtered heart rate metrics: {len(metrics['results']) if 'results' in metrics else len(metrics)} found")
        else:
            print(f"❌ Filtering failed: {response.status_code}")

    def test_user_permissions(self):
        """Test that users can only access their own data"""
        print("\n🔒 Testing User Permissions...")
        
        # Create another user
        timestamp = int(datetime.now().timestamp()) + 1
        other_email = f"other_user_{timestamp}@example.com"
        
        other_user_data = {
            "username": f"other_user_{timestamp}",
            "email": other_email,
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Other",
            "last_name": "User",
            "phone_number": "+14155552673",
            "date_of_birth": "1990-01-01",
            "gender": "MALE"
        }
        
        # Register other user
        other_session = requests.Session()
        response = other_session.post(f"{API_BASE}/auth/register/", json=other_user_data)
        if response.status_code != 201:
            print(f"❌ Failed to create other user: {response.status_code}")
            return
        
        # Login other user
        response = other_session.post(f"{API_BASE}/auth/login/", {
            "email": other_email,
            "password": "testpass123"
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to login other user: {response.status_code}")
            return
        
        other_token = response.json()['tokens']['access']
        other_session.headers.update({'Authorization': f'Bearer {other_token}'})
        
        # Register a device with the first user
        device_data = {
            "name": "Permission Test Device",
            "device_type": "SMARTWATCH",
            "manufacturer": "Security Inc",
            "supported_metrics": ["heart_rate"]
        }
        
        response = self.session.post(f"{API_BASE}/iot-devices/register/", json=device_data)
        if response.status_code != 201:
            print(f"❌ Failed to register device with first user: {response.status_code}")
            return
        
        device_id = response.json()['device_id']
        
        # Try to access device with other user
        response = other_session.get(f"{API_BASE}/iot-devices/{device_id}/")
        if response.status_code == 404:
            print("✅ Other user cannot access device (returns 404)")
        else:
            print(f"❌ Security issue: Other user can access device (status: {response.status_code})")
        
        # Try to delete device with other user
        response = other_session.delete(f"{API_BASE}/iot-devices/{device_id}/delete/")
        if response.status_code == 404:
            print("✅ Other user cannot delete device (returns 404)")
        else:
            print(f"❌ Security issue: Other user can delete device (status: {response.status_code})")

    def test_performance_and_limits(self):
        """Test performance and limits"""
        print("\n⚡ Testing Performance and Limits...")
        
        # Test pagination
        response = self.session.get(f"{API_BASE}/health-metrics/", params={'page_size': 5})
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and 'count' in data:
                print("✅ Pagination working correctly")
            else:
                print("❌ Pagination response format incorrect")
        else:
            print(f"❌ Pagination test failed: {response.status_code}")
        
        # Test search functionality
        response = self.session.get(f"{API_BASE}/iot-devices/", params={'search': 'test'})
        if response.status_code == 200:
            print("✅ Search functionality working")
        else:
            print(f"❌ Search test failed: {response.status_code}")

    def run_all_tests(self):
        """Run all edge case tests"""
        print("============================================================")
        print("JEGHealth Backend - Edge Cases and Advanced Test")
        print("============================================================")
        
        if not self.authenticate():
            print("❌ Authentication failed, stopping tests")
            return
        
        self.test_invalid_device_operations()
        self.test_device_validation()
        self.test_device_configuration_edge_cases()
        self.test_bulk_health_metrics()
        self.test_health_metrics_filtering()
        self.test_user_permissions()
        self.test_performance_and_limits()
        
        print("\n🎉 All edge case tests completed!")
        print("============================================================")
        print("✅ EDGE CASES TEST COMPLETED")
        print("============================================================")

if __name__ == "__main__":
    tester = EdgeCasesTester()
    tester.run_all_tests()
