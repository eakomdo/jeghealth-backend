from django.urls import path
from . import views

urlpatterns = [
    # RESTful Healthcare Provider endpoints
    path('', views.HealthcareProviderListCreateView.as_view(), name='provider-list-create'),
    path('<uuid:pk>/', views.HealthcareProviderDetailView.as_view(), name='provider-detail'),
    
    # Frontend integration endpoints
    path('dropdown/', views.provider_dropdown_list, name='provider-dropdown'),
    path('search/', views.provider_search_autocomplete, name='provider-search'),
    path('hospital/<uuid:hospital_id>/', views.providers_by_hospital, name='providers-by-hospital'),
]



