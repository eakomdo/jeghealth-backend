import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """Google Gemini AI service for health assistance"""
    
    def __init__(self):
        # Configure Gemini API with the key from settings
        if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            # Use the updated model name for current Gemini API
            model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Gemini AI service initialized successfully with model: {model_name}")
        else:
            self.model = None
            logger.warning("Google API key not configured")
    
    def get_health_advice(self, user_message, health_context=None):
        """Get health advice from AI"""
        if not self.model:
            return {
                'success': False,
                'message': 'AI service not configured',
                'advice': 'Please contact a healthcare provider for medical advice.'
            }
        
        try:
            # Build context-aware prompt
            system_prompt = self._build_health_prompt(health_context)
            full_prompt = f"{system_prompt}\n\nUser Question: {user_message}"
            
            # Configure generation parameters for more reliable responses
            generation_config = genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=1000,
                temperature=0.7,
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return {
                'success': True,
                'advice': response.text,
                'tokens_used': len(response.text.split()) if response.text else 0,
                'health_topics': self._extract_health_topics(user_message)
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return {
                'success': False,
                'message': 'AI service temporarily unavailable',
                'advice': 'Please try again later or contact a healthcare provider.'
            }
    
    def analyze_health_data(self, health_metrics):
        """Analyze health data and provide insights"""
        if not self.model:
            return {'success': False, 'message': 'AI service not configured'}
        
        try:
            analysis_prompt = self._build_analysis_prompt(health_metrics)
            
            generation_config = genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=800,
                temperature=0.6,
            )
            
            response = self.model.generate_content(
                analysis_prompt,
                generation_config=generation_config
            )
            
            return {
                'success': True,
                'analysis': response.text,
                'insights': self._extract_insights(response.text),
                'recommendations': self._extract_recommendations(response.text)
            }
            
        except Exception as e:
            logger.error(f"Health analysis error: {str(e)}")
            return {
                'success': False,
                'message': 'Analysis service temporarily unavailable'
            }
    
    def _build_health_prompt(self, health_context):
        """Build system prompt for health assistance"""
        base_prompt = """You are Dr. JEG, a helpful AI health assistant. You provide general health information and wellness advice.

IMPORTANT DISCLAIMERS:
- You are NOT a replacement for professional medical care
- Always recommend consulting healthcare providers for medical concerns
- Do not diagnose conditions or prescribe medications
- Provide general health information and wellness tips
- Encourage healthy lifestyle choices

Guidelines:
- Be empathetic and supportive
- Provide evidence-based health information
- Suggest when to seek professional medical help
- Focus on preventive care and wellness
- Use simple, understandable language"""

        if health_context:
            context_text = f"\n\nUser's Health Context:\n{json.dumps(health_context, indent=2)}"
            return base_prompt + context_text
        
        return base_prompt
    
    def _build_analysis_prompt(self, health_metrics):
        """Build prompt for health data analysis"""
        return f"""As Dr. JEG, analyze this health data and provide insights:

Health Metrics:
{json.dumps(health_metrics, indent=2)}

Please provide:
1. Overall health trends
2. Areas of concern (if any)
3. Positive health indicators
4. General wellness recommendations
5. When to consult a healthcare provider

Keep analysis general and educational. Always recommend professional medical consultation for specific health concerns."""
    
    def _extract_health_topics(self, message):
        """Extract health topics from user message"""
        health_keywords = [
            'blood pressure', 'heart rate', 'weight', 'diabetes', 'exercise',
            'sleep', 'stress', 'nutrition', 'medication', 'symptoms',
            'pain', 'fever', 'fatigue', 'diet', 'mental health'
        ]
        
        topics = []
        message_lower = message.lower()
        for keyword in health_keywords:
            if keyword in message_lower:
                topics.append(keyword)
        
        return topics
    
    def _extract_insights(self, analysis_text):
        """Extract key insights from analysis"""
        insights = []
        if analysis_text:
            analysis_lower = analysis_text.lower()
            if 'improve' in analysis_lower:
                insights.append('improvement_needed')
            if 'good' in analysis_lower or 'healthy' in analysis_lower:
                insights.append('positive_indicators')
            if 'concern' in analysis_lower or 'warning' in analysis_lower:
                insights.append('areas_of_concern')
        
        return insights
    
    def _extract_recommendations(self, analysis_text):
        """Extract recommendations from analysis"""
        recommendations = []
        if analysis_text:
            analysis_lower = analysis_text.lower()
            if 'exercise' in analysis_lower:
                recommendations.append('increase_physical_activity')
            if 'diet' in analysis_lower or 'nutrition' in analysis_lower:
                recommendations.append('improve_nutrition')
            if 'sleep' in analysis_lower:
                recommendations.append('better_sleep_hygiene')
            if 'doctor' in analysis_lower or 'healthcare' in analysis_lower:
                recommendations.append('consult_healthcare_provider')
        
        return recommendations

# Singleton instance
gemini_service = GeminiService()