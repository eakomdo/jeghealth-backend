from rest_framework import serializers
from .models import Hospital, Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for hospital departments"""
    
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class HospitalSerializer(serializers.ModelSerializer):
    """Complete hospital serializer"""
    full_address = serializers.ReadOnlyField()
    specialties_list = serializers.ReadOnlyField()
    departments = DepartmentSerializer(many=True, read_only=True)
    department_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'hospital_type', 'address', 'city', 'region', 'country',
            'full_address', 'phone_number', 'email', 'website', 'description',
            'specialties', 'specialties_list', 'facilities', 'established_year',
            'bed_capacity', 'emergency_services', 'appointment_booking_available',
            'is_active', 'created_at', 'updated_at', 'departments', 'department_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_department_count(self, obj):
        return obj.departments.filter(is_active=True).count()


class HospitalListSerializer(serializers.ModelSerializer):
    """Simplified hospital serializer for listings"""
    full_address = serializers.ReadOnlyField()
    department_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'hospital_type', 'city', 'region', 'full_address',
            'phone_number', 'emergency_services', 'is_active', 'department_count'
        ]
    
    def get_department_count(self, obj):
        return obj.departments.filter(is_active=True).count()


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


class HospitalSearchSerializer(serializers.Serializer):
    """Serializer for hospital search parameters"""
    location = serializers.CharField(required=False, help_text="City, state, or postal code")
    hospital_type = serializers.ChoiceField(
        choices=Hospital.HOSPITAL_TYPE_CHOICES,
        required=False
    )
    emergency_services = serializers.BooleanField(required=False)
    has_icu = serializers.BooleanField(required=False)
    has_surgery = serializers.BooleanField(required=False)
    specialties = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of department types to filter by"
    )
