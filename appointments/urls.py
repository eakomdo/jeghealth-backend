from django.urls import path
from . import views

urlpatterns = [
    # Appointment endpoints (Patient-focused)
    path('', views.AppointmentListView.as_view(), name='appointment-list'),
    path('create/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('<uuid:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('<uuid:pk>/update/', views.AppointmentUpdateView.as_view(), name='appointment-update'),
    path('<uuid:pk>/cancel/', views.AppointmentDeleteView.as_view(), name='appointment-cancel'),
    path('<uuid:appointment_id>/reschedule/', views.reschedule_appointment, name='appointment-reschedule'),
    
    # Doctor-specific appointment endpoints
    path('doctor/<uuid:doctor_id>/', views.DoctorAppointmentListView.as_view(), name='doctor-appointment-list'),
    path('doctor/<uuid:doctor_id>/today/', views.DoctorTodaysAppointmentsView.as_view(), name='doctor-todays-appointments'),
    path('doctor/<uuid:doctor_id>/upcoming/', views.DoctorUpcomingAppointmentsView.as_view(), name='doctor-upcoming-appointments'),
    path('doctor/<uuid:doctor_id>/stats/', views.DoctorAppointmentStatsView.as_view(), name='doctor-appointment-stats'),
    path('doctor/<uuid:doctor_id>/appointment/<uuid:appointment_id>/', views.DoctorAppointmentDetailView.as_view(), name='doctor-appointment-detail'),
    path('doctor/<uuid:doctor_id>/appointment/<uuid:appointment_id>/update-status/', views.doctor_update_appointment_status, name='doctor-update-appointment-status'),
    
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

    # Frontend-compatible endpoints
    path('frontend/', views.FrontendAppointmentListCreateView.as_view(), name='frontend-appointments'),
    path('frontend/choices/', views.frontend_appointment_choices, name='frontend-appointment-choices'),
]
