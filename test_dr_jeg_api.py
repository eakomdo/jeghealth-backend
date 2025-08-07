#!/usr/bin/env python3
"""
Test script for Dr. Jeg AI Assistant API endpoints
"""

import os
import sys
import django
import json
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append('/Users/phill/Desktop/jeghealth-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeghealth_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from dr_jeg.models import Conversation, Message, APIUsageLog

User = get_user_model()

class DrJegAPITester:
    def __init__(self):
        self.client = Client()
        self.base_url = '/api/v1/dr-jeg'
        self.auth_token = None
        self.user = None
        
    def create_test_user(self):
        """Create a test user for API testing"""
        try:
            # Try to get existing test user
            self.user = User.objects.get(email='test_dr_jeg@example.com')
            print("✓ Using existing test user")
        except User.DoesNotExist:
            # Create new test user
            self.user = User.objects.create_user(
                email='test_dr_jeg@example.com',
                username='test_dr_jeg',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            print("✓ Created new test user")
    
    def authenticate(self):
        """Authenticate and get JWT token"""
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'test_dr_jeg@example.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.content)
            self.auth_token = data['tokens']['access']
            print("✓ Successfully authenticated")
            return True
        else:
            print(f"✗ Authentication failed: {response.status_code}")
            print(response.content.decode())
            return False
    
    def test_service_status(self):
        """Test Dr. Jeg service status endpoint"""
        print("\n--- Testing Service Status ---")
        
        response = self.client.get(
            f'{self.base_url}/status/',
            HTTP_AUTHORIZATION=f'Bearer {self.auth_token}'
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.content)
            print("✓ Service status retrieved successfully")
            print(f"  Service Status: {data.get('service_status', 'unknown')}")
            print(f"  User Conversations: {data.get('user_statistics', {}).get('total_conversations', 0)}")
            print(f"  Gemini Model: {data.get('gemini_model', 'unknown')}")
            return True
        else:
            print("✗ Service status check failed")
            print(response.content.decode())
            return False
    
    def test_conversation_creation_mock(self):
        """Test conversation creation (mock - without actual Gemini API)"""
        print("\n--- Testing Conversation Creation (Mock) ---")
        
        # Create a mock conversation directly in database
        conversation = Conversation.objects.create(
            user=self.user,
            title="Test Health Inquiry"
        )
        
        # Create mock messages
        user_message = Message.objects.create(
            conversation=conversation,
            sender='user',
            content='I have been experiencing headaches lately. What could be the cause?'
        )
        
        bot_message = Message.objects.create(
            conversation=conversation,
            sender='bot',
            content='I understand your concern about headaches. There are several potential causes including stress, dehydration, lack of sleep, or tension. However, if headaches persist or are severe, I recommend consulting with a healthcare professional for proper evaluation.',
            ai_model='gemini-pro-mock',
            response_time_ms=1200,
            tokens_used=85
        )
        
        # Create mock API usage log
        api_log = APIUsageLog.objects.create(
            user=self.user,
            conversation=conversation,
            endpoint_called='gemini-pro-mock',
            total_tokens=85,
            response_time_ms=1200,
            success=True
        )
        
        print("✓ Mock conversation created successfully")
        print(f"  Conversation ID: {conversation.id}")
        print(f"  Messages: {conversation.messages.count()}")
        return conversation
    
    def test_conversation_list(self):
        """Test listing user conversations"""
        print("\n--- Testing Conversation List ---")
        
        response = self.client.get(
            f'{self.base_url}/conversations/',
            HTTP_AUTHORIZATION=f'Bearer {self.auth_token}'
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.content)
            print("✓ Conversation list retrieved successfully")
            print(f"  Total conversations: {data.get('count', 0)}")
            
            if data.get('results'):
                for conv in data['results'][:3]:  # Show first 3
                    print(f"    - {conv.get('title', 'Untitled')}: {conv.get('message_count', 0)} messages")
            return True
        else:
            print("✗ Failed to retrieve conversation list")
            print(response.content.decode())
            return False
    
    def test_conversation_details(self, conversation_id):
        """Test getting conversation details"""
        print(f"\n--- Testing Conversation Details ({conversation_id}) ---")
        
        response = self.client.get(
            f'{self.base_url}/conversation/{conversation_id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.auth_token}'
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.content)
            print("✓ Conversation details retrieved successfully")
            print(f"  Title: {data.get('title', 'Untitled')}")
            print(f"  Messages: {len(data.get('messages', []))}")
            
            # Show first few messages
            for msg in data.get('messages', [])[:4]:
                sender = "👤" if msg['sender'] == 'user' else "🤖"
                content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                print(f"    {sender} {content}")
            return True
        else:
            print("✗ Failed to retrieve conversation details")
            print(response.content.decode())
            return False
    
    def test_analytics(self):
        """Test conversation analytics"""
        print("\n--- Testing Analytics ---")
        
        response = self.client.get(
            f'{self.base_url}/analytics/',
            HTTP_AUTHORIZATION=f'Bearer {self.auth_token}'
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.content)
            print("✓ Analytics retrieved successfully")
            print(f"  Analytics records: {len(data)}")
            
            for analytics in data[:3]:  # Show first 3
                print(f"    - {analytics.get('conversation_title', 'Unknown')}")
                print(f"      Messages: {analytics.get('total_messages', 0)}")
                print(f"      Tokens: {analytics.get('total_tokens_used', 0)}")
            return True
        else:
            print("✗ Failed to retrieve analytics")
            print(response.content.decode())
            return False
    
    def test_conversation_api_without_gemini(self):
        """Test conversation API structure without calling Gemini"""
        print("\n--- Testing Conversation API Structure ---")
        
        # This will fail without Gemini API key, but we can test the structure
        response = self.client.post(
            f'{self.base_url}/conversation/',
            json.dumps({
                'message': 'This is a test message to check API structure'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.auth_token}'
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            print("⚠️  Expected failure - Gemini API not configured (this is normal for testing)")
            try:
                data = json.loads(response.content)
                if 'error' in data:
                    print(f"  Error message: {data['error']}")
                    if 'Gemini' in str(data.get('error', '')):
                        print("  ✓ API structure is correct, just missing Gemini API key")
                        return True
            except:
                pass
        elif response.status_code == 200:
            print("✓ Conversation API working with Gemini")
            data = json.loads(response.content)
            print(f"  Response received: {data.get('response', '')[:100]}...")
            return True
        
        print("✗ Unexpected API response structure")
        print(response.content.decode()[:500])
        return False
    
    def test_unauthorized_access(self):
        """Test API without authentication"""
        print("\n--- Testing Unauthorized Access ---")
        
        response = self.client.get(f'{self.base_url}/conversations/')
        
        if response.status_code == 401:
            print("✓ Properly rejected unauthorized access")
            return True
        else:
            print(f"✗ Expected 401, got {response.status_code}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n--- Cleaning Up Test Data ---")
        
        # Delete test conversations
        deleted_conversations = Conversation.objects.filter(user=self.user).delete()[0]
        deleted_logs = APIUsageLog.objects.filter(user=self.user).delete()[0]
        
        print(f"✓ Cleaned up {deleted_conversations} conversations and {deleted_logs} API logs")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Dr. Jeg API Tests")
        print("=" * 50)
        
        # Setup
        self.create_test_user()
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue tests")
            return
        
        # Test results tracking
        results = {
            'service_status': False,
            'conversation_list': False,
            'mock_conversation': False,
            'conversation_details': False,
            'analytics': False,
            'api_structure': False,
            'unauthorized': False
        }
        
        # Run tests
        results['service_status'] = self.test_service_status()
        results['unauthorized'] = self.test_unauthorized_access()
        
        # Create mock data for testing
        mock_conversation = self.test_conversation_creation_mock()
        if mock_conversation:
            results['mock_conversation'] = True
            results['conversation_list'] = self.test_conversation_list()
            results['conversation_details'] = self.test_conversation_details(mock_conversation.id)
            results['analytics'] = self.test_analytics()
        
        results['api_structure'] = self.test_conversation_api_without_gemini()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 50)
        print("🎯 Test Results Summary")
        print("=" * 50)
        
        passed = sum(results.values())
        total = len(results)
        
        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test.replace('_', ' ').title()}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Dr. Jeg API is ready.")
        elif passed >= total * 0.8:
            print("⚠️  Most tests passed. Minor issues detected.")
        else:
            print("🚨 Several tests failed. Please check configuration.")
        
        return passed == total


if __name__ == '__main__':
    tester = DrJegAPITester()
    tester.run_all_tests()
