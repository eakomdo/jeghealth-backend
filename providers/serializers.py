from rest_framework import serializers
from .models import HealthcareProvider
from hospitals.serializers import HospitalDropdownSerializer


class HealthcareProviderSerializer(serializers.ModelSerializer):
    """Serializer for healthcare providers"""
    full_name = serializers.ReadOnlyField()
    hospital_names = serializers.ReadOnlyField()
    primary_hospital = HospitalDropdownSerializer(read_only=True)
    hospitals = HospitalDropdownSerializer(many=True, read_only=True)
    hospital_ids = serializers.ListField(
        child=serializers.UUIDField(), 
        write_only=True, 
        required=False,
        help_text="List of hospital IDs to assign to this doctor"
    )
    
    class Meta:
        model = HealthcareProvider
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone_number',
            'specialization', 'license_number', 'hospitals', 'hospital_ids', 'hospital_names',
            'primary_hospital', 'hospital_clinic', 'address', 'bio', 'years_of_experience', 
            'consultation_fee', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        hospital_ids = validated_data.pop('hospital_ids', None)
        
        # Update other fields
        instance = super().update(instance, validated_data)
        
        # Update hospital relationships if provided
        if hospital_ids is not None:
            from hospitals.models import Hospital
            hospitals = Hospital.objects.filter(id__in=hospital_ids, is_active=True)
            instance.hospitals.set(hospitals)
        
        return instance


class HealthcareProviderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating healthcare providers with validation"""
    hospital_ids = serializers.ListField(
        child=serializers.UUIDField(), 
        required=False,
        help_text="List of hospital IDs where this doctor works"
    )
    
    class Meta:
        model = HealthcareProvider
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'specialization', 'license_number', 'hospital_ids',
            'address', 'bio', 'years_of_experience', 'consultation_fee'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'specialization': {'required': True},
            'license_number': {'required': True},
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
        """Create healthcare provider with hospital relationships"""
        hospital_ids = validated_data.pop('hospital_ids', [])
        
        validated_data['is_active'] = True
        provider = super().create(validated_data)
        
        # Add hospital relationships
        if hospital_ids:
            from hospitals.models import Hospital
            hospitals = Hospital.objects.filter(id__in=hospital_ids, is_active=True)
            provider.hospitals.set(hospitals)
        
        return provider


class HealthcareProviderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing healthcare providers"""
    full_name = serializers.ReadOnlyField()
    hospital_names = serializers.ReadOnlyField()
    
    class Meta:
        model = HealthcareProvider
        fields = [
            'id', 'full_name', 'specialization', 'hospital_names',
            'years_of_experience', 'consultation_fee', 'is_active'
        ]


class ProviderDropdownSerializer(serializers.ModelSerializer):
    """Minimal provider serializer for dropdown selections"""
    full_name = serializers.ReadOnlyField()
    hospital_names = serializers.ReadOnlyField()
    
    class Meta:
        model = HealthcareProvider
        fields = ['id', 'full_name', 'specialization', 'hospital_names']
