from django.urls import path
from . import views

urlpatterns = [
    # RESTful Hospital endpoints
    path('', views.HospitalListCreateView.as_view(), name='hospital-list-create'),
    path('<uuid:pk>/', views.HospitalDetailView.as_view(), name='hospital-detail'),
    
    # Frontend integration endpoints
    path('dropdown/', views.hospital_dropdown_list, name='hospital-dropdown'),
    path('search/', views.hospital_search_autocomplete, name='hospital-search'),
]
