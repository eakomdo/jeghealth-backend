from django.urls import path
from . import views

urlpatterns = [
    # Healthcare Provider endpoints
    path('providers/', views.HealthcareProviderListView.as_view(), name='healthcare-provider-list'),
    path('providers/<uuid:pk>/', views.HealthcareProviderDetailView.as_view(), name='healthcare-provider-detail'),
    
    # Appointment endpoints
    path('', views.AppointmentListView.as_view(), name='appointment-list'),
    path('create/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('<uuid:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('<uuid:pk>/update/', views.AppointmentUpdateView.as_view(), name='appointment-update'),
    path('<uuid:pk>/cancel/', views.AppointmentDeleteView.as_view(), name='appointment-cancel'),
    path('<uuid:appointment_id>/reschedule/', views.reschedule_appointment, name='appointment-reschedule'),
    
    # Appointment Files endpoints
    path('<uuid:appointment_id>/files/', views.AppointmentFileListView.as_view(), name='appointment-file-list'),
    path('files/<uuid:pk>/', views.AppointmentFileDetailView.as_view(), name='appointment-file-detail'),
    
    # Appointment Rating endpoints
    path('<uuid:appointment_id>/rate/', views.AppointmentRatingCreateView.as_view(), name='appointment-rating-create'),
    path('ratings/<uuid:pk>/', views.AppointmentRatingUpdateView.as_view(), name='appointment-rating-update'),
    
    # Statistics and Analytics endpoints
    path('stats/', views.appointment_stats, name='appointment-stats'),
    path('upcoming/', views.upcoming_appointments, name='upcoming-appointments'),
    path('history/', views.appointment_history, name='appointment-history'),
]
