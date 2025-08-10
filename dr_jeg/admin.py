from django.contrib import admin
from .models import Conversation, Message, ConversationAnalytics, APIUsageLog


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'content_preview', 'timestamp']
    list_filter = ['role', 'timestamp']
    search_fields = ['content', 'conversation__user__email']
    readonly_fields = ['id', 'timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(ConversationAnalytics)
class ConversationAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'total_messages', 'user_satisfaction', 'created_at']
    list_filter = ['user_satisfaction', 'created_at']
    readonly_fields = ['conversation', 'created_at', 'updated_at']


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'endpoint', 'request_count', 'tokens_used', 'cost', 'date']
    list_filter = ['endpoint', 'date']
    search_fields = ['user__email']
    readonly_fields = ['date']
