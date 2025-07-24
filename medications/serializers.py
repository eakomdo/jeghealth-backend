from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import (
    MedicationCategory, Medication, UserMedication, MedicationLog,
    MedicationReminder, MedicationInteraction
)

User = get_user_model()


class MedicationCategorySerializer(serializers.ModelSerializer):
    """Serializer for medication categories"""
    
    class Meta:
        model = MedicationCategory
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for medications"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'generic_name', 'brand_name', 'category', 'category_name',
            'form', 'strength', 'manufacturer', 'description', 'side_effects',
            'contraindications', 'interactions', 'storage_instructions',
            'requires_prescription', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing medications"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'generic_name', 'brand_name', 'category_name',
            'form', 'strength', 'requires_prescription'
        ]


class MedicationReminderSerializer(serializers.ModelSerializer):
    """Serializer for medication reminders"""
    
    class Meta:
        model = MedicationReminder
        fields = [
            'id', 'reminder_type', 'reminder_time', 'reminder_text', 'is_active',
            'snooze_duration_minutes', 'advance_notice_minutes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserMedicationSerializer(serializers.ModelSerializer):
    """Main serializer for user medications"""
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    medication_strength = serializers.CharField(source='medication.strength', read_only=True)
    medication_form = serializers.CharField(source='medication.form', read_only=True)
    medication_details = MedicationSerializer(source='medication', read_only=True)
    reminders = MedicationReminderSerializer(many=True, read_only=True)
    is_active = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    needs_refill = serializers.ReadOnlyField()
    
    class Meta:
        model = UserMedication
        fields = [
            'id', 'medication', 'medication_name', 'medication_strength', 'medication_form',
            'medication_details', 'dosage', 'frequency', 'frequency_custom', 'prescribed_by',
            'prescribed_date', 'start_date', 'end_date', 'duration_days', 'instructions',
            'purpose', 'status', 'total_quantity', 'remaining_quantity', 'refills_remaining',
            'reminder_enabled', 'reminder_times', 'notes', 'side_effects_experienced',
            'effectiveness_rating', 'reminders', 'is_active', 'is_expired', 'days_remaining',
            'needs_refill', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'medication_name', 'medication_strength', 'medication_form',
            'is_active', 'is_expired', 'days_remaining', 'needs_refill',
            'created_at', 'updated_at'
        ]

    def validate_start_date(self, value):
        """Validate start date is not in the far past"""
        if value < timezone.now().date() - timedelta(days=365):
            raise serializers.ValidationError("Start date cannot be more than a year in the past")
        return value

    def validate_end_date(self, value):
        """Validate end date is after start date"""
        start_date = self.initial_data.get('start_date')
        if start_date and value:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                if value <= start_date:
                    raise serializers.ValidationError("End date must be after start date")
            except ValueError:
                pass
        return value

    def validate_effectiveness_rating(self, value):
        """Validate effectiveness rating is between 1 and 5"""
        if value is not None and not 1 <= value <= 5:
            raise serializers.ValidationError("Effectiveness rating must be between 1 and 5")
        return value

    def validate_reminder_times(self, value):
        """Validate reminder times format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Reminder times must be a list")
        
        for time_str in value:
            try:
                datetime.strptime(time_str, '%H:%M')
            except ValueError:
                raise serializers.ValidationError(f"Invalid time format: {time_str}. Use HH:MM format")
        
        return value

    def create(self, validated_data):
        # Set user to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            
        # Set remaining quantity to total quantity if not provided
        if validated_data.get('total_quantity') and not validated_data.get('remaining_quantity'):
            validated_data['remaining_quantity'] = validated_data['total_quantity']
            
        return super().create(validated_data)


class UserMedicationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing user medications"""
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    medication_strength = serializers.CharField(source='medication.strength', read_only=True)
    is_active = serializers.ReadOnlyField()
    needs_refill = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = UserMedication
        fields = [
            'id', 'medication_name', 'medication_strength', 'dosage', 'frequency',
            'start_date', 'end_date', 'status', 'remaining_quantity', 'is_active',
            'needs_refill', 'days_remaining', 'reminder_enabled'
        ]


class MedicationLogSerializer(serializers.ModelSerializer):
    """Serializer for medication logs"""
    medication_name = serializers.CharField(source='user_medication.medication.name', read_only=True)
    is_on_time = serializers.ReadOnlyField()
    is_late = serializers.ReadOnlyField()
    delay_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = MedicationLog
        fields = [
            'id', 'user_medication', 'medication_name', 'scheduled_time', 'actual_time',
            'status', 'dosage_taken', 'notes', 'side_effects', 'location',
            'is_on_time', 'is_late', 'delay_minutes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'medication_name', 'is_on_time', 'is_late', 'delay_minutes',
            'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Cross-field validation"""
        # Set actual_time to now if status is 'taken' and actual_time not provided
        if data.get('status') == 'taken' and not data.get('actual_time'):
            data['actual_time'] = timezone.now()
        
        # Verify user owns the medication
        user_medication = data.get('user_medication')
        request = self.context.get('request')
        if request and user_medication and user_medication.user != request.user:
            raise serializers.ValidationError("You can only log your own medications")
            
        return data

    def create(self, validated_data):
        """Create log entry and update medication quantity"""
        log = super().create(validated_data)
        
        # Update remaining quantity if medication was taken
        if log.status == 'taken':
            user_medication = log.user_medication
            if user_medication.remaining_quantity is not None:
                # Assume 1 dose taken unless specified otherwise
                doses_taken = 1
                user_medication.update_quantity(doses_taken)
                
        return log


class MedicationInteractionSerializer(serializers.ModelSerializer):
    """Serializer for medication interactions"""
    medication1_name = serializers.CharField(source='medication1.name', read_only=True)
    medication2_name = serializers.CharField(source='medication2.name', read_only=True)
    
    class Meta:
        model = MedicationInteraction
        fields = [
            'id', 'medication1', 'medication1_name', 'medication2', 'medication2_name',
            'severity', 'description', 'recommendation', 'is_dismissed', 'dismissed_at',
            'created_at'
        ]
        read_only_fields = [
            'id', 'medication1_name', 'medication2_name', 'dismissed_at', 'created_at'
        ]

    def update(self, instance, validated_data):
        """Handle dismissal of interactions"""
        if validated_data.get('is_dismissed') and not instance.is_dismissed:
            validated_data['dismissed_at'] = timezone.now()
        elif not validated_data.get('is_dismissed', True) and instance.is_dismissed:
            validated_data['dismissed_at'] = None
            
        return super().update(instance, validated_data)


class MedicationStatsSerializer(serializers.Serializer):
    """Serializer for medication statistics"""
    total_medications = serializers.IntegerField()
    active_medications = serializers.IntegerField()
    expired_medications = serializers.IntegerField()
    medications_needing_refill = serializers.IntegerField()
    adherence_rate = serializers.FloatField()
    missed_doses_last_week = serializers.IntegerField()
    on_time_percentage = serializers.FloatField()
    most_common_side_effect = serializers.CharField()
    medication_categories = serializers.DictField()
    frequency_distribution = serializers.DictField()
    monthly_adherence = serializers.ListField()


class AdherenceReportSerializer(serializers.Serializer):
    """Serializer for medication adherence reports"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_scheduled_doses = serializers.IntegerField()
    taken_doses = serializers.IntegerField()
    missed_doses = serializers.IntegerField()
    adherence_percentage = serializers.FloatField()
    medications = serializers.ListField()
    daily_adherence = serializers.ListField()
