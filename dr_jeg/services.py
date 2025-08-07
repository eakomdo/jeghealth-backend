import os
import time
import logging
import requests
from typing import Dict, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
import json

logger = logging.getLogger(__name__)


class GeminiAPIService:
    """
    Service class for Google Gemini API integration using OpenAI-compatible endpoint
    """
    
    def __init__(self):
        self._initialized = False
        self.api_key = None
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
        self.model_name = "gemini-2.0-flash"
        
    def _initialize(self):
        """Lazy initialization of Gemini API"""
        if self._initialized:
            return
            
        self.api_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', os.getenv('GOOGLE_GEMINI_API_KEY'))
        if not self.api_key:
            raise ValueError("Google Gemini API key is not configured")
        
        # Healthcare context system message
        self.system_message = {
            "role": "system",
            "content": """You are Dr. Jeg, a knowledgeable and empathetic AI health assistant. 

Your role is to:
- Provide helpful health information and general wellness advice
- Listen empathetically to health concerns
- Suggest when users should consult healthcare professionals
- Offer lifestyle and wellness recommendations
- Answer health-related questions with accurate information

Important guidelines:
- Always emphasize that you cannot replace professional medical diagnosis or treatment
- Suggest consulting healthcare providers for serious symptoms or concerns
- Be supportive and understanding
- Provide evidence-based information when possible
- Respect privacy and confidentiality
- Do not provide specific medication dosages or prescriptions

Remember: You are a supportive health companion, not a replacement for professional medical care."""
        }
        
        self._initialized = True

    def get_rate_limit_key(self, user_id: str) -> str:
        """Generate cache key for rate limiting"""
        return f"gemini_api_rate_limit:{user_id}"
    
    def check_rate_limit(self, user_id: str, limit_per_hour: int = 60) -> bool:
        """
        Check if user has exceeded rate limit
        Returns True if within limit, False if exceeded
        """
        cache_key = self.get_rate_limit_key(user_id)
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= limit_per_hour:
            return False
        
        # Increment counter with 1-hour expiry
        cache.set(cache_key, current_requests + 1, 3600)
        return True
    
    def build_messages(self, user_message: str, conversation_history: list = None) -> list:
        """
        Build messages array for OpenAI-compatible API
        """
        messages = [self.system_message]
        
        # Add conversation context if available
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role = "user" if msg['sender'] == 'user' else "assistant"
                messages.append({
                    "role": role,
                    "content": msg['content']
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def generate_response(self, user_message: str, user_id: str, conversation_history: list = None) -> Tuple[str, Dict]:
        """
        Generate AI response using Google Gemini API (OpenAI-compatible)
        
        Returns:
            Tuple[str, Dict]: (response_text, metadata)
        """
        self._initialize()  # Ensure API is initialized
        
        start_time = time.time()
        metadata = {
            'success': False,
            'response_time_ms': 0,
            'tokens_used': 0,
            'error_message': '',
            'status_code': 200
        }
        
        try:
            # Check rate limiting
            if not self.check_rate_limit(user_id):
                metadata['error_message'] = 'Rate limit exceeded. Please try again later.'
                metadata['status_code'] = 429
                return "", metadata
            
            # Build messages for the API
            messages = self.build_messages(user_message, conversation_history)
            
            # Prepare API request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            payload = {
                'model': self.model_name,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 2048,
                'top_p': 0.8
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            metadata['response_time_ms'] = round(response_time, 2)
            metadata['status_code'] = response.status_code
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract response text
                if 'choices' in response_data and response_data['choices']:
                    response_text = response_data['choices'][0]['message']['content']
                    
                    # Extract token usage if available
                    if 'usage' in response_data:
                        metadata['tokens_used'] = response_data['usage'].get('total_tokens', 0)
                    
                    metadata['success'] = True
                    
                    logger.info(f"Gemini API response generated successfully for user {user_id}")
                    return response_text, metadata
                else:
                    metadata['error_message'] = 'No response generated'
                    logger.error(f"No response in API response: {response_data}")
                    return "", metadata
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_message = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                metadata['error_message'] = error_message
                
                logger.error(f"Gemini API error: {response.status_code} - {error_message}")
                return "", metadata
                
        except requests.exceptions.Timeout:
            metadata['error_message'] = 'Request timeout'
            metadata['status_code'] = 408
            logger.error(f"Gemini API timeout for user {user_id}")
            return "", metadata
            
        except requests.exceptions.ConnectionError:
            metadata['error_message'] = 'Connection error'
            metadata['status_code'] = 503
            logger.error(f"Gemini API connection error for user {user_id}")
            return "", metadata
            
        except ValueError as e:
            # Handle initialization errors (missing API key)
            metadata['error_message'] = str(e)
            metadata['status_code'] = 500
            logger.error(f"Gemini API configuration error: {str(e)}")
            return "", metadata
            
        except Exception as e:
            metadata['error_message'] = f'Unexpected error: {str(e)}'
            metadata['status_code'] = 500
            logger.error(f"Unexpected error in Gemini API: {str(e)}")
            return "", metadata
    
    def get_conversation_summary(self, messages: list) -> str:
        """
        Generate a summary of the conversation for analytics
        """
        if not messages:
            return ""
        
        try:
            self._initialize()  # Ensure API is initialized
            # Create summary prompt
            conversation_text = "\n".join([
                f"{'Patient' if msg['sender'] == 'user' else 'Dr. Jeg'}: {msg['content']}"
                for msg in messages[-10:]  # Last 10 messages
            ])
            
            summary_prompt = f"""Please provide a brief summary of the main health topics discussed in this conversation:

{conversation_text}

Summary (key topics only):"""
            
            response = self.model.generate_content(
                summary_prompt,
                generation_config={'max_output_tokens': 100, 'temperature': 0.3}
            )
            
            return response.text.strip() if response.text else ""
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return ""
    
    def extract_health_topics(self, conversation_text: str) -> list:
        """
        Extract health topics from conversation for categorization (simplified for new API)
        """
        try:
            # Simple keyword extraction for now
            health_keywords = [
                'fatigue', 'tired', 'headache', 'pain', 'fever', 'cough', 'sleep',
                'stress', 'anxiety', 'depression', 'diet', 'nutrition', 'exercise',
                'weight', 'blood pressure', 'diabetes', 'heart', 'medicine'
            ]
            
            topics = []
            text_lower = conversation_text.lower()
            
            for keyword in health_keywords:
                if keyword in text_lower and keyword not in topics:
                    topics.append(keyword)
                    
            return topics[:5]  # Max 5 topics
            
        except Exception as e:
            logger.error(f"Error extracting health topics: {e}")
            return []

    def get_status(self) -> Dict:
        """
        Get service status
        """
        try:
            self._initialize()
            
            # Test API connectivity with a simple request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            payload = {
                'model': self.model_name,
                'messages': [
                    {"role": "user", "content": "Hello"}
                ],
                'max_tokens': 10
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'model': self.model_name,
                    'api_endpoint': self.base_url,
                    'last_check': time.time()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'HTTP {response.status_code}',
                    'model': self.model_name,
                    'api_endpoint': self.base_url,
                    'last_check': time.time()
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'model': self.model_name if hasattr(self, 'model_name') else 'unknown',
                'api_endpoint': self.base_url if hasattr(self, 'base_url') else 'unknown',
                'last_check': time.time()
            }


# Singleton instance
gemini_service = GeminiAPIService()
