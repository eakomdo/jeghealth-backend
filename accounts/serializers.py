from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, Role, UserRole


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
