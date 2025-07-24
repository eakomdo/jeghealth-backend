"""
JEGHealth Backend - IoT Devices Comprehensive Test
Tests all IoT device endpoints in detail
"""

import requests
import json
from datetime import datetime, timedelta, date
import uuid

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class IoTDevicesTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.device_ids = []
        
    def authenticate(self, email=None, password="testpass123"):
        """Register a new user and authenticate"""
        if email is None:
            timestamp = int(datetime.now().timestamp())
            email = f"iot_test_{timestamp}@example.com"
        
        # Register user
        user_data = {
            "username": f"iot_user_{int(datetime.now().timestamp())}",
            "email": email,
            "password": password,
            "password_confirm": password,
            "first_name": "IoT",
            "last_name": "Tester",
            "phone_number": "+14155552671",
            "date_of_birth": "1990-01-01",
            "gender": "MALE"
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
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            tokens = data.get("tokens", {})
            self.token = tokens.get("access")
            self.user_id = data.get("user", {}).get("id")
            
            if self.token:
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                print(f"✅ Authenticated as {email}")
                return True
        
        print(f"❌ Authentication failed")
        return False
    
    def test_device_registration(self):
        """Test device registration with different device types"""
        print("\n🔌 Testing Device Registration...")
        
        devices_to_register = [
            {
                "name": "Apple Watch Series 9",
                "device_type": "SMARTWATCH",
                "manufacturer": "Apple",
                "model": "Series 9",
                "firmware_version": "10.1.1",
                "supported_metrics": ["heart_rate", "steps", "calories"],
                "location": "Wrist"
            },
            {
                "name": "Omron Blood Pressure Monitor",
                "device_type": "BLOOD_PRESSURE_MONITOR", 
                "manufacturer": "Omron",
                "model": "BP785N",
                "firmware_version": "2.1.0",
                "supported_metrics": ["blood_pressure"],
                "location": "Home Office"
            },
            {
                "name": "Withings Body+",
                "device_type": "SCALE",
                "manufacturer": "Withings",
                "model": "Body+",
                "firmware_version": "1.3.2",
                "supported_metrics": ["weight"],
                "location": "Bathroom"
            }
        ]
        
        for device_data in devices_to_register:
            response = self.session.post(f"{API_BASE}/iot-devices/register/", json=device_data)
            if response.status_code == 201:
                device = response.json()
                device_id = device["device_id"]
                self.device_ids.append(device_id)
                print(f"✅ Registered {device['name']} - ID: {device_id}")
            else:
                print(f"❌ Failed to register {device_data['name']}: {response.status_code}")
                print(response.text)
        
        return len(self.device_ids)
    
    def test_device_listing_and_filtering(self):
        """Test device listing with various filters"""
        print("\n📋 Testing Device Listing and Filtering...")
        
        # List all devices
        response = self.session.get(f"{API_BASE}/iot-devices/")
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ All devices: {devices.get('count', 0)} total")
        
        # Filter by device type
        response = self.session.get(f"{API_BASE}/iot-devices/?device_type=SMARTWATCH")
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ Smartwatches: {devices.get('count', 0)} devices")
        
        # Filter by status
        response = self.session.get(f"{API_BASE}/iot-devices/?status=INACTIVE")
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ Inactive devices: {devices.get('count', 0)} devices")
        
        # Search by manufacturer
        response = self.session.get(f"{API_BASE}/iot-devices/?search=Apple")
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ Apple devices: {devices.get('count', 0)} devices")
        
        # Filter verified devices only
        response = self.session.get(f"{API_BASE}/iot-devices/?verified_only=true")
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ Verified devices: {devices.get('count', 0)} devices")
    
    def test_device_details(self):
        """Test getting device details"""
        print("\n🔍 Testing Device Details...")
        
        for device_id in self.device_ids[:2]:  # Test first 2 devices
            response = self.session.get(f"{API_BASE}/iot-devices/{device_id}/")
            if response.status_code == 200:
                device = response.json()
                print(f"✅ Device details for {device['name']}: {device['device_type']}")
            else:
                print(f"❌ Failed to get details for device {device_id}: {response.status_code}")
    
    def test_device_verification(self):
        """Test device verification process"""
        print("\n🔐 Testing Device Verification...")
        
        for device_id in self.device_ids:
            # Test verification
            response = self.session.post(f"{API_BASE}/iot-devices/{device_id}/verify/", json={
                "verification_code": "ABC123"
            })
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Device {device_id} verified: {result.get('message', 'Success')}")
            else:
                print(f"❌ Failed to verify device {device_id}: {response.status_code}")
                print(response.text)
    
    def test_device_configuration(self):
        """Test device configuration updates"""
        print("\n⚙️ Testing Device Configuration...")
        
        if self.device_ids:
            device_id = self.device_ids[0]
            config_data = {
                "configuration": {
                    "sampling_rate": 60,
                    "data_retention_days": 30,
                    "auto_sync": True,
                    "notifications": {
                        "low_battery": True,
                        "sync_errors": True
                    }
                }
            }
            
            response = self.session.post(f"{API_BASE}/iot-devices/{device_id}/configure/", json=config_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Device configuration updated: {result.get('message', 'Success')}")
            else:
                print(f"❌ Failed to configure device: {response.status_code}")
                print(response.text)
    
    def test_device_health_checks(self):
        """Test device health checks"""
        print("\n❤️ Testing Device Health Checks...")
        
        for device_id in self.device_ids:
            response = self.session.get(f"{API_BASE}/iot-devices/{device_id}/health/")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Health check for {device_id}: {health.get('status', 'unknown')}")
            else:
                print(f"❌ Health check failed for {device_id}: {response.status_code}")
    
    def test_device_data_sync(self):
        """Test device data synchronization"""
        print("\n🔄 Testing Device Data Sync...")
        
        if self.device_ids:
            device_id = self.device_ids[0]
            
            # Simulate data sync
            sync_data = {
                "data_points": [
                    {
                        "metric_type": "heart_rate",
                        "value": 75,
                        "timestamp": datetime.now().isoformat(),
                        "accuracy": 0.95
                    },
                    {
                        "metric_type": "steps", 
                        "value": 8500,
                        "timestamp": datetime.now().isoformat(),
                        "accuracy": 0.99
                    }
                ]
            }
            
            response = self.session.post(f"{API_BASE}/iot-devices/{device_id}/sync/", json=sync_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Data sync successful: {result.get('message', 'Success')}")
            else:
                print(f"❌ Data sync failed: {response.status_code}")
                print(response.text)
    
    def test_device_updates(self):
        """Test device updates"""
        print("\n✏️ Testing Device Updates...")
        
        if self.device_ids:
            device_id = self.device_ids[0]
            
            update_data = {
                "location": "Living Room",
                "firmware_version": "10.1.2"
            }
            
            response = self.session.patch(f"{API_BASE}/iot-devices/{device_id}/update/", json=update_data)
            if response.status_code == 200:
                device = response.json()
                print(f"✅ Device updated: location = {device.get('location')}")
            else:
                print(f"❌ Device update failed: {response.status_code}")
                print(response.text)
    
    def test_device_data_batches(self):
        """Test device data batches"""
        print("\n📦 Testing Device Data Batches...")
        
        # List data batches
        response = self.session.get(f"{API_BASE}/iot-devices/data-batches/")
        if response.status_code == 200:
            batches = response.json()
            print(f"✅ Data batches: {batches.get('count', 0)} batches")
        else:
            print(f"❌ Failed to get data batches: {response.status_code}")
    
    def test_device_alerts(self):
        """Test device alerts"""
        print("\n🚨 Testing Device Alerts...")
        
        # List alerts
        response = self.session.get(f"{API_BASE}/iot-devices/alerts/")
        if response.status_code == 200:
            alerts = response.json()
            print(f"✅ Device alerts: {alerts.get('count', 0)} alerts")
        else:
            print(f"❌ Failed to get alerts: {response.status_code}")
    
    def test_device_statistics(self):
        """Test device statistics"""
        print("\n📊 Testing Device Statistics...")
        
        response = self.session.get(f"{API_BASE}/iot-devices/stats/")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Device stats: {stats.get('total_devices', 0)} total devices")
            print(f"    - Active: {stats.get('active_devices', 0)}")
            print(f"    - Verified: {stats.get('verified_devices', 0)}")
            print(f"    - Online: {stats.get('online_devices', 0)}")
        else:
            print(f"❌ Failed to get device stats: {response.status_code}")
    
    def test_device_deletion(self):
        """Test device deletion"""
        print("\n🗑️ Testing Device Deletion...")
        
        if self.device_ids:
            # Delete the last device
            device_id = self.device_ids[-1]
            
            response = self.session.delete(f"{API_BASE}/iot-devices/{device_id}/delete/")
            if response.status_code == 204:
                print(f"✅ Device {device_id} deleted successfully")
                self.device_ids.remove(device_id)
            else:
                print(f"❌ Failed to delete device {device_id}: {response.status_code}")
    
    def run_all_tests(self):
        """Run all IoT device tests"""
        print("=" * 60)
        print("JEGHealth Backend - IoT Devices Comprehensive Test")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ Authentication failed, stopping tests")
            return
        
        try:
            # Test device registration
            devices_created = self.test_device_registration()
            
            if devices_created > 0:
                # Test all device operations
                self.test_device_listing_and_filtering()
                self.test_device_details()
                self.test_device_verification()
                self.test_device_configuration()
                self.test_device_health_checks()
                self.test_device_data_sync()
                self.test_device_updates()
                self.test_device_data_batches()
                self.test_device_alerts()
                self.test_device_statistics()
                self.test_device_deletion()
                
                print(f"\n🎉 All IoT device tests completed!")
                print(f"Created and tested {devices_created} devices")
                print(f"Remaining devices: {len(self.device_ids)}")
            else:
                print("❌ No devices were registered, skipping further tests")
                
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
        
        print("=" * 60)
        print("✅ IoT DEVICES TEST COMPLETED")
        print("=" * 60)


if __name__ == "__main__":
    tester = IoTDevicesTester()
    tester.run_all_tests()
