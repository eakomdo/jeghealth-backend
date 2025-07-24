from django.urls import path
from . import views

urlpatterns = [
    # Health metrics CRUD
    path('', views.HealthMetricListCreateView.as_view(), name='health_metrics_list_create'),
    path('<int:pk>/', views.HealthMetricDetailView.as_view(), name='health_metric_detail'),
    
    # Bulk operations
    path('bulk-create/', views.HealthMetricBulkCreateView.as_view(), name='health_metrics_bulk_create'),
    
    # Analytics and statistics
    path('stats/', views.HealthMetricStatsView.as_view(), name='health_metrics_stats'),
    path('generate-summaries/', views.generate_summaries, name='generate_summaries'),
    
    # Targets/Goals
    path('targets/', views.HealthMetricTargetListCreateView.as_view(), name='health_metric_targets'),
    path('targets/<int:pk>/', views.HealthMetricTargetDetailView.as_view(), name='health_metric_target_detail'),
    
    # Utility endpoints
    path('metric-types/', views.get_metric_types, name='metric_types'),
]
