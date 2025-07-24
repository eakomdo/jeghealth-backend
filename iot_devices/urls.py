from django.urls import path
from . import views

urlpatterns = [
    # IoT Device Management
    path('', views.IoTDeviceListView.as_view(), name='iot-device-list'),
    path('register/', views.IoTDeviceCreateView.as_view(), name='iot-device-register'),
    path('<uuid:device_id>/', views.IoTDeviceDetailView.as_view(), name='iot-device-detail'),
    path('<uuid:device_id>/update/', views.IoTDeviceUpdateView.as_view(), name='iot-device-update'),
    path('<uuid:device_id>/delete/', views.IoTDeviceDeleteView.as_view(), name='iot-device-delete'),
    
    # Device Operations
    path('<uuid:device_id>/verify/', views.verify_device, name='device-verify'),
    path('<uuid:device_id>/configure/', views.update_device_configuration, name='device-configure'),
    path('<uuid:device_id>/health/', views.device_health_check, name='device-health'),
    path('<uuid:device_id>/sync/', views.sync_device_data, name='device-sync'),
    
    # Data Batches
    path('data-batches/', views.DeviceDataBatchListView.as_view(), name='device-data-batch-list'),
    path('data-batches/<uuid:batch_id>/', views.DeviceDataBatchDetailView.as_view(), name='device-data-batch-detail'),
    
    # Alerts
    path('alerts/', views.DeviceAlertListView.as_view(), name='device-alert-list'),
    path('alerts/<int:pk>/', views.DeviceAlertDetailView.as_view(), name='device-alert-detail'),
    
    # Statistics
    path('stats/', views.device_stats, name='device-stats'),
]
