from django.urls import path
from . import views

urlpatterns = [
    # Medication Categories
    path('categories/', views.MedicationCategoryListView.as_view(), name='medication-category-list'),
    
    # Available Medications
    path('available/', views.MedicationListView.as_view(), name='medication-list'),
    path('available/<uuid:pk>/', views.MedicationDetailView.as_view(), name='medication-detail'),
    
    # User Medications (My Medications)
    path('', views.UserMedicationListView.as_view(), name='user-medication-list'),
    path('add/', views.UserMedicationCreateView.as_view(), name='user-medication-create'),
    path('<uuid:pk>/', views.UserMedicationDetailView.as_view(), name='user-medication-detail'),
    path('<uuid:pk>/update/', views.UserMedicationUpdateView.as_view(), name='user-medication-update'),
    path('<uuid:pk>/remove/', views.UserMedicationDeleteView.as_view(), name='user-medication-remove'),
    
    # Medication Logs
    path('logs/', views.MedicationLogListView.as_view(), name='medication-log-list'),
    path('logs/<uuid:pk>/', views.MedicationLogDetailView.as_view(), name='medication-log-detail'),
    path('log-intake/', views.log_medication_intake, name='log-medication-intake'),
    
    # Statistics and Reports
    path('stats/', views.medication_stats, name='medication-stats'),
    path('adherence-report/', views.adherence_report, name='adherence-report'),
]
