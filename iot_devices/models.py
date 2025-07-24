from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class IoTDevice(models.Model):
    """
    Model for IoT devices that can send health data.
    """
    DEVICE_TYPE_CHOICES = [
        ('SMARTWATCH', _('Smart Watch')),
        ('FITNESS_TRACKER', _('Fitness Tracker')),
        ('BLOOD_PRESSURE_MONITOR', _('Blood Pressure Monitor')),
        ('GLUCOSE_METER', _('Glucose Meter')),
        ('SCALE', _('Smart Scale')),
        ('THERMOMETER', _('Digital Thermometer')),
        ('PULSE_OXIMETER', _('Pulse Oximeter')),
        ('ECG_MONITOR', _('ECG Monitor')),
        ('SLEEP_TRACKER', _('Sleep Tracker')),
        ('OTHER', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', _('Active')),
        ('INACTIVE', _('Inactive')),
        ('MAINTENANCE', _('Maintenance')),
        ('ERROR', _('Error')),
    ]
    
    # Unique device identifier
    device_id = models.UUIDField(
        _('Device ID'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    
    # Device information
    name = models.CharField(
        _('Device Name'),
        max_length=100,
        help_text=_('Human-readable name for the device')
    )
    
    device_type = models.CharField(
        _('Device Type'),
        max_length=25,
        choices=DEVICE_TYPE_CHOICES
    )
    
    manufacturer = models.CharField(
        _('Manufacturer'),
        max_length=100,
        blank=True
    )
    
    model = models.CharField(
        _('Model'),
        max_length=100,
        blank=True
    )
    
    firmware_version = models.CharField(
        _('Firmware Version'),
        max_length=50,
        blank=True
    )
    
    # Owner and registration
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='iot_devices',
        verbose_name=_('Owner')
    )
    
    # Device status and connectivity
    status = models.CharField(
        _('Status'),
        max_length=15,
        choices=STATUS_CHOICES,
        default='INACTIVE'
    )
    
    is_verified = models.BooleanField(
        _('Is Verified'),
        default=False,
        help_text=_('Whether the device has been verified and authorized')
    )
    
    # Connectivity information
    last_seen = models.DateTimeField(
        _('Last Seen'),
        blank=True,
        null=True,
        help_text=_('Last time the device sent data')
    )
    
    api_key = models.CharField(
        _('API Key'),
        max_length=64,
        unique=True,
        blank=True,
        help_text=_('API key for device authentication')
    )
    
    # Device capabilities
    supported_metrics = models.JSONField(
        _('Supported Metrics'),
        default=list,
        help_text=_('List of health metrics this device can measure')
    )
    
    # Calibration and accuracy
    calibration_date = models.DateTimeField(
        _('Calibration Date'),
        blank=True,
        null=True,
        help_text=_('Last calibration date')
    )
    
    accuracy_score = models.FloatField(
        _('Accuracy Score'),
        default=0.95,
        help_text=_('Device accuracy score (0-1)')
    )
    
    # Configuration
    configuration = models.JSONField(
        _('Configuration'),
        default=dict,
        help_text=_('Device-specific configuration settings')
    )
    
    # Location (optional)
    location = models.CharField(
        _('Location'),
        max_length=100,
        blank=True,
        help_text=_('Physical location of the device')
    )
    
    # System fields
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('IoT Device')
        verbose_name_plural = _('IoT Devices')
        db_table = 'iot_devices_iotdevice'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'device_type']),
            models.Index(fields=['status', 'is_verified']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()}) - {self.owner.email}"
    
    def save(self, *args, **kwargs):
        # Generate API key if not provided
        if not self.api_key:
            self.api_key = self.generate_api_key()
        super().save(*args, **kwargs)
    
    def generate_api_key(self):
        """Generate a unique API key for the device."""
        import secrets
        return secrets.token_urlsafe(48)
    
    @property
    def is_online(self):
        """Check if device is online (sent data in last 5 minutes)."""
        if not self.last_seen:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        return timezone.now() - self.last_seen < timedelta(minutes=5)
    
    def can_measure_metric(self, metric_type):
        """Check if device can measure a specific metric type."""
        return metric_type in self.supported_metrics


