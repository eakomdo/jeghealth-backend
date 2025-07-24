from django.contrib import admin
from .models import (
    MedicationCategory, Medication, UserMedication, MedicationLog,
    MedicationReminder, MedicationInteraction
)


@admin.register(MedicationCategory)
class MedicationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'brand_name', 'form', 'strength', 'requires_prescription', 'is_active']
    list_filter = ['form', 'category', 'requires_prescription', 'is_active', 'manufacturer']
    search_fields = ['name', 'generic_name', 'brand_name', 'manufacturer']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'generic_name', 'brand_name', 'category')
        }),
        ('Details', {
            'fields': ('form', 'strength', 'manufacturer', 'description')
        }),
        ('Medical Information', {
            'fields': ('side_effects', 'contraindications', 'interactions', 'storage_instructions'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('requires_prescription', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class MedicationReminderInline(admin.TabularInline):
    model = MedicationReminder
    extra = 0
    readonly_fields = ['id', 'created_at', 'updated_at']


class MedicationLogInline(admin.TabularInline):
    model = MedicationLog
    extra = 0
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_on_time', 'delay_minutes']
    ordering = ['-scheduled_time']


@admin.register(UserMedication)
class UserMedicationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'medication', 'dosage', 'frequency', 'status', 'start_date', 
        'end_date', 'remaining_quantity', 'is_active', 'needs_refill'
    ]
    list_filter = ['status', 'frequency', 'start_date', 'reminder_enabled', 'medication__form']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name', 
        'medication__name', 'prescribed_by'
    ]
    readonly_fields = [
        'id', 'is_active', 'is_expired', 'days_remaining', 'needs_refill',
        'created_at', 'updated_at'
    ]
    ordering = ['-start_date']
    date_hierarchy = 'start_date'
    inlines = [MedicationReminderInline, MedicationLogInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'medication', 'dosage', 'frequency', 'frequency_custom')
        }),
        ('Prescription Details', {
            'fields': ('prescribed_by', 'prescribed_date', 'start_date', 'end_date', 'duration_days')
        }),
        ('Instructions', {
            'fields': ('instructions', 'purpose')
        }),
        ('Tracking', {
            'fields': ('status', 'total_quantity', 'remaining_quantity', 'refills_remaining')
        }),
        ('Reminders', {
            'fields': ('reminder_enabled', 'reminder_times'),
            'classes': ('collapse',)
        }),
        ('Notes and Feedback', {
            'fields': ('notes', 'side_effects_experienced', 'effectiveness_rating'),
            'classes': ('collapse',)
        }),
        ('Computed Properties', {
            'fields': ('is_active', 'is_expired', 'days_remaining', 'needs_refill'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'medication')


@admin.register(MedicationLog)
class MedicationLogAdmin(admin.ModelAdmin):
    list_display = [
        'user_medication', 'scheduled_time', 'actual_time', 'status', 
        'is_on_time', 'delay_minutes', 'created_at'
    ]
    list_filter = ['status', 'scheduled_time', 'created_at']
    search_fields = [
        'user_medication__user__email', 'user_medication__medication__name',
        'notes', 'side_effects'
    ]
    readonly_fields = ['id', 'is_on_time', 'is_late', 'delay_minutes', 'created_at', 'updated_at']
    ordering = ['-scheduled_time']
    date_hierarchy = 'scheduled_time'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_medication', 'scheduled_time', 'actual_time', 'status')
        }),
        ('Details', {
            'fields': ('dosage_taken', 'notes', 'side_effects', 'location')
        }),
        ('Analysis', {
            'fields': ('is_on_time', 'is_late', 'delay_minutes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user_medication', 'user_medication__user', 'user_medication__medication'
        )


@admin.register(MedicationReminder)
class MedicationReminderAdmin(admin.ModelAdmin):
    list_display = [
        'user_medication', 'reminder_type', 'reminder_time', 'is_active', 'created_at'
    ]
    list_filter = ['reminder_type', 'is_active', 'created_at']
    search_fields = [
        'user_medication__user__email', 'user_medication__medication__name',
        'reminder_text'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['reminder_time']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user_medication', 'user_medication__user', 'user_medication__medication'
        )


@admin.register(MedicationInteraction)
class MedicationInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'medication1', 'medication2', 'severity', 'is_dismissed', 'created_at'
    ]
    list_filter = ['severity', 'is_dismissed', 'created_at']
    search_fields = [
        'user__email', 'medication1__name', 'medication2__name', 'description'
    ]
    readonly_fields = ['id', 'dismissed_at', 'created_at']
    ordering = ['-severity', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'medication1', 'medication2', 'severity')
        }),
        ('Details', {
            'fields': ('description', 'recommendation')
        }),
        ('Status', {
            'fields': ('is_dismissed', 'dismissed_at')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'medication1', 'medication2')
