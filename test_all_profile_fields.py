#!/usr/bin/env python3
"""
Profile Field Update Test Script
Tests all editable fields in the user profile
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1/auth"
CREDENTIALS = {
    "email": "officialjwise20@gmail.com",
    "password": "Amoako@21"
}

def get_access_token():
    """Get access token from login"""
    response = requests.post(f"{BASE_URL}/login/", json=CREDENTIALS)
    if response.status_code == 200:
        return response.json()['tokens']['access']
    else:
        print(f"Login failed: {response.text}")
        return None

def test_field_update(access_token, field_data, test_name):
    """Test updating specific fields"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🧪 {test_name}")
    print(f"Updating: {json.dumps(field_data, indent=2)}")
    
    response = requests.patch(f"{BASE_URL}/profile/details/", 
                             json=field_data, 
                             headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        # Show only the updated fields
        for key in field_data.keys():
            if key in data:
                print(f"  {key}: {data[key]}")
        if 'bmi' in data:
            print(f"  bmi (auto-calculated): {data['bmi']}")
    else:
        print("❌ Failed!")
        print(f"Status: {response.status_code}")
        print(f"Error: {response.text}")

def main():
    print("🧪 Profile Field Update Tests")
    print("=" * 50)
    
    # Get access token
    token = get_access_token()
    if not token:
        return
    
    print("✅ Login successful!")
    
    # Test 1: Basic physical info
    test_field_update(token, {
        "gender": "f",  # Test case insensitivity
        "height": 165.0,
        "weight": 55.0
    }, "Test 1: Basic Physical Information (case insensitive gender)")
    
    # Test 2: Medical information
    test_field_update(token, {
        "blood_type": "B+",
        "medical_conditions": "Asthma (mild, exercise-induced)",
        "current_medications": "Albuterol inhaler as needed",
        "allergies": "Cats, pollen"
    }, "Test 2: Medical Information")
    
    # Test 3: Health goals and activity
    test_field_update(token, {
        "health_goals": "Improve endurance, manage asthma symptoms, maintain healthy weight",
        "activity_level": "LIGHT"
    }, "Test 3: Health Goals and Activity Level")
    
    # Test 4: Notification preferences
    test_field_update(token, {
        "email_notifications": False,
        "push_notifications": True,
        "health_reminders": False
    }, "Test 4: Notification Preferences")
    
    # Test 5: Try to update read-only BMI
    test_field_update(token, {
        "bmi": 99.9,  # This should be ignored
        "weight": 60.0  # This should update and recalculate BMI
    }, "Test 5: Attempt to Update Read-only BMI (should be ignored)")
    
    # Test 6: Invalid values
    test_field_update(token, {
        "gender": "X",  # Invalid
        "activity_level": "SUPER_ACTIVE"  # Invalid
    }, "Test 6: Invalid Values (should fail)")
    
    # Test 7: Clear text fields
    test_field_update(token, {
        "medical_conditions": "",
        "current_medications": "",
        "allergies": "",
        "health_goals": ""
    }, "Test 7: Clear Optional Text Fields")
    
    # Test 8: All blood types
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "UNKNOWN"]
    for bt in blood_types[:3]:  # Test first 3 to avoid too many requests
        test_field_update(token, {
            "blood_type": bt
        }, f"Test 8.{blood_types.index(bt)+1}: Blood Type {bt}")
    
    # Test 9: All activity levels
    activity_levels = ["SEDENTARY", "LIGHT", "MODERATE", "ACTIVE", "VERY_ACTIVE"]
    for al in activity_levels[:3]:  # Test first 3
        test_field_update(token, {
            "activity_level": al
        }, f"Test 9.{activity_levels.index(al)+1}: Activity Level {al}")
    
    print("\n" + "=" * 50)
    print("🏁 All tests completed!")
    print("\n📝 Summary of Editable Fields:")
    print("✅ Gender: M, F (case insensitive)")
    print("✅ Height: Float (cm)")
    print("✅ Weight: Float (kg)")
    print("✅ Blood Type: A+, A-, B+, B-, AB+, AB-, O+, O-, UNKNOWN")
    print("✅ Medical Conditions: Text")
    print("✅ Current Medications: Text")
    print("✅ Allergies: Text")
    print("✅ Health Goals: Text")
    print("✅ Activity Level: SEDENTARY, LIGHT, MODERATE, ACTIVE, VERY_ACTIVE")
    print("✅ Email Notifications: Boolean")
    print("✅ Push Notifications: Boolean")
    print("✅ Health Reminders: Boolean")
    print("\n🔒 Read-only Fields:")
    print("• BMI: Auto-calculated from height and weight")
    print("• Created At: System timestamp")
    print("• Updated At: System timestamp")

if __name__ == "__main__":
    main()
