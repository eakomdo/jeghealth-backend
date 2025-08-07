import requests
import json

def test_simple_provider():
    """Test with minimal required data only"""
    
    provider_data = {
        "email": "simple@test.com",
        "username": "simpletest",
        "first_name": "Simple",
        "last_name": "Test",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "professional_title": "Dr.",
        "organization_facility": "Test Hospital",
        "professional_role": "Other",
        "license_number": "SIMPLE123"
    }
    
    print("🧪 Testing Simple Provider Registration...")
    print(f"📋 Request Data: {json.dumps(provider_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/provider/register/",
            json=provider_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Simple provider registration successful!")
        else:
            print("❌ Simple provider registration failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_simple_provider()