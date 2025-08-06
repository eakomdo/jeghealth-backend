from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from providers.models import HealthcareProvider
import uuid

User = get_user_model()


# Remove HealthcareProvider from here - it's now in providers app

class Appointment(models.Model):
    """Appointment model for patient-doctor appointments"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]

    TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('checkup', 'Regular Checkup'),
        ('emergency', 'Emergency'),
        ('surgery', 'Surgery'),
        ('therapy', 'Therapy'),
        ('vaccination', 'Vaccination'),
        ('diagnostic', 'Diagnostic'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    healthcare_provider = models.ForeignKey(HealthcareProvider, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30, validators=[MinValueValidator(15), MaxValueValidator(480)])
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='consultation')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Appointment details
    chief_complaint = models.TextField(help_text="Main reason for the appointment")
    symptoms = models.TextField(blank=True, help_text="Patient's symptoms")
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    # Medical consultation details (filled during/after appointment)
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    prescribed_medications = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)
    next_appointment_recommended = models.BooleanField(default=False)
    
    # Administrative
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('partial', 'Partial'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    
    # Reminders and notifications
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_appointments')

    class Meta:
        db_table = 'appointments'
        ordering = ['appointment_date']
        indexes = [
            models.Index(fields=['patient', 'appointment_date']),
            models.Index(fields=['healthcare_provider', 'appointment_date']),
            models.Index(fields=['status', 'appointment_date']),
        ]

    def __str__(self):
        return f"{self.patient.get_full_name()} - Dr. {self.healthcare_provider.full_name} - {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def end_time(self):
        """Calculate appointment end time"""
        return self.appointment_date + timezone.timedelta(minutes=self.duration_minutes)

    @property
    def is_past(self):
        """Check if appointment is in the past"""
        return self.appointment_date < timezone.now()

    @property
    def is_today(self):
        """Check if appointment is today"""
        return self.appointment_date.date() == timezone.now().date()

    @property
    def is_upcoming(self):
        """Check if appointment is upcoming (within next 7 days)"""
        return timezone.now() <= self.appointment_date <= timezone.now() + timezone.timedelta(days=7)

    def can_be_cancelled(self):
        """Check if appointment can be cancelled (not in past, not completed)"""
        return not self.is_past and self.status not in ['completed', 'cancelled']

    def can_be_rescheduled(self):
        """Check if appointment can be rescheduled"""
        return self.status in ['scheduled', 'confirmed'] and not self.is_past


class AppointmentFile(models.Model):
    """Files attached to appointments (lab results, prescriptions, etc.)"""
    
    FILE_TYPE_CHOICES = [
        ('lab_result', 'Lab Result'),
        ('prescription', 'Prescription'),
        ('medical_image', 'Medical Image'),
        ('report', 'Medical Report'),
        ('insurance', 'Insurance Document'),
        ('referral', 'Referral Letter'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='appointments/files/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='other')
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'appointment_files'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file_name} - {self.appointment}"


class AppointmentRating(models.Model):
    """Patient rating and feedback for appointments"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='rating')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    feedback = models.TextField(blank=True)
    would_recommend = models.BooleanField(default=True)
    punctuality_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    communication_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'appointment_ratings'

    def __str__(self):
        return f"{self.appointment} - {self.rating} stars"
