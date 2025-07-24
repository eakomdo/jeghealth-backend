from django.contrib import admin
from .models import HealthcareProvider, Appointment, AppointmentFile, AppointmentRating


@admin.register(HealthcareProvider)
class HealthcareProviderAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'hospital_clinic', 'years_of_experience', 'consultation_fee', 'is_active']
    list_filter = ['specialization', 'hospital_clinic', 'is_active', 'years_of_experience']
    search_fields = ['first_name', 'last_name', 'email', 'specialization', 'license_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['last_name', 'first_name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Professional Information', {
            'fields': ('specialization', 'license_number', 'hospital_clinic', 'years_of_experience', 'consultation_fee')
        }),
        ('Details', {
            'fields': ('address', 'bio')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class AppointmentFileInline(admin.TabularInline):
    model = AppointmentFile
    extra = 0
    readonly_fields = ['id', 'file_size', 'uploaded_by', 'created_at']


class AppointmentRatingInline(admin.StackedInline):
    model = AppointmentRating
    extra = 0
    readonly_fields = ['id', 'created_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'healthcare_provider', 'appointment_date', 'duration_minutes', 
        'appointment_type', 'status', 'priority', 'consultation_fee', 'payment_status'
    ]
    list_filter = [
        'status', 'appointment_type', 'priority', 'payment_status', 
        'healthcare_provider__specialization', 'appointment_date'
    ]
    search_fields = [
        'patient__email', 'patient__first_name', 'patient__last_name',
        'healthcare_provider__first_name', 'healthcare_provider__last_name',
        'chief_complaint', 'diagnosis'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'end_time', 'is_past', 'is_today', 'is_upcoming']
    ordering = ['-appointment_date']
    date_hierarchy = 'appointment_date'
    inlines = [AppointmentFileInline, AppointmentRatingInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'healthcare_provider', 'appointment_date', 'duration_minutes')
        }),
        ('Appointment Details', {
            'fields': ('appointment_type', 'status', 'priority', 'chief_complaint', 'symptoms', 'notes')
        }),
        ('Medical Information', {
            'fields': ('diagnosis', 'treatment_plan', 'prescribed_medications', 'follow_up_instructions', 'next_appointment_recommended'),
            'classes': ('collapse',)
        }),
        ('Administrative', {
            'fields': ('consultation_fee', 'payment_status'),
            'classes': ('collapse',)
        }),
        ('Reminders', {
            'fields': ('reminder_sent', 'reminder_sent_at'),
            'classes': ('collapse',)
        }),
        ('Computed Properties', {
            'fields': ('end_time', 'is_past', 'is_today', 'is_upcoming'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'healthcare_provider', 'created_by')


@admin.register(AppointmentFile)
class AppointmentFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'appointment', 'file_type', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name', 'description', 'appointment__patient__email']
    readonly_fields = ['id', 'file_size', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('appointment', 'uploaded_by')


@admin.register(AppointmentRating)
class AppointmentRatingAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'rating', 'punctuality_rating', 'communication_rating', 'would_recommend', 'created_at']
    list_filter = ['rating', 'would_recommend', 'punctuality_rating', 'communication_rating', 'created_at']
    search_fields = ['appointment__patient__email', 'feedback']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('appointment')
