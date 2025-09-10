from rest_framework import generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import logging
import time
import json

from .models import Conversation, Message, ConversationAnalytics
from .serializers import (
    ConversationListSerializer, ConversationDetailSerializer,
    ConversationCreateSerializer, ConversationResponseSerializer,
    MessageSerializer, ConversationAnalyticsSerializer,
    ConversationBulkDeleteSerializer, HealthAnalysisRequestSerializer,
    ConversationSerializer  # Add this missing import
)
from .services import gemini_service

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class DrJegViewSet(ModelViewSet):
    """Basic ViewSet for Dr. Jeg conversations"""
    serializer_class = ConversationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

class ConversationCreateView(APIView):
    """Simple conversation creation view"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            message = request.data.get('message', '')
            conversation_id = request.data.get('conversation_id')
            
            if not message:
                return Response(
                    {'error': 'Message is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate AI response using Gemini service
            response_text, metadata = gemini_service.generate_response(
                user_message=message,
                user_id=str(request.user.id),
                conversation_history=[]  # For now, empty history
            )
            
            if metadata.get('success'):
                return Response({
                    'response': response_text,
                    'conversation_id': conversation_id,  # Would be generated if creating new conversation
                    'timestamp': timezone.now().isoformat(),
                    'tokens_used': metadata.get('tokens_used', 0),
                    'response_time_ms': metadata.get('response_time_ms', 0)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': metadata.get('error_message', 'AI service unavailable')
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except Exception as e:
            logger.error(f"Conversation creation error: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ConversationListView(generics.ListAPIView):
    """List all conversations for the authenticated user"""
    serializer_class = ConversationListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-updated_at')


class ConversationDetailView(generics.RetrieveAPIView):
    """Get detailed conversation with all messages"""
    serializer_class = ConversationDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'conversation_id'
    
    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user,
            is_active=True
        )


class ConversationDeleteView(APIView):
    """Delete a specific conversation"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, conversation_id):
        try:
            conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                user=request.user,
                is_active=True
            )
            conversation.is_active = False
            conversation.save()
            
            return Response({
                'status': 'success',
                'message': 'Conversation deleted successfully'
            })
        except Exception as e:
            logger.error(f"Conversation deletion error: {str(e)}")
            return Response(
                {'error': 'Failed to delete conversation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationClearView(APIView):
    """Clear all conversations for the user"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        try:
            confirm = request.data.get('confirm', False)
            if not confirm:
                return Response(
                    {'error': 'Confirmation required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            conversations = Conversation.objects.filter(
                user=request.user,
                is_active=True
            )
            count = conversations.count()
            conversations.update(is_active=False)
            
            return Response({
                'status': 'success',
                'message': f'All conversations cleared ({count} deleted)'
            })
        except Exception as e:
            logger.error(f"Conversation clear error: {str(e)}")
            return Response(
                {'error': 'Failed to clear conversations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationAnalyticsView(generics.ListAPIView):
    """Get conversation analytics for the user"""
    serializer_class = ConversationAnalyticsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ConversationAnalytics.objects.filter(
            conversation__user=self.request.user
        )


class ServiceStatusView(APIView):
    """Get Dr. Jeg service status and user statistics"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            conversations = Conversation.objects.filter(user=user, is_active=True)
            total_messages = Message.objects.filter(
                conversation__user=user,
                conversation__is_active=True
            ).count()
            
            return Response({
                'service_status': 'active',
                'user_statistics': {
                    'total_conversations': conversations.count(),
                    'total_messages': total_messages,
                    'recent_successful_calls': 0,  # Could implement tracking
                    'recent_failed_calls': 0,
                    'current_hourly_requests': 0,  # Could implement rate limiting tracking
                    'rate_limit': 60
                },
                'gemini_model': 'gemini-pro',
                'features': [
                    'health_focused_responses',
                    'conversation_history',
                    'safety_filtering',
                    'rate_limiting'
                ]
            })
        except Exception as e:
            logger.error(f"Service status error: {str(e)}")
            return Response(
                {'error': 'Failed to get service status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )