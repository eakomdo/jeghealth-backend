from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model for JEGHealth application.
    Extends Django's AbstractUser to include additional fields.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone_number = PhoneNumberField(_('phone number'), blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    profile_image = models.ImageField(
        _('profile image'), 
        upload_to='user_profiles/',  # Store in static/user_profiles/
        blank=True, 
        null=True
    )
    profile_image_path = models.CharField(
        _('profile image path'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Stores the path of the uploaded profile image.')
    )
    
    # Medical information
    emergency_contact_name = models.CharField(
        _('emergency contact name'), 
        max_length=100, 
        blank=True
    )
    emergency_contact_phone = PhoneNumberField(
        _('emergency contact phone'), 
        blank=True, 
        null=True
    )
    
    # System fields
    is_email_verified = models.BooleanField(_('email verified'), default=False)
    is_phone_verified = models.BooleanField(_('phone verified'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'accounts_user'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return self.get_full_name()

    def save(self, *args, **kwargs):
        # Automatically update profile_image_path when profile_image is set
        if self.profile_image:
            self.profile_image_path = self.profile_image.name
        else:
            self.profile_image_path = None
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Extended user profile information for health data.
    """
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('UNKNOWN', _('Unknown')),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Personal information
    gender = models.CharField(
        _('gender'), 
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True
    )
    height = models.FloatField(
        _('height (cm)'), 
        blank=True, 
        null=True,
        help_text=_('Height in centimeters')
    )
    weight = models.FloatField(
        _('weight (kg)'), 
        blank=True, 
        null=True,
        help_text=_('Weight in kilograms')
    )
    blood_type = models.CharField(
        _('blood type'), 
        max_length=10, 
        choices=BLOOD_TYPE_CHOICES, 
        default='UNKNOWN'
    )
    
    # Medical information
    medical_conditions = models.TextField(
        _('medical conditions'), 
        blank=True,
        help_text=_('List any chronic conditions, allergies, or important medical history')
    )
    current_medications = models.TextField(
        _('current medications'), 
        blank=True,
        help_text=_('List current medications and dosages')
    )
    allergies = models.TextField(
        _('allergies'), 
        blank=True,
        help_text=_('List any known allergies')
    )
    
    # Health goals and preferences
    health_goals = models.TextField(
        _('health goals'), 
        blank=True,
        help_text=_('Personal health and fitness goals')
    )
    
    # Activity level
    ACTIVITY_LEVEL_CHOICES = [
        ('SEDENTARY', _('Sedentary (little to no exercise)')),
        ('LIGHT', _('Light (exercise 1-3 times/week)')),
        ('MODERATE', _('Moderate (exercise 4-5 times/week)')),
        ('ACTIVE', _('Active (daily exercise or intense exercise 3-4 times/week)')),
        ('VERY_ACTIVE', _('Very Active (intense exercise 6-7 times/week)')),
    ]
    
    activity_level = models.CharField(
        _('activity level'), 
        max_length=15, 
        choices=ACTIVITY_LEVEL_CHOICES, 
        default='MODERATE'
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        _('email notifications'), 
        default=True
    )
    push_notifications = models.BooleanField(
        _('push notifications'), 
        default=True
    )
    health_reminders = models.BooleanField(
        _('health reminders'), 
        default=True
    )
    
    # System fields
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        db_table = 'accounts_userprofile'
    
    def __str__(self):
        return f"{self.user.full_name}'s Profile"
    
    @property
    def bmi(self):
        """Calculate BMI if height and weight are available."""
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to meters
            return round(self.weight / (height_m ** 2), 2)
        return None


class Role(models.Model):
    """
    Role model for user permission management.
    Based on the role system seen in your mobile app AuthContext.
    """
    name = models.CharField(_('role name'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True)
    permissions = models.JSONField(
        _('permissions'), 
        default=dict,
        help_text=_('JSON object containing permission settings')
    )
    is_active = models.BooleanField(_('is active'), default=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        db_table = 'accounts_role'
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Many-to-many relationship between users and roles.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role, 
        on_delete=models.CASCADE, 
        related_name='role_users'
    )
    assigned_at = models.DateTimeField(_('assigned at'), auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_roles'
    )
    
    class Meta:
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')
        db_table = 'accounts_userrole'
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
