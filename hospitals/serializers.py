from rest_framework import serializers
from .models import Hospital


class HospitalSerializer(serializers.ModelSerializer):
    """Complete hospital serializer"""
    full_address = serializers.ReadOnlyField()
    specialties_list = serializers.ReadOnlyField()
    
    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'hospital_type', 'address', 'city', 'region', 'country',
            'full_address', 'phone_number', 'email', 'website', 'description',
            'specialties', 'specialties_list', 'facilities', 'established_year',
            'bed_capacity', 'emergency_services', 'appointment_booking_available',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HospitalListSerializer(serializers.ModelSerializer):
    """Simplified hospital serializer for listings"""
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'hospital_type', 'city', 'region', 'full_address',
            'phone_number', 'emergency_services', 'is_active'
        ]


class HospitalCreateSerializer(serializers.ModelSerializer):
    """Hospital creation serializer with validation"""
    
    class Meta:
        model = Hospital
        fields = [
            'name', 'hospital_type', 'address', 'city', 'region', 'country',
            'phone_number', 'email', 'website', 'description', 'specialties',
            'facilities', 'established_year', 'bed_capacity', 'emergency_services'
        ]
        extra_kwargs = {
            'name': {'required': True},
            'address': {'required': True},
            'city': {'required': True},
            'region': {'required': True},
        }

    def validate_name(self, value):
        """Ensure hospital name is unique"""
        if Hospital.objects.filter(name=value).exists():
            raise serializers.ValidationError("Hospital with this name already exists.")
        return value

    def create(self, validated_data):
        """Create hospital with is_active=True by default"""
        validated_data['is_active'] = True
        return super().create(validated_data)


class HospitalDropdownSerializer(serializers.ModelSerializer):
    """Minimal hospital serializer for dropdown selections"""
    
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'city', 'hospital_type']