class DeviceDataBatch(models.Model):
    """
    Model for batch data uploads from IoT devices.
    """
    device = models.ForeignKey(
        IoTDevice,
        on_delete=models.CASCADE,
        related_name='data_batches',
        verbose_name=_('Device')
    )
    
    batch_id = models.UUIDField(
        _('Batch ID'),
        default=uuid.uuid4,
        unique=True
    )
    
    # Batch metadata
    data_count = models.IntegerField(
        _('Data Count'),
        default=0,
        help_text=_('Number of data points in this batch')
    )
    
    batch_start_time = models.DateTimeField(
        _('Batch Start Time'),
        help_text=_('Earliest timestamp in the batch')
    )
    
    batch_end_time = models.DateTimeField(
        _('Batch End Time'),
        help_text=_('Latest timestamp in the batch')
    )
    
    # Processing status
    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('PARTIAL', _('Partially Processed')),
    ]
    
    status = models.CharField(
        _('Status'),
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    processed_count = models.IntegerField(
        _('Processed Count'),
        default=0,
        help_text=_('Number of successfully processed data points')
    )
    
    error_count = models.IntegerField(
        _('Error Count'),
        default=0,
        help_text=_('Number of data points that failed processing')
    )
    
    # Raw data and processing
    raw_data = models.JSONField(
        _('Raw Data'),
        help_text=_('Raw data from the device')
    )
    
    processing_errors = models.JSONField(
        _('Processing Errors'),
        default=list,
        help_text=_('List of processing errors')
    )
    
    # Checksums for data integrity
    checksum = models.CharField(
        _('Checksum'),
        max_length=64,
        blank=True,
        help_text=_('Data integrity checksum')
    )
    
    # System fields
    received_at = models.DateTimeField(_('Received At'), auto_now_add=True)
    processed_at = models.DateTimeField(_('Processed At'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Device Data Batch')
        verbose_name_plural = _('Device Data Batches')
        db_table = 'iot_devices_devicedatabatch'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['device', 'status']),
            models.Index(fields=['batch_start_time', 'batch_end_time']),
        ]
    
    def __str__(self):
        return f"Batch {self.batch_id} from {self.device.name} ({self.data_count} points)"


class DeviceAlert(models.Model):
    """
    Model for device-related alerts and notifications.
    """
    ALERT_TYPE_CHOICES = [
        ('OFFLINE', _('Device Offline')),
        ('LOW_BATTERY', _('Low Battery')),
        ('CALIBRATION_DUE', _('Calibration Due')),
        ('DATA_ANOMALY', _('Data Anomaly')),
        ('SYNC_ERROR', _('Sync Error')),
        ('FIRMWARE_UPDATE', _('Firmware Update Available')),
        ('SENSOR_ERROR', _('Sensor Error')),
        ('MAINTENANCE_DUE', _('Maintenance Due')),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', _('Low')),
        ('MEDIUM', _('Medium')),
        ('HIGH', _('High')),
        ('CRITICAL', _('Critical')),
    ]
    
    device = models.ForeignKey(
        IoTDevice,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name=_('Device')
    )
    
    alert_type = models.CharField(
        _('Alert Type'),
        max_length=20,
        choices=ALERT_TYPE_CHOICES
    )
    
    severity = models.CharField(
        _('Severity'),
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='MEDIUM'
    )
    
    title = models.CharField(
        _('Title'),
        max_length=200
    )
    
    message = models.TextField(
        _('Message'),
        help_text=_('Detailed alert message')
    )
    
    # Alert status
    is_active = models.BooleanField(
        _('Is Active'),
        default=True
    )
    
    is_acknowledged = models.BooleanField(
        _('Is Acknowledged'),
        default=False
    )
    
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='acknowledged_alerts',
        verbose_name=_('Acknowledged By')
    )
    
    acknowledged_at = models.DateTimeField(
        _('Acknowledged At'),
        blank=True,
        null=True
    )
    
    # Resolution
    is_resolved = models.BooleanField(
        _('Is Resolved'),
        default=False
    )
    
    resolved_at = models.DateTimeField(
        _('Resolved At'),
        blank=True,
        null=True
    )
    
    resolution_notes = models.TextField(
        _('Resolution Notes'),
        blank=True,
        help_text=_('Notes about how the alert was resolved')
    )
    
    # System fields
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Device Alert')
        verbose_name_plural = _('Device Alerts')
        db_table = 'iot_devices_devicealert'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', 'is_active', 'severity']),
            models.Index(fields=['alert_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.device.name} ({self.get_severity_display()})"
