from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, Role, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin interface.
    """
    list_display = [
        'email', 'username', 'first_name', 'last_name', 
        'is_email_verified', 'is_phone_verified', 'is_staff', 'is_active',
        'date_joined'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 'is_email_verified', 
        'is_phone_verified', 'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'phone_number', 'date_of_birth',
                'profile_image'
            )
        }),
        (_('Emergency Contact'), {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            ),
        }),
        (_('Verification Status'), {
            'fields': ('is_email_verified', 'is_phone_verified'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile.
    """
    model = UserProfile
    can_delete = False
    verbose_name = _('Profile')
    verbose_name_plural = _('Profile')
    
    fieldsets = (
        (_('Physical Information'), {
            'fields': ('gender', 'height', 'weight', 'blood_type')
        }),
        (_('Medical Information'), {
            'fields': ('medical_conditions', 'current_medications', 'allergies'),
            'classes': ('collapse',)
        }),
        (_('Health & Fitness'), {
            'fields': ('health_goals', 'activity_level'),
            'classes': ('collapse',)
        }),
        (_('Notification Preferences'), {
            'fields': ('email_notifications', 'push_notifications', 'health_reminders'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    UserProfile admin interface.
    """
    list_display = [
        'user', 'gender', 'height', 'weight', 'blood_type', 
        'activity_level', 'created_at'
    ]
    list_filter = ['gender', 'blood_type', 'activity_level', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Physical Information'), {
            'fields': ('gender', 'height', 'weight', 'blood_type')
        }),
        (_('Medical Information'), {
            'fields': ('medical_conditions', 'current_medications', 'allergies'),
            'classes': ('collapse',)
        }),
        (_('Health & Fitness'), {
            'fields': ('health_goals', 'activity_level'),
        }),
        (_('Notification Preferences'), {
            'fields': ('email_notifications', 'push_notifications', 'health_reminders'),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Role admin interface.
    """
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('name', 'description', 'is_active')}),
        (_('Permissions'), {'fields': ('permissions',)}),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    UserRole admin interface.
    """
    list_display = ['user', 'role', 'assigned_at', 'assigned_by']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'role__name']
    readonly_fields = ['assigned_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'role', 'assigned_by')}),
        (_('Assignment Info'), {'fields': ('assigned_at',)}),
    )


# Customize admin site
admin.site.site_header = "JEGHealth Administration"
admin.site.site_title = "JEGHealth Admin"
admin.site.index_title = "Welcome to JEGHealth Administration"
