from django.contrib import admin
from .models import Conversation, Message, ConversationAnalytics, APIUsageLog


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'updated_at', 'is_active', 'message_count']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation_title', 'sender', 'content_preview', 'timestamp', 'ai_model', 'response_time_ms']
    list_filter = ['sender', 'ai_model', 'timestamp']
    search_fields = ['content', 'conversation__title', 'conversation__user__email']
    readonly_fields = ['id', 'timestamp']
    ordering = ['-timestamp']
    
    def conversation_title(self, obj):
        return obj.conversation.title
    conversation_title.short_description = 'Conversation'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(ConversationAnalytics)
class ConversationAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'conversation_title', 'total_messages', 'total_user_messages', 
        'total_bot_messages', 'total_tokens_used', 'average_response_time_ms'
    ]
    readonly_fields = [
        'conversation', 'total_messages', 'total_user_messages', 
        'total_bot_messages', 'created_at', 'updated_at'
    ]
    ordering = ['-updated_at']
    
    def conversation_title(self, obj):
        return obj.conversation.title
    conversation_title.short_description = 'Conversation'


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        'user_email', 'endpoint_called', 'success', 'response_time_ms', 
        'total_tokens', 'timestamp'
    ]
    list_filter = ['success', 'endpoint_called', 'timestamp']
    search_fields = ['user__email', 'error_message']
    readonly_fields = ['id', 'timestamp']
    ordering = ['-timestamp']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
