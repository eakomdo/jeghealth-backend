import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Conversation(models.Model):
    """
    Model to store Dr. Jeg conversations with users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dr_jeg_conversations')
    title = models.CharField(max_length=100, help_text="Auto-generated or user-editable title")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Soft delete flag")

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    def save(self, *args, **kwargs):
        # Auto-generate title from first message if not provided
        if not self.title and not self.pk:
            self.title = "New Conversation"
        super().save(*args, **kwargs)


class Message(models.Model):
    """
    Model to store individual messages in Dr. Jeg conversations
    """
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Dr. Jeg (AI)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField(help_text="Message content")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional metadata for AI responses
    ai_model = models.CharField(max_length=50, blank=True, help_text="AI model used (e.g., gemini-pro)")
    response_time_ms = models.PositiveIntegerField(null=True, blank=True, help_text="Response time in milliseconds")
    tokens_used = models.PositiveIntegerField(null=True, blank=True, help_text="Tokens consumed by AI")

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update conversation title if this is the first user message
        if self.sender == 'user' and self.conversation.title == "New Conversation":
            # Generate title from first 5 words of the message
            words = self.content.split()[:5]
            title = " ".join(words)
            if len(title) > 50:
                title = title[:47] + "..."
            self.conversation.title = title
            self.conversation.save()


class ConversationAnalytics(models.Model):
    """
    Model to store analytics data for Dr. Jeg conversations
    """
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='analytics')
    total_messages = models.PositiveIntegerField(default=0)
    total_user_messages = models.PositiveIntegerField(default=0)
    total_bot_messages = models.PositiveIntegerField(default=0)
    total_tokens_used = models.PositiveIntegerField(default=0)
    average_response_time_ms = models.FloatField(null=True, blank=True)
    
    # Health topics discussed (for insights)
    health_topics = models.JSONField(default=list, blank=True, help_text="List of health topics discussed")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.conversation.title}"

    def update_analytics(self):
        """Update analytics based on current messages"""
        messages = self.conversation.messages.all()
        self.total_messages = messages.count()
        self.total_user_messages = messages.filter(sender='user').count()
        self.total_bot_messages = messages.filter(sender='bot').count()
        
        bot_messages = messages.filter(sender='bot', tokens_used__isnull=False)
        if bot_messages.exists():
            self.total_tokens_used = sum(msg.tokens_used or 0 for msg in bot_messages)
            
        response_times = messages.filter(sender='bot', response_time_ms__isnull=False)
        if response_times.exists():
            self.average_response_time_ms = sum(msg.response_time_ms for msg in response_times) / response_times.count()
        
        self.save()


class APIUsageLog(models.Model):
    """
    Model to log Google Gemini API usage for monitoring and billing
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gemini_api_usage')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, blank=True)
    
    # API call details
    endpoint_called = models.CharField(max_length=100, default='gemini-pro')
    request_tokens = models.PositiveIntegerField(null=True, blank=True)
    response_tokens = models.PositiveIntegerField(null=True, blank=True)
    total_tokens = models.PositiveIntegerField(null=True, blank=True)
    
    # Response details
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    
    # Cost tracking (if applicable)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['success', '-timestamp']),
        ]

    def __str__(self):
        status = "Success" if self.success else f"Error ({self.status_code})"
        return f"{self.user.email} - {self.endpoint_called} - {status}"
