from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import HealthMetric, HealthMetricTarget, HealthMetricSummary


@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    """
    Admin interface for health metrics.
    """
    list_display = [
        'user', 'metric_type', 'display_value', 'unit', 
        'recorded_at', 'is_manual_entry', 'device', 'is_anomaly'
    ]
    list_filter = [
        'metric_type', 'is_manual_entry', 'is_anomaly', 
        'recorded_at', 'created_at', 'device__device_type'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'device__name', 'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'recorded_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'metric_type', 'recorded_at')
        }),
        (_('Values'), {
            'fields': ('value', 'unit', 'systolic_value', 'diastolic_value')
        }),
        (_('Source'), {
            'fields': ('is_manual_entry', 'device', 'confidence_score')
        }),
        (_('Additional Information'), {
            'fields': ('notes', 'is_anomaly'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'device')


@admin.register(HealthMetricTarget)
class HealthMetricTargetAdmin(admin.ModelAdmin):
    """
    Admin interface for health metric targets.
    """
    list_display = [
        'user', 'metric_type', 'target_value', 'target_unit',
        'target_type', 'target_date', 'is_active'
    ]
    list_filter = [
        'metric_type', 'target_type', 'is_active', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name', 'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'metric_type', 'is_active')
        }),
        (_('Target Values'), {
            'fields': ('target_value', 'target_unit', 'target_systolic', 'target_diastolic')
        }),
        (_('Target Type'), {
            'fields': ('target_type', 'min_value', 'max_value', 'target_date')
        }),
        (_('Additional Information'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HealthMetricSummary)
class HealthMetricSummaryAdmin(admin.ModelAdmin):
    """
    Admin interface for health metric summaries.
    """
    list_display = [
        'user', 'metric_type', 'period_type', 'period_start', 
        'period_end', 'reading_count', 'average_value', 'trend_direction'
    ]
    list_filter = [
        'metric_type', 'period_type', 'trend_direction', 
        'period_start', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'metric_type', 'period_type')
        }),
        (_('Period'), {
            'fields': ('period_start', 'period_end', 'reading_count')
        }),
        (_('Statistics'), {
            'fields': ('average_value', 'min_value', 'max_value', 'variance')
        }),
        (_('Blood Pressure Stats'), {
            'fields': ('avg_systolic', 'avg_diastolic'),
            'classes': ('collapse',)
        }),
        (_('Trends'), {
            'fields': ('trend_direction',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
