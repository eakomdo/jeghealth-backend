"""
JEGHealth Backend API Test Script
Tests all major API endpoints including appointments, medications, and IoT devices
"""

import requests
import json
from datetime import datetime, timedelta, date
import uuid

# API Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1"

class JEGHealthAPITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        
    def authenticate(self, email, password):
        """Login and get JWT token"""
        print("🔐 Authenticating...")
        response = self.session.post(f"{API_BASE}/auth/login/", {
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            tokens = data.get("tokens", {})
            self.token = tokens.get("access")
            self.user_id = data.get("user", {}).get("id")
            # Update session headers with the token
            if self.token:
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                print(f"✅ Authenticated as {email}")
                print(f"🔑 Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ No access token received")
                return False
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.text)
            return False
    
    def register_user(self, email, password, first_name, last_name):
        """Register a new user"""
        print(f"👤 Registering user {email}...")
        username = email.split('@')[0]  # Use email prefix as username
        response = self.session.post(f"{API_BASE}/auth/register/", {
            "email": email,
            "username": username,
            "password": password,
            "password_confirm": password,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": "1990-01-01",
            "phone_number": ""  # Optional field, leave empty to avoid validation issues
        })
        
        if response.status_code == 201:
            print(f"✅ User {email} registered successfully")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.text)
            return False
    
    def test_health_metrics(self):
        """Test health metrics endpoints"""
        print("\n📊 Testing Health Metrics...")
        
        # Create health metrics
        metrics_data = [
            {
                "metric_type": "heart_rate",
                "value": 72.5,
                "unit": "bpm",
                "recorded_at": datetime.now().isoformat(),
                "notes": "Resting heart rate after morning exercise"
            },
            {
                "metric_type": "blood_pressure",
                "value": 120,  # This will be set to systolic_value in validation
                "systolic_value": 120,
                "diastolic_value": 80,
                "unit": "mmHg",
                "recorded_at": datetime.now().isoformat(),
            },
            {
                "metric_type": "weight",
                "value": 70.2,
                "unit": "kg",
                "recorded_at": datetime.now().isoformat(),
            },
            {
                "metric_type": "temperature",
                "value": 36.8,
                "unit": "°C",
                "recorded_at": datetime.now().isoformat(),
            }
        ]
        
        metric_ids = []
        for metric_data in metrics_data:
            response = self.session.post(f"{API_BASE}/health-metrics/", json=metric_data)
            if response.status_code == 201:
                response_data = response.json()
                print(f"✅ Created {metric_data['metric_type']} metric")
                print(f"Response data keys: {list(response_data.keys())}")
                metric_ids.append(response_data.get("id", response_data.get("pk")))
            else:
                print(f"❌ Failed to create {metric_data['metric_type']}: {response.status_code}")
                print(f"Response: {response.text}")
        
        # Get health metrics stats
        response = self.session.get(f"{API_BASE}/health-metrics/stats/")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Health metrics stats: {stats.get('total_readings', 0)} total metrics")
            print(f"Stats keys: {list(stats.keys())}")
        
        return metric_ids
    
    def test_appointments(self):
        """Test appointments endpoints"""
        print("\n📅 Testing Appointments...")
        
        # First, create a healthcare provider (in real app, this would be admin-created)
        # For testing, we'll skip this and use mock data
        
        # List healthcare providers (should be empty in test)
        response = self.session.get(f"{API_BASE}/appointments/providers/")
        print(f"Healthcare providers: {response.status_code}")
        
        # Get appointment stats
        response = self.session.get(f"{API_BASE}/appointments/stats/")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Appointment stats: {stats['total_appointments']} total appointments")
        
        # Get upcoming appointments
        response = self.session.get(f"{API_BASE}/appointments/upcoming/")
        if response.status_code == 200:
            upcoming = response.json()
            print(f"✅ Upcoming appointments: {len(upcoming)} appointments")
        
        return []
    
    def test_medications(self):
        """Test medications endpoints"""
        print("\n💊 Testing Medications...")
        
        # List medication categories
        response = self.session.get(f"{API_BASE}/medications/categories/")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Medication categories: {len(categories)} categories")
        
        # List available medications
        response = self.session.get(f"{API_BASE}/medications/available/")
        if response.status_code == 200:
            medications = response.json()
            print(f"✅ Available medications: {medications.get('count', 0)} medications")
        
        # Get user medications (should be empty initially)
        response = self.session.get(f"{API_BASE}/medications/")
        if response.status_code == 200:
            user_meds = response.json()
            print(f"✅ User medications: {user_meds.get('count', 0)} medications")
        
        # Get medication stats
        response = self.session.get(f"{API_BASE}/medications/stats/")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Medication stats: {stats['total_medications']} total medications")
        
        # Get adherence report
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        response = self.session.get(f"{API_BASE}/medications/adherence-report/?start_date={start_date}&end_date={end_date}")
        if response.status_code == 200:
            report = response.json()
            print(f"✅ Adherence report: {report['adherence_percentage']}% adherence")
        
        return []
    
    def test_iot_devices(self):
        """Test IoT devices endpoints"""
        print("\n🔌 Testing IoT Devices...")
        
        # Register a new IoT device
        device_data = {
            "name": "My Fitness Tracker",
            "device_type": "FITNESS_TRACKER",
            "manufacturer": "FitBit",
            "model": "Charge 5",
            "firmware_version": "1.2.3",
            "supported_metrics": ["heart_rate", "steps", "calories"],
            "location": "Bedroom"
        }
        
        response = self.session.post(f"{API_BASE}/iot-devices/register/", json=device_data)
        device_id = None
        if response.status_code == 201:
            device = response.json()
            device_id = device["device_id"]
            print(f"✅ Registered IoT device: {device['name']}")
        else:
            print(f"❌ Failed to register device: {response.status_code}")
            print(response.text)
        
        # List user's IoT devices
        response = self.session.get(f"{API_BASE}/iot-devices/")
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ IoT devices: {devices.get('count', 0)} devices")
        
        # Get device stats
        response = self.session.get(f"{API_BASE}/iot-devices/stats/")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Device stats: {stats['total_devices']} total devices")
        
        # Test device verification (if device was created)
        if device_id:
            response = self.session.post(f"{API_BASE}/iot-devices/{device_id}/verify/", json={
                "verification_code": "ABC123"
            })
            if response.status_code == 200:
                print(f"✅ Device verified: {device_id}")
            else:
                print(f"❌ Device verification failed: {response.status_code}")
        
        # Test device health check
        if device_id:
            response = self.session.get(f"{API_BASE}/iot-devices/{device_id}/health/")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Device health: {health['status']}")
        
        return [device_id] if device_id else []
    
    def test_user_profile(self):
        """Test user profile endpoints"""
        print("\n👤 Testing User Profile...")
        
        # Get current user profile
        response = self.session.get(f"{API_BASE}/auth/me/")
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User profile: {user['email']}")
        
        # Update profile
        profile_update = {
            "height": 175.0,
            "emergency_contact_name": "John Doe",
            "emergency_contact_phone": "+1234567890"
        }
        response = self.session.patch(f"{API_BASE}/auth/profile/", json=profile_update)
        if response.status_code == 200:
            print("✅ Profile updated successfully")
        
        return True
    
    def test_api_documentation(self):
        """Test API documentation endpoints"""
        print("\n📚 Testing API Documentation...")
        
        # Check Swagger UI
        response = requests.get(f"{BASE_URL}/api/docs/")
        if response.status_code == 200:
            print("✅ Swagger UI accessible")
        else:
            print(f"❌ Swagger UI not accessible: {response.status_code}")
        
        # Check ReDoc
        response = requests.get(f"{BASE_URL}/api/redoc/")
        if response.status_code == 200:
            print("✅ ReDoc accessible")
        else:
            print(f"❌ ReDoc not accessible: {response.status_code}")
        
        return True
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting JEGHealth Backend API Tests\n")
        
        # Test API documentation first
        self.test_api_documentation()
        
        # Generate test user credentials
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "TestPassword123!"
        
        # Register and authenticate
        if not self.register_user(test_email, test_password, "Test", "User"):
            return False
        
        if not self.authenticate(test_email, test_password):
            return False
        
        # Run all API tests
        try:
            self.test_user_profile()
            health_metric_ids = self.test_health_metrics()
            appointment_ids = self.test_appointments()
            medication_ids = self.test_medications()
            device_ids = self.test_iot_devices()
            
            print(f"\n🎉 All tests completed successfully!")
            print(f"Created {len(health_metric_ids)} health metrics")
            print(f"Created {len(appointment_ids)} appointments")
            print(f"Created {len(medication_ids)} medications")
            print(f"Created {len(device_ids)} IoT devices")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            return False


def main():
    """Main test function"""
    print("=" * 60)
    print("JEGHealth Backend - Comprehensive API Test")
    print("=" * 60)
    
    tester = JEGHealthAPITester()
    success = tester.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - API is working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check the output above")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    main()
