from django.contrib import admin
from .models import Hospital, Department

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'hospital_type', 'emergency_services', 'is_active']
    list_filter = ['hospital_type', 'emergency_services', 'has_icu', 'has_surgery', 'is_active']
    search_fields = ['name', 'city', 'state']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'hospital_type', 'address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'website')
        }),
        ('Services', {
            'fields': ('emergency_services', 'has_icu', 'has_surgery', 'has_maternity', 'has_pediatrics')
        }),
        ('Details', {
            'fields': ('bed_count', 'established_year')
        }),
        ('Status', {
            'fields': ('is_active', 'verified')
        }),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital', 'department_type', 'is_active']
    list_filter = ['department_type', 'is_active', 'hospital']
    search_fields = ['name', 'hospital__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
