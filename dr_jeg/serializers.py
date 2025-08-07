from rest_framework import serializers
from .models import Conversation, Message, ConversationAnalytics, APIUsageLog


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'content', 'timestamp', 
            'ai_model', 'response_time_ms', 'tokens_used'
        ]
        read_only_fields = ['id', 'timestamp', 'ai_model', 'response_time_ms', 'tokens_used']


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing conversations (metadata only)
    """
    message_count = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'created_at', 'updated_at', 
            'message_count', 'last_message_time'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message_time(self, obj):
        last_message = obj.messages.last()
        return last_message.timestamp if last_message else obj.created_at


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed conversation with messages
    """
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'created_at', 'updated_at', 
            'messages', 'message_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new conversation with initial message
    """
    message = serializers.CharField(max_length=5000, help_text="Initial user message")
    conversation_id = serializers.UUIDField(required=False, help_text="Optional: continue existing conversation")
    
    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class ConversationResponseSerializer(serializers.Serializer):
    """
    Serializer for AI response
    """
    conversation_id = serializers.UUIDField()
    response = serializers.CharField()
    timestamp = serializers.DateTimeField()
    message_id = serializers.UUIDField()
    tokens_used = serializers.IntegerField(required=False)
    response_time_ms = serializers.IntegerField(required=False)


class ConversationAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for conversation analytics
    """
    conversation_title = serializers.CharField(source='conversation.title', read_only=True)
    
    class Meta:
        model = ConversationAnalytics
        fields = [
            'conversation_title', 'total_messages', 'total_user_messages',
            'total_bot_messages', 'total_tokens_used', 'average_response_time_ms',
            'health_topics', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class APIUsageLogSerializer(serializers.ModelSerializer):
    """
    Serializer for API usage logs (admin/monitoring)
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = APIUsageLog
        fields = [
            'id', 'user_email', 'endpoint_called', 'request_tokens',
            'response_tokens', 'total_tokens', 'response_time_ms',
            'success', 'error_message', 'status_code', 'estimated_cost',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class ConversationBulkDeleteSerializer(serializers.Serializer):
    """
    Serializer for bulk deleting conversations
    """
    confirm = serializers.BooleanField(help_text="Confirmation required for bulk delete")
    
    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("Confirmation is required to delete all conversations")
        return value
