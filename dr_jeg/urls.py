from django.urls import path
from . import views

urlpatterns = [
    # Main conversation endpoint
    path('conversation/', views.ConversationCreateView.as_view(), name='dr-jeg-chat'),
    
    # Conversation management
    path('conversations/', views.ConversationListView.as_view(), name='dr-jeg-conversations'),
    path('conversation/<uuid:conversation_id>/', views.ConversationDetailView.as_view(), name='dr-jeg-conversation-detail'),
    path('conversation/<uuid:conversation_id>/delete/', views.ConversationDeleteView.as_view(), name='dr-jeg-conversation-delete'),
    path('conversations/clear/', views.ConversationClearView.as_view(), name='dr-jeg-conversations-clear'),
    
    # Analytics and status
    path('analytics/', views.ConversationAnalyticsView.as_view(), name='dr-jeg-analytics'),
    path('status/', views.ServiceStatusView.as_view(), name='dr-jeg-status'),
]
