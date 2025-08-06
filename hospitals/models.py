from django.db import models
import uuid


class Hospital(models.Model):
    """Hospital/Clinic model"""
    
    HOSPITAL_TYPES = [
        ('public', 'Public Hospital'),
        ('private', 'Private Hospital'),
        ('clinic', 'Private Clinic'),
        ('specialized', 'Specialized Center'),
        ('military', 'Military Hospital'),
        ('university', 'University Hospital'),
        ('community', 'Community Health Center'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    hospital_type = models.CharField(max_length=20, choices=HOSPITAL_TYPES, default='private')
    address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Ghana')
    
    # Contact information
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Services and facilities
    description = models.TextField(blank=True, help_text="Brief description of the hospital")
    specialties = models.TextField(blank=True, help_text="Comma-separated list of specialties offered")
    facilities = models.TextField(blank=True, help_text="Available facilities (ICU, Emergency, etc.)")
    
    # Operational details
    established_year = models.PositiveIntegerField(null=True, blank=True)
    bed_capacity = models.PositiveIntegerField(null=True, blank=True)
    emergency_services = models.BooleanField(default=False)
    appointment_booking_available = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hospitals'
        ordering = ['name']
        indexes = [
            models.Index(fields=['city', 'region']),
            models.Index(fields=['hospital_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.city})"

    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.region}, {self.country}"
    
    @property
    def specialties_list(self):
        """Return specialties as a list"""
        if self.specialties:
            return [specialty.strip() for specialty in self.specialties.split(',')]
        return []
