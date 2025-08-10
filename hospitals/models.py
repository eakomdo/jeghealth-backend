import uuid
from django.db import models

class Hospital(models.Model):
    """Hospital/Healthcare Facility model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='United States')
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Hospital Classification
    HOSPITAL_TYPE_CHOICES = [
        ('general', 'General Hospital'),
        ('specialty', 'Specialty Hospital'),
        ('teaching', 'Teaching Hospital'),
        ('clinic', 'Clinic'),
        ('urgent_care', 'Urgent Care'),
        ('emergency', 'Emergency Center'),
        ('outpatient', 'Outpatient Facility'),
    ]
    hospital_type = models.CharField(max_length=20, choices=HOSPITAL_TYPE_CHOICES, default='general')
    
    # Services and Features
    emergency_services = models.BooleanField(default=False)
    has_icu = models.BooleanField(default=False)
    has_surgery = models.BooleanField(default=False)
    has_maternity = models.BooleanField(default=False)
    has_pediatrics = models.BooleanField(default=False)
    
    # Operational Info
    bed_count = models.IntegerField(null=True, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"

class Department(models.Model):
    """Hospital departments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Department types
    DEPARTMENT_CHOICES = [
        ('emergency', 'Emergency Department'),
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('maternity', 'Maternity'),
        ('surgery', 'Surgery'),
        ('radiology', 'Radiology'),
        ('laboratory', 'Laboratory'),
        ('pharmacy', 'Pharmacy'),
        ('icu', 'Intensive Care Unit'),
        ('oncology', 'Oncology'),
        ('psychiatry', 'Psychiatry'),
        ('dermatology', 'Dermatology'),
        ('ophthalmology', 'Ophthalmology'),
        ('ent', 'ENT (Ear, Nose, Throat)'),
        ('other', 'Other'),
    ]
    department_type = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='other')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['hospital', 'name']
        ordering = ['name']
        
    def __str__(self):
        return f"{self.hospital.name} - {self.name}"
