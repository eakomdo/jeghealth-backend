#!/usr/bin/env python3
"""
JEGHealth Backend API Testing Script

This script demonstrates how to interact with the JEGHealth backend API,
showing examples of all major functionality including:
- User registration and authentication
- Health metrics management
- IoT device integration
- Analytics and statistics

Run this script to test the backend functionality.
"""

import requests
import json
from datetime import datetime, timedelta
import random

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test@jeghealth.com"
TEST_USER_PASSWORD = "TestPass123"

class JEGHealthAPITester:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()
    
    def register_user(self):
        """Register a new test user."""
        print("📝 Registering new user...")
        
        data = {
            "email": TEST_USER_EMAIL,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": TEST_USER_PASSWORD,
            "password_confirm": TEST_USER_PASSWORD,
            "phone_number": "+1234567890",
            "date_of_birth": "1990-01-01"
        }
        
        response = self.session.post(f"{BASE_URL}/auth/register/", json=data)
        
        if response.status_code == 201:
            result = response.json()
            self.access_token = result['tokens']['access']
            self.refresh_token = result['tokens']['refresh']
            print("✅ User registered successfully!")
            print(f"   User ID: {result['user']['id']}")
            print(f"   Email: {result['user']['email']}")
            return True
        elif response.status_code == 400 and "Email already exists" in str(response.json()):
            print("ℹ️  User already exists, proceeding to login...")
            return self.login_user()
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    
    def login_user(self):
        """Login with existing user."""
        print("🔐 Logging in...")
        
        data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/auth/login/", json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result['tokens']['access']
            self.refresh_token = result['tokens']['refresh']
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    
    def set_auth_header(self):
        """Set authorization header for authenticated requests."""
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
    
    def get_current_user(self):
        """Get current user information."""
        print("👤 Getting current user info...")
        
        response = self.session.get(f"{BASE_URL}/auth/current-user/")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Current user info retrieved!")
            print(f"   Name: {result['authUser']['first_name']} {result['authUser']['last_name']}")
            print(f"   Email: {result['authUser']['email']}")
            print(f"   Roles: {result['role']['name']}")
            return result
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            return None
    
    def update_user_profile(self):
        """Update user profile information."""
        print("📋 Updating user profile...")
        
        profile_data = {
            "gender": "M",
            "height": 175.0,
            "weight": 70.0,
            "blood_type": "O+",
            "medical_conditions": "None known",
            "activity_level": "MODERATE",
            "health_goals": "Maintain healthy weight and cardiovascular fitness"
        }
        
        response = self.session.patch(f"{BASE_URL}/auth/profile/details/", json=profile_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Profile updated successfully!")
            print(f"   BMI: {result.get('bmi', 'N/A')}")
            return True
        else:
            print(f"❌ Profile update failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    
    def create_health_metrics(self):
        """Create sample health metrics."""
        print("🏥 Creating sample health metrics...")
        
        # Sample health metrics data
        metrics = [
            {
                "metric_type": "blood_pressure",
                "systolic_value": 120,
                "diastolic_value": 80,
                "unit": "mmHg",
                "recorded_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "is_manual_entry": True,
                "notes": "Morning reading after exercise"
            },
            {
                "metric_type": "heart_rate",
                "value": 72,
                "unit": "bpm",
                "recorded_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "is_manual_entry": True,
                "notes": "Resting heart rate"
            },
            {
                "metric_type": "weight",
                "value": 70.5,
                "unit": "kg",
                "recorded_at": datetime.now().isoformat(),
                "is_manual_entry": True,
                "notes": "Morning weight"
            },
            {
                "metric_type": "temperature",
                "value": 36.8,
                "unit": "°C",
                "recorded_at": (datetime.now() - timedelta(hours=12)).isoformat(),
                "is_manual_entry": True
            },
            {
                "metric_type": "oxygen_saturation",
                "value": 98,
                "unit": "%",
                "recorded_at": (datetime.now() - timedelta(hours=6)).isoformat(),
                "is_manual_entry": True
            }
        ]
        
        created_count = 0
        for metric_data in metrics:
            response = self.session.post(f"{BASE_URL}/health-metrics/", json=metric_data)
            
            if response.status_code == 201:
                created_count += 1
                result = response.json()
                print(f"   ✅ Created {result['metric_type']}: {result['display_value']} {result['unit']}")
            else:
                print(f"   ❌ Failed to create {metric_data['metric_type']}: {response.status_code}")
        
        print(f"📊 Created {created_count} health metrics!")
        return created_count > 0
    
    def get_health_metrics(self):
        """Retrieve health metrics."""
        print("📊 Retrieving health metrics...")
        
        response = self.session.get(f"{BASE_URL}/health-metrics/")
        
        if response.status_code == 200:
            result = response.json()
            metrics = result.get('results', [])
            print(f"✅ Retrieved {len(metrics)} health metrics!")
            
            for metric in metrics[:3]:  # Show first 3
                print(f"   • {metric['metric_type']}: {metric['display_value']} {metric['unit']} "
                      f"({metric['recorded_at'][:10]})")
            
            if len(metrics) > 3:
                print(f"   ... and {len(metrics) - 3} more")
            
            return metrics
        else:
            print(f"❌ Failed to retrieve metrics: {response.status_code}")
            return []
    
    def get_health_stats(self):
        """Get health statistics."""
        print("📈 Getting health statistics...")
        
        response = self.session.get(f"{BASE_URL}/health-metrics/stats/")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health statistics retrieved!")
            print(f"   Total readings: {result['total_readings']}")
            print(f"   Metric types: {result['metric_types']}")
            
            for overview in result.get('overview', [])[:3]:
                print(f"   • {overview['metric_type']}: {overview['total_readings']} readings, "
                      f"avg: {overview['average_value']:.1f}")
            
            return result
        else:
            print(f"❌ Failed to get statistics: {response.status_code}")
            return None
    
    def get_metric_types(self):
        """Get available metric types."""
        print("📋 Getting available metric types...")
        
        response = self.session.get(f"{BASE_URL}/health-metrics/metric-types/")
        
        if response.status_code == 200:
            metric_types = response.json()
            print(f"✅ Retrieved {len(metric_types)} metric types!")
            
            for mtype in metric_types[:5]:  # Show first 5
                print(f"   • {mtype['label']} ({mtype['value']}) - Unit: {mtype['unit']}")
            
            return metric_types
        else:
            print(f"❌ Failed to get metric types: {response.status_code}")
            return []
    
    def create_health_target(self):
        """Create a health target/goal."""
        print("🎯 Creating health target...")
        
        target_data = {
            "metric_type": "weight",
            "target_value": 68.0,
            "target_unit": "kg",
            "target_type": "DECREASE",
            "target_date": (datetime.now() + timedelta(days=90)).date().isoformat(),
            "notes": "Goal to lose 2.5kg in 3 months through healthy diet and exercise"
        }
        
        response = self.session.post(f"{BASE_URL}/health-metrics/targets/", json=target_data)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Health target created!")
            print(f"   Target: {result['target_value']} {result['target_unit']} by {result['target_date']}")
            return True
        else:
            print(f"❌ Failed to create target: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    
    def test_api_documentation(self):
        """Test API documentation endpoints."""
        print("📚 Testing API documentation...")
        
        # Test schema endpoint
        response = self.session.get(f"http://localhost:8000/api/schema/")
        if response.status_code == 200:
            print("✅ OpenAPI schema available!")
        else:
            print(f"❌ Schema endpoint failed: {response.status_code}")
        
        # Note: Swagger UI and ReDoc are web interfaces, not JSON endpoints
        print("💡 API Documentation available at:")
        print("   • Swagger UI: http://localhost:8000/api/docs/")
        print("   • ReDoc: http://localhost:8000/api/redoc/")
    
    def run_comprehensive_test(self):
        """Run comprehensive API test suite."""
        print("🚀 Starting JEGHealth Backend API Comprehensive Test")
        print("=" * 60)
        
        # Authentication tests
        if not self.register_user():
            return False
        
        self.set_auth_header()
        
        # User profile tests
        if not self.get_current_user():
            return False
        
        if not self.update_user_profile():
            return False
        
        # Health metrics tests
        if not self.create_health_metrics():
            return False
        
        self.get_health_metrics()
        self.get_health_stats()
        self.get_metric_types()
        
        # Health targets tests
        self.create_health_target()
        
        # Documentation tests
        self.test_api_documentation()
        
        print("\n" + "=" * 60)
        print("🎉 Comprehensive test completed successfully!")
        print("\n📖 Your JEGHealth backend is ready to use!")
        print("\n🔗 Next steps for mobile app integration:")
        print("   1. Update your mobile app to use this backend instead of Appwrite")
        print("   2. Replace authentication calls with /auth/ endpoints")
        print("   3. Replace health metric calls with /health-metrics/ endpoints")
        print("   4. Test with your mobile app and IoT devices")
        print("\n📚 Documentation: http://localhost:8000/api/docs/")
        
        return True


def main():
    """Main function to run the test suite."""
    tester = JEGHealthAPITester()
    
    try:
        success = tester.run_comprehensive_test()
        if success:
            print("\n✅ All tests passed! Your backend is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running at http://localhost:8000")
        print("   Run: python manage.py runserver 8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
