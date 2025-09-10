from django.db import models
import uuid


class HealthcareProvider(models.Model):
    """Healthcare provider/doctor model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    
    # Many-to-many relationship with hospitals
    hospitals = models.ManyToManyField('hospitals.Hospital', related_name='doctors', blank=True)
    
    # Keep the old field for backward compatibility, but make it optional
    hospital_clinic = models.CharField(max_length=200, blank=True, help_text="Legacy field - use hospitals relationship instead")
    
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'healthcare_providers'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialization}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
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
