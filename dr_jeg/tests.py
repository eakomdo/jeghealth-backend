from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock

from .models import Conversation, Message, ConversationAnalytics, APIUsageLog
from .gemini_service import GeminiService

User = get_user_model()

class DrJegModelTests(TestCase):
    """Test Dr. JEG models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_conversation_creation(self):
        """Test conversation model creation"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
        
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.title, 'Test Conversation')
        self.assertTrue(conversation.is_active)
        self.assertIsNotNone(conversation.id)
    
    def test_message_creation(self):
        """Test message model creation"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
        
        message = Message.objects.create(
            conversation=conversation,
            role='user',
            content='Hello Dr. JEG'
        )
        
        self.assertEqual(message.conversation, conversation)
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, 'Hello Dr. JEG')
    
    def test_conversation_analytics(self):
        """Test conversation analytics model"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
        
        analytics = ConversationAnalytics.objects.create(
            conversation=conversation,
            total_messages=5,
            health_topics_discussed=['blood pressure', 'exercise'],
            user_satisfaction=4
        )
        
        self.assertEqual(analytics.conversation, conversation)
        self.assertEqual(analytics.total_messages, 5)
        self.assertIn('blood pressure', analytics.health_topics_discussed)

class DrJegAPITests(APITestCase):
    """Test Dr. JEG API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    @patch('dr_jeg.gemini_service.gemini_service.get_health_advice')
    def test_chat_endpoint(self, mock_get_advice):
        """Test chat endpoint"""
        # Mock AI response
        mock_get_advice.return_value = {
            'success': True,
            'advice': 'Drink plenty of water and get regular exercise.',
            'tokens_used': 50,
            'health_topics': ['hydration', 'exercise']
        }
        
        url = reverse('dr-jeg-chat')
        data = {
            'message': 'How can I stay healthy?'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('conversation_id', response.data)
        self.assertIn('message', response.data)
        
        # Check that conversation and messages were created
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Message.objects.count(), 2)  # User + AI message
    
    def test_chat_endpoint_no_message(self):
        """Test chat endpoint with no message"""
        url = reverse('dr-jeg-chat')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('dr_jeg.gemini_service.gemini_service.analyze_health_data')
    def test_health_analysis_endpoint(self, mock_analyze):
        """Test health analysis endpoint"""
        # Mock analysis response
        mock_analyze.return_value = {
            'success': True,
            'analysis': 'Your health metrics look good overall.',
            'insights': ['positive_indicators'],
            'recommendations': ['maintain_current_habits']
        }
        
        url = reverse('dr-jeg-analyze-health')
        data = {
            'health_metrics': {
                'blood_pressure': '120/80',
                'heart_rate': 72,
                'weight': 70
            },
            'analysis_type': 'general'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('analysis', response.data)
        self.assertIn('insights', response.data)
        self.assertIn('recommendations', response.data)
    
    def test_conversations_list(self):
        """Test getting conversation list"""
        # Create test conversations
        conversation1 = Conversation.objects.create(
            user=self.user,
            title='Health Chat 1'
        )
        conversation2 = Conversation.objects.create(
            user=self.user,
            title='Health Chat 2'
        )
        
        url = reverse('dr-jeg-conversations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_health_tips_endpoint(self):
        """Test health tips endpoint"""
        url = reverse('dr-jeg-health-tips')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tip', response.data)
        self.assertIn('category', response.data)

class GeminiServiceTests(TestCase):
    """Test Gemini AI service"""
    
    def setUp(self):
        self.service = GeminiService()
    
    @patch('google.generativeai.GenerativeModel')
    def test_get_health_advice_success(self, mock_model):
        """Test successful health advice generation"""
        # Mock the model and response
        mock_response = MagicMock()
        mock_response.text = "Stay hydrated and exercise regularly."
        
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        # Override the service model
        self.service.model = mock_model_instance
        
        result = self.service.get_health_advice("How to stay healthy?")
        
        self.assertTrue(result['success'])
        self.assertIn('advice', result)
        self.assertIn('health_topics', result)
    
    def test_extract_health_topics(self):
        """Test health topic extraction"""
        message = "I have high blood pressure and need exercise advice"
        topics = self.service._extract_health_topics(message)
        
        self.assertIn('blood pressure', topics)
        self.assertIn('exercise', topics)
    
    def test_extract_recommendations(self):
        """Test recommendation extraction"""
        analysis = "You should exercise more and improve your diet. Consider seeing a doctor."
        recommendations = self.service._extract_recommendations(analysis)
        
        self.assertIn('increase_physical_activity', recommendations)
        self.assertIn('improve_nutrition', recommendations)
        self.assertIn('consult_healthcare_provider', recommendations)
