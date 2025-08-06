from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import HealthcareProvider, Appointment, AppointmentFile, AppointmentRating

User = get_user_model()


class HealthcareProviderSerializer(serializers.ModelSerializer):
    """Serializer for healthcare providers"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = HealthcareProvider
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone_number',
            'specialization', 'license_number', 'hospital_clinic', 'address', 'bio',
            'years_of_experience', 'consultation_fee', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HealthcareProviderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating healthcare providers with validation"""
    
    class Meta:
        model = HealthcareProvider
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'specialization', 'license_number', 'hospital_clinic', 'address', 'bio',
            'years_of_experience', 'consultation_fee'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'specialization': {'required': True},
            'license_number': {'required': True},
            'hospital_clinic': {'required': True},
        }

    def validate_email(self, value):
        """Ensure email is unique"""
        if HealthcareProvider.objects.filter(email=value).exists():
            raise serializers.ValidationError("Healthcare provider with this email already exists.")
        return value

    def validate_license_number(self, value):
        """Ensure license number is unique"""
        if HealthcareProvider.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("Healthcare provider with this license number already exists.")
        return value

    def create(self, validated_data):
        """Create healthcare provider with is_active=True by default"""
        validated_data['is_active'] = True
        return super().create(validated_data)


class HealthcareProviderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing healthcare providers"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = HealthcareProvider
        fields = [
            'id', 'full_name', 'specialization', 'hospital_clinic',
            'years_of_experience', 'consultation_fee', 'is_active'
        ]


class AppointmentFileSerializer(serializers.ModelSerializer):
    """Serializer for appointment files"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = AppointmentFile
        fields = [
            'id', 'file', 'file_name', 'file_type', 'file_size', 'description',
            'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'file_size', 'uploaded_by', 'created_at']

    def create(self, validated_data):
        # Auto-set file_name and file_size if not provided
        file_obj = validated_data.get('file')
        if file_obj:
            if not validated_data.get('file_name'):
                validated_data['file_name'] = file_obj.name
            validated_data['file_size'] = file_obj.size
        
        # Set uploaded_by to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user
            
        return super().create(validated_data)


class AppointmentRatingSerializer(serializers.ModelSerializer):
    """Serializer for appointment ratings"""
    
    class Meta:
        model = AppointmentRating
        fields = [
            'id', 'rating', 'feedback', 'would_recommend', 'punctuality_rating',
            'communication_rating', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_punctuality_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Punctuality rating must be between 1 and 5")
        return value

    def validate_communication_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Communication rating must be between 1 and 5")
        return value


class AppointmentSerializer(serializers.ModelSerializer):
    """Main serializer for appointments"""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    healthcare_provider_name = serializers.CharField(source='healthcare_provider.full_name', read_only=True)
    healthcare_provider_specialization = serializers.CharField(source='healthcare_provider.specialization', read_only=True)
    end_time = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    can_be_rescheduled = serializers.ReadOnlyField()
    files = AppointmentFileSerializer(many=True, read_only=True)
    rating = AppointmentRatingSerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'healthcare_provider', 'healthcare_provider_name',
            'healthcare_provider_specialization', 'appointment_date', 'end_time', 'duration_minutes',
            'appointment_type', 'status', 'priority', 'chief_complaint', 'symptoms', 'notes',
            'diagnosis', 'treatment_plan', 'prescribed_medications', 'follow_up_instructions',
            'next_appointment_recommended', 'consultation_fee', 'payment_status',
            'reminder_sent', 'reminder_sent_at', 'is_past', 'is_today', 'is_upcoming',
            'can_be_cancelled', 'can_be_rescheduled', 'files', 'rating',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'patient_name', 'healthcare_provider_name', 'healthcare_provider_specialization',
            'end_time', 'is_past', 'is_today', 'is_upcoming', 'can_be_cancelled', 'can_be_rescheduled',
            'reminder_sent', 'reminder_sent_at', 'created_at', 'updated_at', 'created_by'
        ]

    def validate_appointment_date(self, value):
        """Validate that appointment date is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future")
        return value

    def validate_duration_minutes(self, value):
        """Validate appointment duration"""
        if not 15 <= value <= 480:
            raise serializers.ValidationError("Duration must be between 15 minutes and 8 hours")
        return value

    def validate(self, data):
        """Cross-field validation"""
        # Check if healthcare provider is active
        healthcare_provider = data.get('healthcare_provider')
        if healthcare_provider and not healthcare_provider.is_active:
            raise serializers.ValidationError("Cannot book appointment with inactive healthcare provider")
        
        # Set consultation fee from healthcare provider if not provided
        if healthcare_provider and not data.get('consultation_fee'):
            data['consultation_fee'] = healthcare_provider.consultation_fee
            
        return data

    def create(self, validated_data):
        # Set patient to current user if not provided
        request = self.context.get('request')
        if request and request.user.is_authenticated and not validated_data.get('patient'):
            validated_data['patient'] = request.user
            
        # Set created_by to current user
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
            
        return super().create(validated_data)


class AppointmentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing appointments"""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    healthcare_provider_name = serializers.CharField(source='healthcare_provider.full_name', read_only=True)
    healthcare_provider_specialization = serializers.CharField(source='healthcare_provider.specialization', read_only=True)
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient_name', 'healthcare_provider_name', 'healthcare_provider_specialization',
            'appointment_date', 'duration_minutes', 'appointment_type', 'status', 'priority',
            'chief_complaint', 'consultation_fee', 'payment_status', 'is_upcoming'
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    
    class Meta:
        model = Appointment
        fields = [
            'healthcare_provider', 'appointment_date', 'duration_minutes', 'appointment_type',
            'priority', 'chief_complaint', 'symptoms', 'notes'
        ]

    def validate_appointment_date(self, value):
        """Validate that appointment date is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future")
        return value

    def create(self, validated_data):
        # Set patient to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['patient'] = request.user
            validated_data['created_by'] = request.user
            
        # Set consultation fee from healthcare provider
        healthcare_provider = validated_data.get('healthcare_provider')
        if healthcare_provider:
            validated_data['consultation_fee'] = healthcare_provider.consultation_fee
            
        return super().create(validated_data)


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointments"""
    
    class Meta:
        model = Appointment
        fields = [
            'appointment_date', 'duration_minutes', 'appointment_type', 'status', 'priority',
            'chief_complaint', 'symptoms', 'notes', 'diagnosis', 'treatment_plan',
            'prescribed_medications', 'follow_up_instructions', 'next_appointment_recommended',
            'payment_status'
        ]

    def validate_appointment_date(self, value):
        """Validate that appointment date is in the future for non-completed appointments"""
        instance = getattr(self, 'instance', None)
        if instance and instance.status not in ['completed', 'cancelled'] and value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future")
        return value

    def validate_status(self, value):
        """Validate status transitions"""
        instance = getattr(self, 'instance', None)
        if instance:
            # Cannot change status of completed appointments
            if instance.status == 'completed' and value != 'completed':
                raise serializers.ValidationError("Cannot change status of completed appointment")
            
            # Cannot mark past appointments as scheduled/confirmed
            if instance.is_past and value in ['scheduled', 'confirmed']:
                raise serializers.ValidationError("Cannot mark past appointment as scheduled or confirmed")
                
        return value


class AppointmentStatsSerializer(serializers.Serializer):
    """Serializer for appointment statistics"""
    total_appointments = serializers.IntegerField()
    scheduled_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    upcoming_appointments = serializers.IntegerField()
    today_appointments = serializers.IntegerField()
    average_rating = serializers.FloatField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)
    most_visited_specialization = serializers.CharField()
    appointment_types_distribution = serializers.DictField()
    monthly_appointments = serializers.ListField()
