from rest_framework import serializers
from .models import Conversation, Message, ConversationAnalytics, APIUsageLog


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for AI conversation messages"""
    
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'timestamp', 'metadata']
        read_only_fields = ['id', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for AI conversations"""
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'messages', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new conversations"""
    initial_message = serializers.CharField(write_only=True)
    
    class Meta:
        model = Conversation
        fields = ['title', 'initial_message']
    
    def create(self, validated_data):
        initial_message = validated_data.pop('initial_message')
        user = self.context['request'].user
        
        # Create conversation
        conversation = Conversation.objects.create(
            user=user,
            title=validated_data.get('title', f"Conversation {initial_message[:30]}...")
        )
        
        # Create initial user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=initial_message
        )
        
        return conversation


class HealthAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for health data analysis requests"""
    health_metrics = serializers.JSONField()
    analysis_type = serializers.ChoiceField(
        choices=[
            ('general', 'General Analysis'),
            ('trends', 'Trend Analysis'),
            ('alerts', 'Alert Analysis'),
            ('recommendations', 'Recommendations')
        ],
        default='general'
    )
    include_recommendations = serializers.BooleanField(default=True)


class ConversationAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for conversation analytics"""
    
    class Meta:
        model = ConversationAnalytics
        fields = '__all__'
        read_only_fields = ['conversation', 'created_at', 'updated_at']


class APIUsageSerializer(serializers.ModelSerializer):
    """Serializer for API usage tracking"""
    
    class Meta:
        model = APIUsageLog
        fields = '__all__'
        read_only_fields = ['user', 'date']
