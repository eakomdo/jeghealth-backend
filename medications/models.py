from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()


class MedicationCategory(models.Model):
    """Medication categories for organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medication_categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Medication(models.Model):
    """Medication/drug information"""
    
    FORM_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('liquid', 'Liquid/Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream/Ointment'),
        ('inhaler', 'Inhaler'),
        ('drops', 'Drops'),
        ('patch', 'Patch'),
        ('suppository', 'Suppository'),
        ('powder', 'Powder'),
        ('gel', 'Gel'),
        ('spray', 'Spray'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    brand_name = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(MedicationCategory, on_delete=models.SET_NULL, null=True, blank=True)
    form = models.CharField(max_length=20, choices=FORM_CHOICES, default='tablet')
    strength = models.CharField(max_length=100, help_text="e.g., 500mg, 10ml, 2.5mg/ml")
    manufacturer = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    interactions = models.TextField(blank=True)
    storage_instructions = models.TextField(blank=True)
    requires_prescription = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medications'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['generic_name']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.strength})"


class UserMedication(models.Model):
    """User's prescribed medications"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('discontinued', 'Discontinued'),
    ]

    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_times_daily', 'Three Times Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('every_4_hours', 'Every 4 Hours'),
        ('every_6_hours', 'Every 6 Hours'),
        ('every_8_hours', 'Every 8 Hours'),
        ('every_12_hours', 'Every 12 Hours'),
        ('as_needed', 'As Needed'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medications')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100, help_text="e.g., 1 tablet, 5ml, 2 capsules")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once_daily')
    frequency_custom = models.CharField(max_length=200, blank=True, help_text="Custom frequency description")
    
    # Prescription details
    prescribed_by = models.CharField(max_length=200, blank=True, help_text="Doctor's name")
    prescribed_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    
    # Instructions
    instructions = models.TextField(blank=True, help_text="Special instructions (with food, before bed, etc.)")
    purpose = models.TextField(blank=True, help_text="Reason for taking this medication")
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    total_quantity = models.PositiveIntegerField(null=True, blank=True, help_text="Total pills/doses prescribed")
    remaining_quantity = models.PositiveIntegerField(null=True, blank=True, help_text="Remaining pills/doses")
    refills_remaining = models.PositiveIntegerField(default=0)
    
    # Reminders
    reminder_enabled = models.BooleanField(default=True)
    reminder_times = models.JSONField(default=list, help_text="List of reminder times (e.g., ['08:00', '20:00'])")
    
    # Notes and tracking
    notes = models.TextField(blank=True)
    side_effects_experienced = models.TextField(blank=True)
    effectiveness_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Effectiveness rating from 1-5"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_medications'
        ordering = ['-start_date', 'medication__name']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['status', 'start_date']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.medication.name} ({self.dosage})"

    @property
    def is_active(self):
        """Check if medication is currently active"""
        if self.status != 'active':
            return False
        
        today = timezone.now().date()
        if self.end_date and today > self.end_date:
            return False
            
        return True

    @property
    def is_expired(self):
        """Check if medication has expired"""
        if not self.end_date:
            return False
        return timezone.now().date() > self.end_date

    @property
    def days_remaining(self):
        """Calculate days remaining for medication"""
        if not self.end_date:
            return None
        
        today = timezone.now().date()
        if today >= self.end_date:
            return 0
            
        return (self.end_date - today).days

    @property
    def needs_refill(self):
        """Check if medication needs refill"""
        if not self.remaining_quantity:
            return False
        return self.remaining_quantity <= 7  # Alert when 7 or fewer doses remain

    def update_quantity(self, doses_taken):
        """Update remaining quantity after taking doses"""
        if self.remaining_quantity is not None:
            self.remaining_quantity = max(0, self.remaining_quantity - doses_taken)
            self.save(update_fields=['remaining_quantity', 'updated_at'])


class MedicationLog(models.Model):
    """Log of medication intake"""
    
    STATUS_CHOICES = [
        ('taken', 'Taken'),
        ('missed', 'Missed'),
        ('skipped', 'Skipped'),
        ('partial', 'Partial Dose'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_medication = models.ForeignKey(UserMedication, on_delete=models.CASCADE, related_name='logs')
    scheduled_time = models.DateTimeField()
    actual_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='taken')
    dosage_taken = models.CharField(max_length=100, blank=True, help_text="Actual dosage taken if different")
    notes = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    
    # Location tracking (optional)
    location = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medication_logs'
        ordering = ['-scheduled_time']
        indexes = [
            models.Index(fields=['user_medication', 'scheduled_time']),
            models.Index(fields=['status', 'scheduled_time']),
        ]

    def __str__(self):
        return f"{self.user_medication.medication.name} - {self.scheduled_time.strftime('%Y-%m-%d %H:%M')} ({self.status})"

    @property
    def is_on_time(self):
        """Check if medication was taken on time (within 30 minutes)"""
        if not self.actual_time or self.status != 'taken':
            return False
        
        time_diff = abs((self.actual_time - self.scheduled_time).total_seconds() / 60)
        return time_diff <= 30  # Within 30 minutes

    @property
    def is_late(self):
        """Check if medication was taken late"""
        if not self.actual_time or self.status != 'taken':
            return False
        
        return self.actual_time > self.scheduled_time

    @property
    def delay_minutes(self):
        """Calculate delay in minutes (positive for late, negative for early)"""
        if not self.actual_time:
            return None
        
        return int((self.actual_time - self.scheduled_time).total_seconds() / 60)


class MedicationReminder(models.Model):
    """Medication reminder settings"""
    
    REMINDER_TYPE_CHOICES = [
        ('time', 'Time-based'),
        ('meal', 'Meal-based'),
        ('activity', 'Activity-based'),
        ('symptom', 'Symptom-based'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_medication = models.ForeignKey(UserMedication, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPE_CHOICES, default='time')
    reminder_time = models.TimeField(null=True, blank=True)
    reminder_text = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Advanced reminder settings
    snooze_duration_minutes = models.PositiveIntegerField(default=5)
    advance_notice_minutes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medication_reminders'
        ordering = ['reminder_time']

    def __str__(self):
        return f"{self.user_medication.medication.name} - {self.reminder_time}"


class MedicationInteraction(models.Model):
    """Track potential medication interactions"""
    
    SEVERITY_CHOICES = [
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('severe', 'Severe'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medication_interactions')
    medication1 = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='interactions_as_med1')
    medication2 = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='interactions_as_med2')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='minor')
    description = models.TextField()
    recommendation = models.TextField(blank=True)
    is_dismissed = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medication_interactions'
        unique_together = ['user', 'medication1', 'medication2']
        ordering = ['-severity', '-created_at']

    def __str__(self):
        return f"{self.medication1.name} + {self.medication2.name} ({self.severity})"
