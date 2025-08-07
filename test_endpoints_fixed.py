import requests
import json

# Base URL for your API
BASE_URL = "http://localhost:8000/api/v1"

def test_provider_registration():
    """Test healthcare provider registration with corrected data"""
    
    # Test data for provider registration - CORRECTED VERSION
    provider_data = {
        "email": "doctor.smith@hospital.com",
        "username": "drsmith",
        "first_name": "John",
        "last_name": "Smith",
        "phone_number": "+12345678901",  # Fixed: Full international format
        "password": "securepassword123",
        "password_confirm": "securepassword123",
        
        # Professional Information
        "professional_title": "Dr.",
        "organization_facility": "General Hospital",
        "professional_role": "Other",  # Fixed: Using default choice
        "license_number": "MD123456789",
        "specialization": "Cardiology",
        "additional_information": "Interested in IoT heart monitoring devices",
        
        # Optional fields with defaults
        "years_of_experience": 10,
        "consultation_fee": 150.00,
        "bio": "Experienced cardiologist specializing in heart monitoring",
        "hospital_clinic": "General Hospital Cardiology Department",
        "address": "123 Medical Center Drive"
    }
    
    print("🧪 Testing Provider Registration (Fixed Version)...")
    print(f"📋 Request Data: {json.dumps(provider_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/provider/register/",
            json=provider_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📄 Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Provider registration successful!")
            return True
        else:
            print("❌ Provider registration failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure your Django server is running!")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_user_registration():
    """Test regular user registration with corrected data"""
    
    user_data = {
        "email": "patient@email.com",
        "username": "patient123",
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+19876543210",  # Fixed: Full international format
        "password": "userpassword123",
        "password_confirm": "userpassword123",
        "date_of_birth": "1990-05-15"
    }
    
    print("\n🧪 Testing User Registration (Fixed Version)...")
    print(f"📋 Request Data: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register/",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📄 Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 201:
            print("✅ User registration successful!")
            return True
        else:
            print("❌ User registration failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure your Django server is running!")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_provider_registration_alternative():
    """Test with different valid professional role choices"""
    
    # Try different combinations to find valid choices
    test_cases = [
        {"professional_role": "Other", "email": "doctor1@test.com", "username": "doctor1"},
        {"professional_role": "Doctor", "email": "doctor2@test.com", "username": "doctor2"},
        {"professional_role": "Nurse", "email": "nurse1@test.com", "username": "nurse1"},
        {"professional_role": "Pharmacist", "email": "pharmacist1@test.com", "username": "pharmacist1"},
    ]
    
    print("\n🧪 Testing Different Professional Role Choices...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['professional_role']} ---")
        
        provider_data = {
            "email": test_case["email"],
            "username": test_case["username"],
            "first_name": "Test",
            "last_name": "Provider",
            "phone_number": f"+1234567890{i}",
            "password": "testpassword123",
            "password_confirm": "testpassword123",
            "professional_title": "Dr.",
            "organization_facility": "Test Hospital",
            "professional_role": test_case["professional_role"],
            "license_number": f"TEST12345{i}",
            "specialization": "General Practice",
            "additional_information": "Test provider",
            "years_of_experience": 5,
            "consultation_fee": 100.00,
            "bio": "Test bio",
            "hospital_clinic": "Test Clinic",
            "address": "Test Address"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/provider/register/",
                json=provider_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 201:
                print(f"✅ {test_case['professional_role']} registration successful!")
            else:
                try:
                    error_details = response.json()
                    if 'professional_role' in str(error_details):
                        print(f"❌ Invalid choice: {test_case['professional_role']}")
                    else:
                        print(f"❌ Other error: {error_details}")
                except:
                    print(f"❌ Failed with status {response.status_code}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed. Make sure your Django server is running!")
            break
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
        
        try:
            response_json = response.json()
            print(f"📄 Response: {json.dumps(response_json, indent=2)}")
            
            if response.status_code == 200:
                print("✅ Login successful!")
                return response_json.get('access_token') or response_json.get('access')
            else:
                print("❌ Login failed!")
                
        except:
            print(f"📄 Response Text: {response.text}")
            
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
        
        try:
            response_json = response.json()
            print(f"📄 Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Current user endpoint successful!")
        else:
            print("❌ Current user endpoint failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure your Django server is running!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_database():
    """Check if records were created in database"""
    
    print("\n🗄️ Database Check Instructions:")
    print("Run these commands in a separate terminal to verify data:")
    print("1. Check healthcare providers:")
    print("   sqlite3 db.sqlite3 \"SELECT * FROM healthcare_providers;\"")
    print("2. Check users:")
    print("   sqlite3 db.sqlite3 \"SELECT id, email, first_name, last_name, username FROM accounts_user;\"")
    print("3. Check all tables:")
    print("   sqlite3 db.sqlite3 \".tables\"")

if __name__ == "__main__":
    print("🚀 Starting JegHealth Backend API Tests (Fixed Version)")
    print("=" * 60)
    
    # Test provider registration with corrected data
    provider_success = test_provider_registration()
    
    # Test user registration with corrected data
    user_success = test_user_registration()
    
    # Test different professional role choices to find valid ones
    test_provider_registration_alternative()
    
    # Test login (only if provider registration was successful)
    token = None
    if provider_success:
        token = test_login()
    
    # Test current user endpoint
    test_current_user(token)
    
    # Provide database check instructions
    check_database()
    
    print("\n" + "=" * 60)
    print("🏁 Testing Complete!")
    print("\n📋 Summary:")
    print(f"✅ Provider Registration: {'Success' if provider_success else 'Failed'}")
    print(f"✅ User Registration: {'Success' if user_success else 'Failed'}")
    print(f"✅ Authentication Token: {'Obtained' if token else 'Not obtained'}")
    
    if not provider_success and not user_success:
        print("\n💡 Next Steps:")
        print("1. Check the valid professional_role choices in providers/models.py")
        print("2. Verify phone number format requirements")
        print("3. Check Django server logs for detailed error messages")