from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, Role, UserRole
from providers.models import HealthcareProvider


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Based on the registration flow in your mobile app.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 
            'phone_number', 'date_of_birth', 'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True},
        }
    
    def validate(self, data):
        """Validate that passwords match and set default username."""
        # Default username to email if not provided
        if not data.get('username'):
            data['username'] = data.get('email')
        # Check password confirmation
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def validate_email(self, value):
        """Validate that email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate_username(self, value):
        """Validate that username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    
    def create(self, validated_data):
        """Create a new user with encrypted password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile if it doesn't exist
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Invalid email or password.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Email and password are required.',
                code='authorization'
            )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    """
    bmi = serializers.ReadOnlyField()
    # Override gender field to handle case insensitivity
    gender = serializers.CharField(max_length=1, required=False, allow_blank=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'gender', 'height', 'weight', 'blood_type',
            'medical_conditions', 'current_medications', 'allergies',
            'health_goals', 'activity_level', 'email_notifications',
            'push_notifications', 'health_reminders', 'bmi',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_gender(self, value):
        """
        Validate gender field and handle case sensitivity.
        Accept lowercase input and convert to uppercase.
        Only Male (M) and Female (F) are allowed.
        """
        if value:
            # Convert to uppercase for consistency
            value = value.upper()
            
            # Check if it's a valid choice - only M or F
            valid_choices = ['M', 'F']
            if value not in valid_choices:
                raise serializers.ValidationError(
                    "Invalid gender choice. Must be either 'M' (Male) or 'F' (Female)"
                )
        
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information.
    """
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'profile_image',
            'emergency_contact_name', 'emergency_contact_phone',
            'is_email_verified', 'is_phone_verified', 'full_name',
            'profile', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_email_verified', 'is_phone_verified', 
            'created_at', 'updated_at'
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'profile_image', 'emergency_contact_name', 'emergency_contact_phone'
        ]
    
    def update(self, instance, validated_data):
        """Update user instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def save(self):
        """Save new password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for role information.
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'is_active']
        read_only_fields = ['id']


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for user role assignments.
    """
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'assigned_at', 'assigned_by']
        read_only_fields = ['id', 'assigned_at']


class UserWithRolesSerializer(serializers.ModelSerializer):
    """
    Serializer for user with role information.
    Matches the structure used in your mobile app AuthContext.
    """
    profile = UserProfileSerializer(read_only=True)
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'profile_image',
            'emergency_contact_name', 'emergency_contact_phone',
            'is_email_verified', 'is_phone_verified', 'profile',
            'roles', 'permissions', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_email_verified', 'is_phone_verified',
            'created_at', 'updated_at'
        ]
    
    def get_roles(self, obj):
        """Get user roles."""
        user_roles = UserRole.objects.filter(user=obj).select_related('role')
        return [ur.role.name for ur in user_roles]
    
    def get_permissions(self, obj):
        """Get user permissions from all assigned roles."""
        permissions = {}
        user_roles = UserRole.objects.filter(user=obj).select_related('role')
        
        for user_role in user_roles:
            if user_role.role.permissions:
                permissions.update(user_role.role.permissions)
        
        return permissions


class ComprehensiveUserRegistrationSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for user registration including profile data.
    Handles user creation along with profile information in a single request.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=False, allow_blank=True)
    
    # Profile fields
    gender = serializers.CharField(max_length=1, required=False, allow_blank=True)
    height = serializers.FloatField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)
    blood_type = serializers.CharField(max_length=10, required=False, allow_blank=True)
    medical_conditions = serializers.CharField(required=False, allow_blank=True)
    current_medications = serializers.CharField(required=False, allow_blank=True)
    allergies = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 
            'phone_number', 'date_of_birth', 'password', 'password_confirm',
            'gender', 'height', 'weight', 'blood_type',
            'medical_conditions', 'current_medications', 'allergies'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True},
        }
    
    def validate_gender(self, value):
        """
        Validate gender field and handle case sensitivity.
        Accept lowercase input and convert to uppercase.
        Only Male (M) and Female (F) are allowed.
        """
        if value:
            # Convert to uppercase for consistency
            value = value.upper()
            
            # Check if it's a valid choice - only M or F
            valid_choices = ['M', 'F']
            if value not in valid_choices:
                raise serializers.ValidationError(
                    "Invalid gender choice. Must be either 'M' (Male) or 'F' (Female)"
                )
        
        return value
    
    def validate(self, data):
        """Validate that passwords match and set default username."""
        # Default username to email if not provided
        if not data.get('username'):
            data['username'] = data.get('email')
        # Check password confirmation
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def validate_email(self, value):
        """Validate that email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate_username(self, value):
        """Validate that username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    
    def create(self, validated_data):
        """Create a new user with profile data."""
        # Extract profile fields
        profile_fields = {
            'gender': validated_data.pop('gender', ''),
            'height': validated_data.pop('height', None),
            'weight': validated_data.pop('weight', None),
            'blood_type': validated_data.pop('blood_type', ''),
            'medical_conditions': validated_data.pop('medical_conditions', ''),
            'current_medications': validated_data.pop('current_medications', ''),
            'allergies': validated_data.pop('allergies', ''),
        }
        
        # Create user
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create or update user profile
        if hasattr(user, 'profile'):
            profile = user.profile
            for field, value in profile_fields.items():
                if value:  # Only update non-empty values
                    setattr(profile, field, value)
            profile.save()
        else:
            UserProfile.objects.create(user=user, **profile_fields)
        
        return user


class BasicInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for basic user information: full name, email, profile image
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'full_name', 'email', 'profile_image']
        read_only_fields = ['full_name']
    
    def validate_email(self, value):
        """Validate that email is unique (excluding current user)."""
        user = self.instance
        if user and User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Email already exists.")
        elif not user and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


class PersonalInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for personal information: age, gender, blood type, height, weight
    Combines User model (date_of_birth) with UserProfile model fields
    """
    # Fields from User model
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    age = serializers.SerializerMethodField()
    
    # Fields from UserProfile model
    gender = serializers.CharField(max_length=1, required=False, allow_blank=True)
    height = serializers.FloatField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)
    blood_type = serializers.CharField(max_length=10, required=False, allow_blank=True)
    bmi = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['date_of_birth', 'age', 'gender', 'blood_type', 'height', 'weight', 'bmi']
        read_only_fields = ['age', 'bmi']
    
    def get_age(self, obj):
        """Calculate age from date of birth"""
        if obj.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
        return None
    
    def validate_gender(self, value):
        """
        Validate gender field and handle case sensitivity.
        Only Male (M) and Female (F) are allowed.
        """
        if value:
            # Convert to uppercase for consistency
            value = value.upper()
            
            # Check if it's a valid choice - only M or F
            valid_choices = ['M', 'F']
            if value not in valid_choices:
                raise serializers.ValidationError(
                    "Invalid gender choice. Must be either 'M' (Male) or 'F' (Female)"
                )
        
        return value
    
    def update(self, instance, validated_data):
        """Update user and profile data"""
        # Extract profile fields
        profile_fields = {}
        user_fields = {}
        
        for field_name, value in validated_data.items():
            if field_name in ['gender', 'height', 'weight', 'blood_type']:
                profile_fields[field_name] = value
            else:
                user_fields[field_name] = value
        
        # Update user fields
        for field_name, value in user_fields.items():
            setattr(instance, field_name, value)
        instance.save()
        
        # Update profile fields
        if profile_fields:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for field_name, value in profile_fields.items():
                setattr(profile, field_name, value)
            profile.save()
        
        return instance
    
    def to_representation(self, instance):
        """Custom representation to include profile data"""
        data = super().to_representation(instance)
        
        # Add profile fields
        if hasattr(instance, 'profile'):
            profile = instance.profile
            data['gender'] = profile.gender
            data['height'] = profile.height
            data['weight'] = profile.weight
            data['blood_type'] = profile.blood_type
            data['bmi'] = profile.bmi
        else:
            data['gender'] = ''
            data['height'] = None
            data['weight'] = None
            data['blood_type'] = ''
            data['bmi'] = None
        
        return data


class ProviderRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for healthcare provider registration.
    Creates both User account and HealthcareProvider record.
    Includes all professional form fields.
    """
    # Security fields
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    # Professional Information fields
    professional_title = serializers.ChoiceField(
        choices=HealthcareProvider.PROFESSIONAL_TITLE_CHOICES,
        help_text="Professional title (Dr., RN, etc.)"
    )
    organization_facility = serializers.CharField(
        max_length=200,
        help_text="Organization/Facility (General Hospital, Private Practice, etc.)"
    )
    professional_role = serializers.ChoiceField(
        choices=HealthcareProvider.PROFESSIONAL_ROLE_CHOICES,
        help_text="Primary professional role"
    )
    specialization = serializers.CharField(max_length=100, required=False, allow_blank=True)
    license_number = serializers.CharField(
        max_length=50,
        help_text="Professional license number for verification"
    )
    
    # Optional fields
    additional_information = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Tell us about your specific IoT monitoring needs or questions"
    )
    
    # Legacy fields (backward compatibility)
    years_of_experience = serializers.IntegerField(min_value=0, default=0, required=False)
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.00, required=False)
    bio = serializers.CharField(required=False, allow_blank=True)
    hospital_clinic = serializers.CharField(max_length=200, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            # User account fields
            'email', 'username', 'first_name', 'last_name', 'phone_number',
            'password', 'password_confirm',
            # Professional fields  
            'professional_title', 'organization_facility', 'professional_role',
            'specialization', 'license_number', 'additional_information',
            # Legacy fields
            'years_of_experience', 'consultation_fee', 'bio', 'hospital_clinic', 'address'
        ]

    def validate(self, attrs):
        # Password validation
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        if len(attrs['password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        # Check if license number is unique
        if HealthcareProvider.objects.filter(license_number=attrs['license_number']).exists():
            raise serializers.ValidationError("A provider with this license number already exists")
        
        # Email format validation (additional check)
        email = attrs.get('email', '')
        if not email or '@' not in email:
            raise serializers.ValidationError("Please enter a valid email address")
            
        return attrs

    def create(self, validated_data):
        # Extract provider-specific fields
        provider_fields = {
            'professional_title': validated_data.pop('professional_title'),
            'organization_facility': validated_data.pop('organization_facility'),
            'professional_role': validated_data.pop('professional_role'),
            'license_number': validated_data.pop('license_number'),
            'specialization': validated_data.pop('specialization', ''),
            'additional_information': validated_data.pop('additional_information', ''),
            'years_of_experience': validated_data.pop('years_of_experience', 0),
            'consultation_fee': validated_data.pop('consultation_fee', 0.00),
            'bio': validated_data.pop('bio', ''),
            'hospital_clinic': validated_data.pop('hospital_clinic', ''),
            'address': validated_data.pop('address', ''),
        }
        
        # Remove password confirmation
        validated_data.pop('password_confirm')
        
        # Create user account
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create healthcare provider record
        provider_fields.update({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': str(user.phone_number) if user.phone_number else '',
        })
        
        provider = HealthcareProvider.objects.create(**provider_fields)
        
        return user
        user.save()
        
        # Create healthcare provider record
        provider_fields.update({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': str(user.phone_number) if user.phone_number else '',
        })
        
        provider = HealthcareProvider.objects.create(**provider_fields)
        
        return user


class ProviderProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for healthcare provider profile data
    """
    # Include related user data
    user_id = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='email', read_only=True)
    user_first_name = serializers.CharField(source='first_name', read_only=True) 
    user_last_name = serializers.CharField(source='last_name', read_only=True)
    user_phone_number = serializers.CharField(source='phone_number', read_only=True)
    
    class Meta:
        model = HealthcareProvider
        fields = [
            # Basic information
            'id', 'professional_title', 'first_name', 'last_name', 'email', 'phone_number',
            # Professional information
            'organization_facility', 'professional_role', 'specialization', 
            'license_number', 'license_verified', 'additional_information',
            # Legacy fields
            'hospital_clinic', 'address', 'bio', 'years_of_experience', 'consultation_fee',
            # Status
            'is_active', 'created_at', 'updated_at', 
            # User relationship
            'user_id', 'user_email', 'user_first_name', 'user_last_name', 'user_phone_number'
        ]
        read_only_fields = ['id', 'license_verified', 'created_at', 'updated_at']
        
    def get_user_id(self, obj):
        # Get the corresponding User record
        try:
            from .models import User
            user = User.objects.get(email=obj.email)
            return user.id
        except User.DoesNotExist:
            return None
