#!/usr/bin/env python3
"""
Simple test script to interact with Dr. Jeg chatbot
"""

import os
import sys
import django
import json
import requests

# Setup Django environment
sys.path.append('/Users/phill/Desktop/jeghealth-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeghealth_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

def test_chatbot_conversation():
    print("🤖 Testing Dr. Jeg AI Chatbot")
    print("=" * 50)
    
    client = Client()
    
    # Create or get test user
    try:
        user = User.objects.get(email='test_chatbot@example.com')
        print("✓ Using existing test user")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_chatbot',
            email='test_chatbot@example.com', 
            password='testpass123'
        )
        print("✓ Created new test user")
    
    # Login to get token
    login_response = client.post('/api/v1/auth/login/', {
        'email': 'test_chatbot@example.com',
        'password': 'testpass123'
    })
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        # Extract token from nested structure
        tokens = login_data.get('tokens', {})
        token = tokens.get('access') or login_data.get('access')
        print("✓ Successfully authenticated")
        print(f"Token extracted: {token[:50]}...")
    else:
        print("✗ Authentication failed")
        print(f"Login error: {login_response.content.decode()}")
        return
    
    # Test conversation
    print("\n--- Starting Conversation with Dr. Jeg ---")
    
    message = "What is HIV AIDS and what could be causing this?"
    
    response = client.post(
        '/api/v1/dr-jeg/conversation/',
        {
            'message': message
        },
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Dr. Jeg responded successfully!")
        print(f"\n👤 You: {message}")
        print(f"\n🤖 Dr. Jeg: {data.get('response', 'No response text')}")
        
        if 'conversation_id' in data:
            print(f"\n📋 Conversation ID: {data['conversation_id']}")
        if 'tokens_used' in data:
            print(f"🔢 Tokens used: {data['tokens_used']}")
        if 'response_time_ms' in data:
            print(f"⏱️ Response time: {data['response_time_ms']}ms")
            
    else:
        print("✗ Dr. Jeg failed to respond")
        print(f"Error: {response.content.decode()}")
        
    # Test service status
    print("\n--- Checking Service Status ---")
    status_response = client.get(
        '/api/v1/dr-jeg/status/',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print("✓ Service status retrieved")
        print(f"Service: {status_data.get('service_status')}")
        stats = status_data.get('user_statistics', {})
        print(f"Your conversations: {stats.get('total_conversations', 0)}")
        print(f"Total messages: {stats.get('total_messages', 0)}")
    else:
        print("✗ Failed to get service status")

if __name__ == '__main__':
    test_chatbot_conversation()
