from django.db import models
import uuid


class HealthcareProvider(models.Model):
    """Healthcare provider/doctor model"""
    
    # Professional Title Choices
    PROFESSIONAL_TITLE_CHOICES = [
        ('Dr.', 'Dr. (Doctor)'),
        ('Prof.', 'Prof. (Professor)'),
        ('RN', 'RN (Registered Nurse)'),
        ('LPN', 'LPN (Licensed Practical Nurse)'),
        ('NP', 'NP (Nurse Practitioner)'),
        ('PA', 'PA (Physician Assistant)'),
        ('RPh', 'RPh (Pharmacist)'),
        ('PT', 'PT (Physical Therapist)'),
        ('OT', 'OT (Occupational Therapist)'),
        ('RT', 'RT (Respiratory Therapist)'),
        ('MT', 'MT (Medical Technologist)'),
        ('RD', 'RD (Registered Dietitian)'),
        ('MSW', 'MSW (Medical Social Worker)'),
        ('Mr.', 'Mr.'),
        ('Ms.', 'Ms.'),
        ('Mrs.', 'Mrs.'),
    ]
    
    # Professional Role Choices
    PROFESSIONAL_ROLE_CHOICES = [
        ('Physician', 'Physician'),
        ('Registered Nurse', 'Registered Nurse'),
        ('Specialist', 'Specialist'),
        ('Healthcare Administrator', 'Healthcare Administrator'),
        ('Medical Technician', 'Medical Technician'),
        ('Other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Personal Information
    professional_title = models.CharField(
        max_length=10, 
        choices=PROFESSIONAL_TITLE_CHOICES,
        default='Dr.',
        help_text="Professional title (Dr., RN, etc.)"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Professional Information
    organization_facility = models.CharField(
        max_length=200,
        default='Not Specified',
        help_text="Organization/Facility (General Hospital, Private Practice, etc.)"
    )
    professional_role = models.CharField(
        max_length=50,
        choices=PROFESSIONAL_ROLE_CHOICES,
        default='Other',
        help_text="Primary professional role"
    )
    specialization = models.CharField(max_length=100, blank=True)
    
    # License Information
    license_number = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Professional license number for verification"
    )
    license_verified = models.BooleanField(default=False)
    license_document = models.FileField(
        upload_to='license_documents/', 
        blank=True, 
        null=True,
        help_text="Upload license document for verification"
    )
    
    # Additional Information
    additional_information = models.TextField(
        blank=True,
        help_text="Tell us about your specific IoT monitoring needs or any questions"
    )
    
    # Many-to-many relationship with hospitals
    hospitals = models.ManyToManyField('hospitals.Hospital', related_name='doctors', blank=True)
    
    # Legacy fields (keep for backward compatibility)
    hospital_clinic = models.CharField(max_length=200, blank=True, help_text="Legacy field - use organization_facility instead")
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'healthcare_providers'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.professional_title} {self.first_name} {self.last_name} - {self.professional_role}"

    @property
    def full_name(self):
        return f"{self.professional_title} {self.first_name} {self.last_name}"
    
    @property
    def hospital_names(self):
        """Get comma-separated list of hospital names"""
        return ", ".join([hospital.name for hospital in self.hospitals.all()])
    
    @property
    def primary_hospital(self):
        """Get the first hospital (primary workplace)"""
        return self.hospitals.first()
    
    def get_hospitals_in_city(self, city):
        """Get hospitals where this doctor works in a specific city"""
        return self.hospitals.filter(city__icontains=city)
