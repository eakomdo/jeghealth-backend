import logging
from django.utils import timezone
from django.db import transaction
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
import time
import json

from .models import Conversation, Message, ConversationAnalytics
from .serializers import (
    ConversationListSerializer, ConversationDetailSerializer,
    ConversationCreateSerializer, ConversationResponseSerializer,
    MessageSerializer, ConversationAnalyticsSerializer,
    ConversationBulkDeleteSerializer, HealthAnalysisRequestSerializer
)
from .services import gemini_service
from health_metrics.models import HealthMetric

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ConversationCreateView(APIView):
    """
    Create a new conversation or continue an existing one with Dr. Jeg AI
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Send message to Dr. Jeg AI",
        description="Send a message to Dr. Jeg AI and get a response. Can start new conversation or continue existing one.",
        request=ConversationCreateSerializer,
        responses={200: ConversationResponseSerializer},
        tags=["Dr. Jeg AI"],
        auth=['Bearer'],
        examples=[
            OpenApiExample(
                'New conversation',
                summary='Starting a new conversation',
                description='Send a message to start a new conversation with Dr. Jeg',
                value={
                    "message": "I've been having headaches lately. What could be causing them?"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Continue conversation',
                summary='Continue existing conversation',
                description='Continue an existing conversation by providing conversation_id',
                value={
                    "message": "The headaches happen mostly in the morning",
                    "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
                },
                request_only=True,
            )
        ]
    )
    def post(self, request):
        serializer = ConversationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        message = serializer.validated_data['message']
        conversation_id = serializer.validated_data.get('conversation_id')
        
        try:
            with transaction.atomic():
                # Get or create conversation
                if conversation_id:
                    try:
                        conversation = Conversation.objects.get(
                            id=conversation_id, 
                            user=user,
                            is_active=True
                        )
                    except Conversation.DoesNotExist:
                        return Response({
                            'error': 'Conversation not found or access denied'
                        }, status=status.HTTP_404_NOT_FOUND)
                else:
                    conversation = Conversation.objects.create(user=user)
                
                # Save user message
                user_message = Message.objects.create(
                    conversation=conversation,
                    sender='user',
                    content=message
                )
                
                # Get conversation history for context
                conversation_history = list(conversation.messages.values(
                    'sender', 'content', 'timestamp'
                ).order_by('timestamp'))
                
                # Generate AI response
                ai_response_text, metadata = gemini_service.generate_response(
                    message, 
                    str(user.id),
                    conversation_history[:-1]  # Exclude current message
                )
                
                # Log API usage
                api_log = APIUsageLog.objects.create(
                    user=user,
                    conversation=conversation,
                    endpoint_called='gemini-pro',
                    total_tokens=metadata.get('tokens_used'),
                    response_time_ms=metadata.get('response_time_ms'),
                    success=metadata.get('success', False),
                    error_message=metadata.get('error_message', ''),
                    status_code=metadata.get('status_code', 500)
                )
                
                if not metadata.get('success'):
                    return Response({
                        'error': metadata.get('error_message', 'Failed to generate AI response'),
                        'conversation_id': str(conversation.id)
                    }, status=metadata.get('status_code', 500))
                
                # Save AI response
                ai_message = Message.objects.create(
                    conversation=conversation,
                    sender='bot',
                    content=ai_response_text,
                    ai_model='gemini-pro',
                    response_time_ms=metadata.get('response_time_ms'),
                    tokens_used=metadata.get('tokens_used')
                )
                
                # Update conversation timestamp
                conversation.updated_at = timezone.now()
                conversation.save()
                
                # Update or create analytics
                analytics, created = ConversationAnalytics.objects.get_or_create(
                    conversation=conversation
                )
                analytics.update_analytics()
                
                # Prepare response
                response_data = {
                    'conversation_id': str(conversation.id),
                    'response': ai_response_text,
                    'timestamp': ai_message.timestamp,
                    'message_id': str(ai_message.id),
                    'tokens_used': metadata.get('tokens_used'),
                    'response_time_ms': metadata.get('response_time_ms')
                }
                
                logger.info(f"Dr. Jeg conversation response generated for user {user.id}")
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error in Dr. Jeg conversation: {str(e)}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationListView(generics.ListAPIView):
    """
    Get list of user's Dr. Jeg conversations
    """
    serializer_class = ConversationListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List user's conversations",
        description="Get a list of all Dr. Jeg conversations for the authenticated user.",
        tags=["Dr. Jeg AI"],
        auth=['Bearer'],
        parameters=[
            OpenApiParameter(
                name='limit',
                description='Number of conversations to return (default: 50)',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='offset',
                description='Number of conversations to skip',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user,
            is_active=True
        ).prefetch_related('messages')
    
    def get_paginated_response(self, data):
        # Limit to 50 conversations by default
        limit = min(int(self.request.query_params.get('limit', 50)), 100)
        offset = int(self.request.query_params.get('offset', 0))
        
        queryset = self.get_queryset()[offset:offset + limit]
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    def list(self, request, *args, **kwargs):
        return self.get_paginated_response(None)


class ConversationDetailView(generics.RetrieveAPIView):
    """
    Get full conversation history with Dr. Jeg
    """
    serializer_class = ConversationDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'conversation_id'
    
    @extend_schema(
        summary="Get conversation details",
        description="Retrieve full message history for a specific Dr. Jeg conversation.",
        tags=["Dr. Jeg AI"],
        auth=['Bearer']
    )
    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user,
            is_active=True
        ).prefetch_related('messages')


class ConversationDeleteView(generics.DestroyAPIView):
    """
    Delete a specific Dr. Jeg conversation
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'conversation_id'
    
    @extend_schema(
        summary="Delete conversation",
        description="Delete a specific Dr. Jeg conversation and all its messages.",
        tags=["Dr. Jeg AI"],
        auth=['Bearer']
    )
    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user,
            is_active=True
        )
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()
        
        logger.info(f"Dr. Jeg conversation {instance.id} deleted by user {self.request.user.id}")
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'status': 'success',
                'message': 'Conversation deleted successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to delete conversation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationBulkDeleteView(APIView):
    """
    Delete all Dr. Jeg conversations for a user
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Delete all conversations",
        description="Delete all Dr. Jeg conversations for the authenticated user.",
        request=ConversationBulkDeleteSerializer,
        tags=["Dr. Jeg AI"],
        auth=['Bearer'],
        examples=[
            OpenApiExample(
                'Confirm deletion',
                summary='Confirm bulk deletion',
                description='Confirmation required to delete all conversations',
                value={"confirm": True},
                request_only=True,
            )
        ]
    )
    def delete(self, request):
        serializer = ConversationBulkDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Soft delete all user's conversations
            deleted_count = Conversation.objects.filter(
                user=request.user,
                is_active=True
            ).update(is_active=False)
            
            logger.info(f"User {request.user.id} deleted {deleted_count} Dr. Jeg conversations")
            
            return Response({
                'status': 'success',
                'message': f'All conversations cleared ({deleted_count} deleted)'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in bulk delete: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to delete conversations'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationAnalyticsView(generics.ListAPIView):
    """
    Get analytics for user's Dr. Jeg conversations
    """
    serializer_class = ConversationAnalyticsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get conversation analytics",
        description="Get analytics data for the user's Dr. Jeg conversations.",
        tags=["Dr. Jeg AI"],
        auth=['Bearer']
    )
    def get_queryset(self):
        user_conversations = Conversation.objects.filter(
            user=self.request.user,
            is_active=True
        )
        return ConversationAnalytics.objects.filter(
            conversation__in=user_conversations
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Dr. Jeg API status",
    description="Check the status of Dr. Jeg AI service and user's usage statistics.",
    tags=["Dr. Jeg AI"],
    auth=['Bearer']
)
def dr_jeg_status(request):
    """
    Get Dr. Jeg service status and user statistics
    """
    try:
        user = request.user
        
        # Get user's conversation statistics
        total_conversations = Conversation.objects.filter(user=user, is_active=True).count()
        total_messages = Message.objects.filter(conversation__user=user, conversation__is_active=True).count()
        
        # Get recent API usage - careful with the slicing and filtering
        recent_logs = list(APIUsageLog.objects.filter(user=user).order_by('-timestamp')[:10])
        successful_calls = sum(1 for log in recent_logs if log.success)
        failed_calls = len(recent_logs) - successful_calls
        
        # Check rate limit status
        rate_limit_key = gemini_service.get_rate_limit_key(str(user.id))
        from django.core.cache import cache
        current_requests = cache.get(rate_limit_key, 0)
        
        # Get Gemini service status
        try:
            service_info = gemini_service.get_status()
            gemini_status = service_info.get('status', 'unknown')
        except Exception:
            gemini_status = 'error'
        
        return Response({
            'service_status': 'active',
            'gemini_service_status': gemini_status,
            'user_statistics': {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'recent_successful_calls': successful_calls,
                'recent_failed_calls': failed_calls,
                'current_hourly_requests': current_requests,
                'rate_limit': 60
            },
            'gemini_model': gemini_service.model_name,
            'features': [
                'health_focused_responses',
                'conversation_history',
                'safety_filtering',
                'rate_limiting'
            ]
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting Dr. Jeg status: {str(e)}")
        return Response({
            'service_status': 'error',
            'error': 'Unable to retrieve status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DrJegViewSet(viewsets.ViewSet):
    """Dr. JEG AI Assistant API endpoints"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """Start or continue a chat with Dr. JEG"""
        try:
            message = request.data.get('message', '').strip()
            conversation_id = request.data.get('conversation_id')
            
            if not message:
                return Response(
                    {'error': 'Message is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create conversation
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(
                        id=conversation_id,
                        user=request.user,
                        is_active=True
                    )
                except Conversation.DoesNotExist:
                    return Response(
                        {'error': 'Conversation not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Create new conversation
                conversation = Conversation.objects.create(
                    user=request.user,
                    title=f"Chat: {message[:30]}..."
                )
            
            # Save user message
            user_message = Message.objects.create(
                conversation=conversation,
                role='user',
                content=message
            )
            
            # Get user's health context
            health_context = self._get_user_health_context(request.user)
            
            # Get AI response
            ai_response = gemini_service.get_health_advice(message, health_context)
            
            if ai_response['success']:
                # Save AI response
                ai_message = Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=ai_response['advice'],
                    metadata={
                        'tokens_used': ai_response.get('tokens_used', 0),
                        'health_topics': ai_response.get('health_topics', [])
                    }
                )
                
                # Update analytics
                self._update_conversation_analytics(conversation, ai_response)
                
                # Log API usage
                self._log_api_usage(request.user, 'chat', ai_response.get('tokens_used', 0))
                
                return Response({
                    'success': True,
                    'conversation_id': str(conversation.id),
                    'message': {
                        'id': str(ai_message.id),
                        'content': ai_message.content,
                        'timestamp': ai_message.timestamp
                    },
                    'health_topics': ai_response.get('health_topics', [])
                })
            else:
                return Response({
                    'success': False,
                    'error': ai_response['message'],
                    'fallback_advice': ai_response['advice']
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return Response(
                {'error': 'Service temporarily unavailable'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def analyze_health(self, request):
        """Analyze user's health data"""
        try:
            serializer = HealthAnalysisRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            health_metrics = serializer.validated_data['health_metrics']
            analysis_type = serializer.validated_data['analysis_type']
            
            # Get AI analysis
            analysis_result = gemini_service.analyze_health_data(health_metrics)
            
            if analysis_result['success']:
                # Create conversation for this analysis
                conversation = Conversation.objects.create(
                    user=request.user,
                    title=f"Health Analysis - {analysis_type.title()}"
                )
                
                # Save analysis request as user message
                Message.objects.create(
                    conversation=conversation,
                    role='user',
                    content=f"Health Analysis Request: {analysis_type}",
                    metadata={'health_metrics': health_metrics}
                )
                
                # Save analysis result as AI message
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=analysis_result['analysis'],
                    metadata={
                        'analysis_type': analysis_type,
                        'insights': analysis_result.get('insights', []),
                        'recommendations': analysis_result.get('recommendations', [])
                    }
                )
                
                # Log API usage
                self._log_api_usage(request.user, 'health_analysis', 100)  # Estimate tokens
                
                return Response({
                    'success': True,
                    'conversation_id': str(conversation.id),
                    'analysis': analysis_result['analysis'],
                    'insights': analysis_result.get('insights', []),
                    'recommendations': analysis_result.get('recommendations', [])
                })
            else:
                return Response({
                    'success': False,
                    'error': analysis_result['message']
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            logger.error(f"Health analysis error: {str(e)}")
            return Response(
                {'error': 'Analysis service temporarily unavailable'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Get user's conversation history"""
        try:
            conversations = Conversation.objects.filter(
                user=request.user,
                is_active=True
            ).order_by('-updated_at')
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(conversations, request)
            
            if page is not None:
                serializer = ConversationSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = ConversationSerializer(conversations, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Conversation history error: {str(e)}")
            return Response(
                {'error': 'Unable to retrieve conversations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def conversation_detail(self, request, pk=None):
        """Get detailed conversation with all messages"""
        try:
            conversation = get_object_or_404(
                Conversation,
                id=pk,
                user=request.user,
                is_active=True
            )
            
            serializer = ConversationSerializer(conversation)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Conversation detail error: {str(e)}")
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def delete_conversation(self, request, pk=None):
        """Delete (deactivate) a conversation"""
        try:
            conversation = get_object_or_404(
                Conversation,
                id=pk,
                user=request.user
            )
            
            conversation.is_active = False
            conversation.save()
            
            return Response({'success': True, 'message': 'Conversation deleted'})
            
        except Exception as e:
            logger.error(f"Delete conversation error: {str(e)}")
            return Response(
                {'error': 'Unable to delete conversation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def health_tips(self, request):
        """Get daily health tips"""
        tips = [
            "Stay hydrated by drinking at least 8 glasses of water daily.",
            "Aim for 30 minutes of moderate exercise most days of the week.",
            "Eat a variety of colorful fruits and vegetables for optimal nutrition.",
            "Prioritize 7-9 hours of quality sleep each night.",
            "Practice stress management through meditation or deep breathing.",
            "Schedule regular check-ups with your healthcare provider.",
            "Limit processed foods and choose whole grains when possible.",
            "Take breaks from screens to protect your eye health.",
            "Maintain good posture to prevent back and neck problems.",
            "Practice good hand hygiene to prevent illness."
        ]
        
        import random
        daily_tip = random.choice(tips)
        
        return Response({
            'tip': daily_tip,
            'date': request.data.get('date', 'today'),
            'category': 'general_wellness'
        })
    
    def _get_user_health_context(self, user):
        """Get user's health context for AI"""
        try:
            # Get recent health metrics
            recent_metrics = HealthMetric.objects.filter(
                user=user
            ).order_by('-recorded_at')[:10]
            
            context = {
                'user_id': str(user.id),
                'recent_metrics': []
            }
            
            for metric in recent_metrics:
                context['recent_metrics'].append({
                    'metric_type': metric.metric_type,
                    'recorded_at': metric.recorded_at.isoformat()
                })
            return context
        except Exception as e:
            logger.error(f"Health context error: {str(e)}")
            return {}
    def _update_conversation_analytics(self, conversation, ai_response):
        """Update conversation analytics"""
        try:
            analytics, created = ConversationAnalytics.objects.get_or_create(
                conversation=conversation,
                defaults={
                    'total_messages': 0,
                    'health_topics_discussed': [],
                    'recommendations_given': []
                }
            )
            analytics.total_messages += 2  # User + AI message
            # Add health topics
            health_topics = ai_response.get('health_topics', [])
            for topic in health_topics:
                if topic not in analytics.health_topics_discussed:
                    analytics.health_topics_discussed.append(topic)
            analytics.save()
        except Exception as e:
            logger.error(f"Analytics update error: {str(e)}")
    def _log_api_usage(self, user, endpoint, tokens_used=0):
        """Log API usage for analytics"""
        try:
            usage, created = APIUsageLog.objects.get_or_create(
                user=user,
                endpoint=endpoint,
                date=timezone.now().date(),
                defaults={
                    'request_count': 0,
                    'tokens_used': 0,
                    'cost': 0.0
                }
            )
            usage.request_count += 1
            usage.tokens_used += tokens_used
            # Simple cost calculation (adjust based on actual pricing)
            usage.cost += tokens_used * 0.0001
            usage.save()
        except Exception as e:
            logger.error(f"Usage logging error: {str(e)}")

    def _get_health_context(self, user):
        """Get user's health context for AI"""
        try:
            # Get recent health metrics for context
            recent_metrics = HealthMetric.objects.filter(
                user=user
            ).order_by('-recorded_at')[:5]
            
            context = {
                'user_id': str(user.id),
                'recent_metrics': []
            }
            
            for metric in recent_metrics:
                context['recent_metrics'].append({
                    'metric_type': metric.metric_type,
                    'recorded_at': metric.recorded_at.isoformat()
                })
            return context
        except Exception as e:
            logger.error(f"Health context error: {str(e)}")
            return {}

    def _update_conversation_analytics(self, conversation, ai_response):
        """Update conversation analytics"""
        try:
            # Implementation for updating analytics
            pass
        except Exception as e:
            logger.error(f"Analytics update error: {str(e)}")
