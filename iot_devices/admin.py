from django.contrib import admin
from .models import IoTDevice, DeviceDataBatch, DeviceAlert


class DeviceDataBatchInline(admin.TabularInline):
    model = DeviceDataBatch
    extra = 0
    readonly_fields = ['batch_id', 'received_at', 'processed_at']
    fields = ['batch_id', 'data_count', 'status', 'received_at', 'processed_at']


class DeviceAlertInline(admin.TabularInline):
    model = DeviceAlert
    extra = 0
    readonly_fields = ['created_at']
    fields = ['alert_type', 'severity', 'title', 'is_active', 'is_resolved', 'created_at']


@admin.register(IoTDevice)
class IoTDeviceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'device_type', 'owner', 'status', 'is_verified', 'is_online',
        'manufacturer', 'model', 'last_seen', 'created_at'
    ]
    list_filter = ['device_type', 'status', 'is_verified', 'manufacturer', 'created_at']
    search_fields = ['name', 'owner__email', 'manufacturer', 'model', 'device_id']
    readonly_fields = ['device_id', 'api_key', 'is_online', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    inlines = [DeviceDataBatchInline, DeviceAlertInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('device_id', 'name', 'device_type', 'owner')
        }),
        ('Device Details', {
            'fields': ('manufacturer', 'model', 'firmware_version', 'location')
        }),
        ('Status and Verification', {
            'fields': ('status', 'is_verified', 'last_seen', 'is_online')
        }),
        ('Capabilities', {
            'fields': ('supported_metrics', 'accuracy_score', 'calibration_date'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('configuration',),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': ('api_key',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')


@admin.register(DeviceDataBatch)
class DeviceDataBatchAdmin(admin.ModelAdmin):
    list_display = [
        'batch_id', 'device', 'data_count', 'status', 'batch_start_time',
        'batch_end_time', 'processed_count', 'error_count', 'received_at'
    ]
    list_filter = ['status', 'device__device_type', 'received_at', 'batch_start_time']
    search_fields = ['batch_id', 'device__name', 'device__owner__email']
    readonly_fields = ['batch_id', 'received_at', 'processed_at']
    ordering = ['-received_at']
    date_hierarchy = 'received_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('batch_id', 'device', 'data_count', 'status')
        }),
        ('Time Range', {
            'fields': ('batch_start_time', 'batch_end_time', 'received_at', 'processed_at')
        }),
        ('Processing Results', {
            'fields': ('processed_count', 'error_count', 'processing_errors')
        }),
        ('Data', {
            'fields': ('raw_data', 'checksum'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('device', 'device__owner')


@admin.register(DeviceAlert)
class DeviceAlertAdmin(admin.ModelAdmin):
    list_display = [
        'device', 'alert_type', 'severity', 'title', 'is_active',
        'is_acknowledged', 'is_resolved', 'created_at'
    ]
    list_filter = [
        'alert_type', 'severity', 'is_active', 'is_acknowledged', 'is_resolved',
        'device__device_type', 'created_at'
    ]
    search_fields = ['title', 'message', 'device__name', 'device__owner__email']
    readonly_fields = ['created_at', 'updated_at', 'acknowledged_at', 'resolved_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('device', 'alert_type', 'severity', 'title', 'message')
        }),
        ('Status', {
            'fields': ('is_active', 'is_acknowledged', 'acknowledged_by', 'acknowledged_at')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolution_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('device', 'device__owner', 'acknowledged_by')
