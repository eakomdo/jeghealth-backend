from django.urls import path, re_path
from . import views

app_name = 'dr_jeg'

urlpatterns = [
    # Dr. Jeg conversation endpoints
    re_path(r'^conversation/?$', views.ConversationCreateView.as_view(), name='conversation_create'),
    re_path(r'^conversations/?$', views.ConversationListView.as_view(), name='conversations_list'),
    re_path(r'^conversation/(?P<conversation_id>[0-9a-f-]{36})/?$', views.ConversationDetailView.as_view(), name='conversation_detail'),
    re_path(r'^conversation/(?P<conversation_id>[0-9a-f-]{36})/delete/?$', views.ConversationDeleteView.as_view(), name='conversation_delete'),
    re_path(r'^conversations/clear/?$', views.ConversationBulkDeleteView.as_view(), name='conversations_bulk_delete'),
    
    # Analytics and status
    re_path(r'^analytics/?$', views.ConversationAnalyticsView.as_view(), name='conversation_analytics'),
    re_path(r'^status/?$', views.dr_jeg_status, name='dr_jeg_status'),
]
