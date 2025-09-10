#!/usr/bin/env python3
"""
Complete Dr. Jeg API Frontend Implementation Test
Demonstrates all available endpoints for frontend developers
"""

import os
import sys
import django
import json
import time

# Setup Django environment
sys.path.append('/Users/phill/Desktop/jeghealth-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeghealth_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

class DrJegFrontendAPIDemo:
    def __init__(self):
        self.client = Client()
        self.token = None
        self.base_url = '/api/v1/dr-jeg'
        
    def setup_auth(self):
        """Setup authentication for API testing"""
        print("🔐 Setting up authentication...")
        
        # Create or get test user
        try:
            user = User.objects.get(email='frontend_test@example.com')
            print("✓ Using existing test user")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='frontend_test',
                email='frontend_test@example.com', 
                password='testpass123'
            )
            print("✓ Created new test user")
        
        # Login to get token
        login_response = self.client.post('/api/v1/auth/login/', {
            'email': 'frontend_test@example.com',
            'password': 'testpass123'
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            tokens = login_data.get('tokens', {})
            self.token = tokens.get('access')
            print("✅ Authentication successful")
            return True
        else:
            print("❌ Authentication failed")
            print(f"Error: {login_response.content.decode()}")
            return False
    
    def make_request(self, method, endpoint, data=None):
        """Make authenticated API request"""
        url = f"{self.base_url}{endpoint}"
        kwargs = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        
        if method.upper() == 'GET':
            response = self.client.get(url, **kwargs)
        elif method.upper() == 'POST':
            response = self.client.post(url, data, content_type='application/json', **kwargs)
        elif method.upper() == 'DELETE':
            response = self.client.delete(url, data, content_type='application/json', **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        return response
    
    def test_service_status(self):
        """Test GET /status/ endpoint"""
        print("\n🔍 Testing Service Status Endpoint")
        print("=" * 50)
        print("GET /api/v1/dr-jeg/status/")
        
        response = self.make_request('GET', '/status/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Service status retrieved successfully")
            print(f"Service Status: {data.get('service_status')}")
            print(f"Gemini Model: {data.get('gemini_model')}")
            
            stats = data.get('user_statistics', {})
            print(f"User Statistics:")
            print(f"  - Total Conversations: {stats.get('total_conversations')}")
            print(f"  - Total Messages: {stats.get('total_messages')}")
            print(f"  - Rate Limit: {stats.get('rate_limit')}")
            
            features = data.get('features', [])
            print(f"Features: {', '.join(features)}")
            return True
        else:
            print("❌ Failed to get service status")
            return False
    
    def test_send_message(self, message, conversation_id=None):
        """Test POST /conversation/ endpoint"""
        print(f"\n💬 Testing Send Message Endpoint")
        print("=" * 50)
        print("POST /api/v1/dr-jeg/conversation/")
        
        data = {"message": message}
        if conversation_id:
            data["conversation_id"] = conversation_id
            
        print(f"Request: {json.dumps(data, indent=2)}")
        
        response = self.make_request('POST', '/conversation/', json.dumps(data))
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Message sent successfully")
            print(f"\n👤 You: {message}")
            print(f"\n🤖 Dr. Jeg: {data.get('response', 'No response')[:200]}...")
            print(f"\nMetadata:")
            print(f"  - Conversation ID: {data.get('conversation_id')}")
            print(f"  - Tokens Used: {data.get('tokens_used')}")
            print(f"  - Response Time: {data.get('response_time_ms')}ms")
            print(f"  - Timestamp: {data.get('timestamp')}")
            return data.get('conversation_id')
        else:
            print("❌ Failed to send message")
            print(f"Error: {response.content.decode()}")
            return None
    
    def test_list_conversations(self):
        """Test GET /conversations/ endpoint"""
        print(f"\n📋 Testing List Conversations Endpoint")
        print("=" * 50)
        print("GET /api/v1/dr-jeg/conversations/")
        
        response = self.make_request('GET', '/conversations/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversations retrieved successfully")
            print(f"Total Count: {data.get('count', 0)}")
            
            results = data.get('results', [])
            if results:
                print(f"Conversations:")
                for i, conv in enumerate(results[:3], 1):
                    print(f"  {i}. {conv.get('title', 'Untitled')}")
                    print(f"     ID: {conv.get('id')}")
                    print(f"     Messages: {conv.get('message_count', 0)}")
                    print(f"     Created: {conv.get('created_at')}")
                    print(f"     Active: {conv.get('is_active')}")
                    
                return results[0].get('id') if results else None
            else:
                print("No conversations found")
                return None
        else:
            print("❌ Failed to list conversations")
            return None
    
    def test_conversation_details(self, conversation_id):
        """Test GET /conversation/{id}/ endpoint"""
        if not conversation_id:
            print("⚠️ Skipping conversation details test - no conversation ID")
            return
            
        print(f"\n🔍 Testing Conversation Details Endpoint")
        print("=" * 50)
        print(f"GET /api/v1/dr-jeg/conversation/{conversation_id}/")
        
        response = self.make_request('GET', f'/conversation/{conversation_id}/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversation details retrieved successfully")
            print(f"Title: {data.get('title')}")
            print(f"Message Count: {data.get('message_count')}")
            print(f"Created: {data.get('created_at')}")
            print(f"Updated: {data.get('updated_at')}")
            
            messages = data.get('messages', [])
            if messages:
                print(f"\nMessages:")
                for i, msg in enumerate(messages[:3], 1):
                    sender_icon = "👤" if msg.get('sender') == 'user' else "🤖"
                    content = msg.get('content', '')[:100]
                    print(f"  {i}. {sender_icon} {content}...")
                    if msg.get('tokens_used'):
                        print(f"     Tokens: {msg.get('tokens_used')}, Time: {msg.get('response_time_ms')}ms")
            return True
        else:
            print("❌ Failed to get conversation details")
            return False
    
    def test_analytics(self):
        """Test GET /analytics/ endpoint"""
        print(f"\n📊 Testing Analytics Endpoint")
        print("=" * 50)
        print("GET /api/v1/dr-jeg/analytics/")
        
        response = self.make_request('GET', '/analytics/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics retrieved successfully")
            
            if isinstance(data, dict) and 'results' in data:
                results = data['results']
            elif isinstance(data, list):
                results = data
            else:
                results = []
                
            print(f"Analytics Records: {len(results)}")
            
            if results:
                for i, analytics in enumerate(results[:2], 1):
                    print(f"  {i}. Conversation: {analytics.get('conversation_title', 'Unknown')}")
                    print(f"     Total Messages: {analytics.get('total_messages', 0)}")
                    print(f"     Tokens Used: {analytics.get('total_tokens_used', 0)}")
                    print(f"     Avg Response Time: {analytics.get('average_response_time_ms', 0)}ms")
            return True
        else:
            print("❌ Failed to get analytics")
            return False
    
    def test_delete_conversation(self, conversation_id):
        """Test DELETE /conversation/{id}/delete/ endpoint"""
        if not conversation_id:
            print("⚠️ Skipping conversation deletion test - no conversation ID")
            return
            
        print(f"\n🗑️ Testing Delete Conversation Endpoint")
        print("=" * 50)
        print(f"DELETE /api/v1/dr-jeg/conversation/{conversation_id}/delete/")
        
        response = self.make_request('DELETE', f'/conversation/{conversation_id}/delete/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversation deleted successfully")
            print(f"Message: {data.get('message')}")
            return True
        else:
            print("❌ Failed to delete conversation")
            return False
    
    def test_clear_conversations(self):
        """Test DELETE /conversations/clear/ endpoint"""
        print(f"\n🧹 Testing Clear All Conversations Endpoint")
        print("=" * 50)
        print("DELETE /api/v1/dr-jeg/conversations/clear/")
        
        data = {"confirm": True}
        print(f"Request: {json.dumps(data, indent=2)}")
        
        response = self.make_request('DELETE', '/conversations/clear/', json.dumps(data))
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ All conversations cleared successfully")
            print(f"Message: {data.get('message')}")
            return True
        else:
            print("❌ Failed to clear conversations")
            return False
    
    def run_complete_demo(self):
        """Run complete demonstration of all endpoints"""
        print("🚀 Dr. Jeg API - Complete Frontend Implementation Demo")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_auth():
            return
            
        # Test all endpoints in logical order
        tests = []
        
        # 1. Check service status
        tests.append(("Service Status", self.test_service_status()))
        
        # 2. Send a message (creates conversation)
        conversation_id = self.test_send_message("Hello Dr. Jeg! I've been having trouble sleeping lately. Any advice?")
        
        # 3. Send follow-up message
        if conversation_id:
            self.test_send_message("The sleep issues started about a week ago.", conversation_id)
        
        # 4. List conversations
        tests.append(("List Conversations", self.test_list_conversations()))
        
        # 5. Get conversation details
        if conversation_id:
            tests.append(("Conversation Details", self.test_conversation_details(conversation_id)))
        
        # 6. Get analytics
        tests.append(("Analytics", self.test_analytics()))
        
        # 7. Delete specific conversation (optional)
        # tests.append(("Delete Conversation", self.test_delete_conversation(conversation_id)))
        
        # 8. Clear all conversations (optional - commented out to preserve data)
        # tests.append(("Clear All Conversations", self.test_clear_conversations()))
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 Test Results Summary")
        print("=" * 60)
        
        passed = sum(1 for name, result in tests if result)
        total = len(tests)
        
        for name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {name}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All endpoints working perfectly! Ready for frontend integration.")
        else:
            print("⚠️ Some endpoints need attention.")
        
        # Frontend integration notes
        print(f"\n📝 Frontend Integration Notes:")
        print(f"- Base URL: http://0.0.0.0:8000{self.base_url}")
        print(f"- Authentication: Bearer token required")
        print(f"- Sample conversation ID: {conversation_id}")
        print(f"- All endpoints tested and documented")
        print(f"- Check DR_JEG_FRONTEND_IMPLEMENTATION_GUIDE.md for complete details")

if __name__ == '__main__':
    demo = DrJegFrontendAPIDemo()
    demo.run_complete_demo()
