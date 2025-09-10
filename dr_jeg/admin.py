from django.contrib import admin
from .models import Conversation, Message, ConversationAnalytics, APIUsageLog


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'content_preview', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['content', 'conversation__title']
    readonly_fields = ['id', 'timestamp']
    raw_id_fields = ['conversation']
    
    def content_preview(self, obj):
        """Show first 50 characters of content"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(ConversationAnalytics)
class ConversationAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['conversation__title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['conversation']


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'endpoint_called', 'total_tokens', 
        'success', 'estimated_cost', 'response_time_ms'
    ]
    list_filter = ['success', 'endpoint_called']
    search_fields = ['user__email', 'user__username', 'error_message']
    readonly_fields = ['id']
    raw_id_fields = ['user', 'conversation']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'conversation')
