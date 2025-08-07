import requests
import json

# Base URL for your API
BASE_URL = "http://localhost:8000/api/v1"

def test_provider_registration():
    """Test healthcare provider registration"""
    
    # Test data for provider registration - FIXED VERSION
    provider_data = {
        "email": "doctor.smith@hospital.com",
        "username": "drsmith",  # Added username - required field
        "first_name": "John",
        "last_name": "Smith",
        "phone_number": "1234567890",  # Fixed phone format - no + or dashes
        "password": "securepassword123",
        "password_confirm": "securepassword123",
        
        # Professional Information
        "professional_title": "Dr.",
        "organization_facility": "General Hospital",
        "professional_role": "Doctor",  # Changed to proper choice value
        "license_number": "MD123456789",
        "specialization": "Cardiology",
        "additional_information": "Interested in IoT heart monitoring devices",
        
        # Optional fields
        "years_of_experience": 10,
        "consultation_fee": 150.00,
        "bio": "Experienced cardiologist specializing in heart monitoring",
        "hospital_clinic": "General Hospital Cardiology Department",
        "address": "123 Medical Center Drive"
    }
    
    print("🧪 Testing Provider Registration...")
    print(f"📋 Request Data: {json.dumps(provider_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/provider/register/",
            json=provider_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Provider registration successful!")
        else:
            print("❌ Provider registration failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure your Django server is running!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_user_registration():
    """Test regular user registration"""
    
    user_data = {
        "email": "patient@email.com",
        "username": "patient123",  # Username is required
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "9876543210",  # Fixed phone format
        "password": "userpassword123",
        "password_confirm": "userpassword123",
        "date_of_birth": "1990-05-15"
    }
    
    print("\n🧪 Testing User Registration...")
    print(f"📋 Request Data: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register/",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ User registration successful!")
        else:
            print("❌ User registration failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure your Django server is running!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_login():
    """Test user login"""
    
    login_data = {
        "email": "doctor.smith@hospital.com",
        "password": "securepassword123"
    }
    
    print("\n🧪 Testing Login...")
    print(f"📋 Request Data: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json().get('access_token')
        else:
            print("❌ Login failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure your Django server is running!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None

def test_current_user(token):
    """Test current user endpoint"""
    
    if not token:
        print("\n❌ No token available for current user test")
        return
    
    print("\n🧪 Testing Current User Endpoint...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/current-user/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Current user endpoint successful!")
        else:
            print("❌ Current user endpoint failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure your Django server is running!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting JegHealth Backend API Tests")
    print("=" * 50)
    
    # Test provider registration
    test_provider_registration()
    
    # Test user registration
    test_user_registration()
    
    # Test login and get token
    token = test_login()
    
    # Test current user endpoint
    test_current_user(token)
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")