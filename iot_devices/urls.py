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
    
    # === iOS Device Detection Endpoints ===
    
    # Device Scanning
    path('scan/start/', views.start_device_scan, name='start-device-scan'),
    path('scan/<uuid:scan_id>/status/', views.get_scan_status, name='get-scan-status'),
    path('scan/<uuid:scan_id>/results/', views.get_scan_results, name='get-scan-results'),
    path('scan/sessions/', views.DeviceScanSessionListView.as_view(), name='device-scan-sessions'),
    
    # Detected Devices
    path('detected/', views.DetectedDeviceListView.as_view(), name='detected-devices-list'),
    path('detected/<uuid:pk>/', views.DetectedDeviceDetailView.as_view(), name='detected-device-detail'),
    
    # iOS Device Profiles
    path('ios-profiles/', views.iOSDeviceProfileListView.as_view(), name='ios-device-profiles'),
    path('ios-profiles/create/', views.create_ios_device_profile, name='create-ios-device-profile'),
    path('ios-profiles/<uuid:pk>/', views.iOSDeviceProfileDetailView.as_view(), name='ios-device-profile-detail'),
    
    # Detection Statistics
    path('detection-stats/', views.device_detection_stats, name='device-detection-stats'),
]
