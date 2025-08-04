#!/usr/bin/env python3
"""
Test script for gender validation functionality
Tests login and profile update with gender field validation
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000/api/v1/auth"

# Test credentials
TEST_CREDENTIALS = {
    "email": "officialjwise20@gmail.com",
    "password": "Amoako@21"
}

def test_login():
    """Test login and get access token"""
    print("🔐 Testing Login...")
    response = requests.post(f"{BASE_URL}/login/", json=TEST_CREDENTIALS)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
        return data['tokens']['access']
    else:
        print("❌ Login failed!")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_profile_update_valid_gender(access_token):
    """Test profile update with valid gender (Male)"""
    print("\n👤 Testing Profile Update with Valid Gender (Male)...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    profile_data = {
        "gender": "M",  # Valid: Male
        "height": 175.0,
        "weight": 70.0,
        "blood_type": "O+"
    }
    
    response = requests.patch(f"{BASE_URL}/profile/details/", 
                             json=profile_data, 
                             headers=headers)
    
    if response.status_code == 200:
        print("✅ Profile update successful!")
        data = response.json()
        print(f"Gender: {data.get('gender', 'Not set')}")
        print(f"Height: {data.get('height', 'Not set')} cm")
        print(f"Weight: {data.get('weight', 'Not set')} kg")
    else:
        print("❌ Profile update failed!")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

def test_profile_update_valid_gender_female(access_token):
    """Test profile update with valid gender (Female)"""
    print("\n👩 Testing Profile Update with Valid Gender (Female)...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    profile_data = {
        "gender": "F",  # Valid: Female
        "height": 165.0,
        "weight": 60.0
    }
    
    response = requests.patch(f"{BASE_URL}/profile/details/", 
                             json=profile_data, 
                             headers=headers)
    
    if response.status_code == 200:
        print("✅ Profile update successful!")
        data = response.json()
        print(f"Gender: {data.get('gender', 'Not set')}")
    else:
        print("❌ Profile update failed!")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

def test_profile_update_invalid_gender(access_token):
    """Test profile update with invalid gender"""
    print("\n⚠️ Testing Profile Update with Invalid Gender (Other)...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    profile_data = {
        "gender": "O"  # Invalid: Other (not allowed anymore)
    }
    
    response = requests.patch(f"{BASE_URL}/profile/details/", 
                             json=profile_data, 
                             headers=headers)
    
    if response.status_code == 400:
        print("✅ Validation worked! Invalid gender rejected.")
        print(f"Error message: {response.text}")
    else:
        print("❌ Validation failed! Invalid gender was accepted.")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

def test_profile_update_case_insensitive(access_token):
    """Test profile update with lowercase gender (should be converted to uppercase)"""
    print("\n🔤 Testing Case Insensitive Gender Input...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    profile_data = {
        "gender": "m"  # Lowercase - should be converted to 'M'
    }
    
    response = requests.patch(f"{BASE_URL}/profile/details/", 
                             json=profile_data, 
                             headers=headers)
    
    if response.status_code == 200:
        print("✅ Case insensitive input successful!")
        data = response.json()
        print(f"Input: 'm' -> Stored as: {data.get('gender', 'Not set')}")
    else:
        print("❌ Case insensitive input failed!")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

def main():
    """Main test function"""
    print("🧪 Starting Gender Validation Tests")
    print("=" * 50)
    
    # Test login
    access_token = test_login()
    if not access_token:
        return
    
    # Test various gender validation scenarios
    test_profile_update_valid_gender(access_token)
    test_profile_update_valid_gender_female(access_token)
    test_profile_update_invalid_gender(access_token)
    test_profile_update_case_insensitive(access_token)
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")

if __name__ == "__main__":
    main()
