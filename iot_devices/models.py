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


class DeviceScanSession(models.Model):
    """
    Model to track device scanning sessions for iOS device detection
    """
    SCAN_TYPE_CHOICES = [
        ('BLUETOOTH', _('Bluetooth Scan')),
        ('WIFI', _('WiFi Scan')),
        ('COMBINED', _('Combined Scan')),
    ]
    
    STATUS_CHOICES = [
        ('INITIATED', _('Initiated')),
        ('SCANNING', _('Scanning')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('TIMEOUT', _('Timeout')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_scan_sessions'
    )
    scan_type = models.CharField(
        _('Scan Type'),
        max_length=20,
        choices=SCAN_TYPE_CHOICES
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='INITIATED'
    )
    scan_duration = models.IntegerField(
        _('Scan Duration (seconds)'),
        default=30,
        help_text=_('Duration of the scan in seconds')
    )
    devices_found = models.IntegerField(
        _('Devices Found'),
        default=0
    )
    ios_devices_found = models.IntegerField(
        _('iOS Devices Found'),
        default=0
    )
    scan_results = models.JSONField(
        _('Scan Results'),
        default=dict,
        help_text=_('Raw scan results data')
    )
    error_message = models.TextField(
        _('Error Message'),
        blank=True,
        help_text=_('Error message if scan failed')
    )
    initiated_at = models.DateTimeField(_('Initiated At'), auto_now_add=True)
    completed_at = models.DateTimeField(_('Completed At'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Device Scan Session')
        verbose_name_plural = _('Device Scan Sessions')
        ordering = ['-initiated_at']
    
    def __str__(self):
        return f"{self.scan_type} scan by {self.user.email} - {self.status}"


class DetectedDevice(models.Model):
    """
    Model to store detected devices from Bluetooth/WiFi scans
    """
    DEVICE_TYPE_CHOICES = [
        ('IOS_PHONE', _('iOS Phone')),
        ('IOS_TABLET', _('iOS Tablet')),
        ('IOS_WATCH', _('Apple Watch')),
        ('IOS_AIRPODS', _('AirPods')),
        ('IOS_UNKNOWN', _('Unknown iOS Device')),
        ('ANDROID', _('Android Device')),
        ('WINDOWS', _('Windows Device')),
        ('MAC', _('Mac Device')),
        ('UNKNOWN', _('Unknown Device')),
    ]
    
    CONNECTION_TYPE_CHOICES = [
        ('BLUETOOTH', _('Bluetooth')),
        ('WIFI', _('WiFi')),
        ('BOTH', _('Both')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan_session = models.ForeignKey(
        DeviceScanSession,
        on_delete=models.CASCADE,
        related_name='detected_devices'
    )
    device_name = models.CharField(
        _('Device Name'),
        max_length=100,
        blank=True,
        help_text=_('Device name if available')
    )
    device_type = models.CharField(
        _('Device Type'),
        max_length=20,
        choices=DEVICE_TYPE_CHOICES,
        default='UNKNOWN'
    )
    mac_address = models.CharField(
        _('MAC Address'),
        max_length=17,
        blank=True,
        help_text=_('Device MAC address if available')
    )
    bluetooth_address = models.CharField(
        _('Bluetooth Address'),
        max_length=17,
        blank=True,
        help_text=_('Bluetooth address if available')
    )
    signal_strength = models.IntegerField(
        _('Signal Strength (dBm)'),
        blank=True,
        null=True,
        help_text=_('Signal strength in dBm')
    )
    connection_type = models.CharField(
        _('Connection Type'),
        max_length=20,
        choices=CONNECTION_TYPE_CHOICES
    )
    manufacturer = models.CharField(
        _('Manufacturer'),
        max_length=50,
        blank=True,
        help_text=_('Device manufacturer if detected')
    )
    ios_version = models.CharField(
        _('iOS Version'),
        max_length=20,
        blank=True,
        help_text=_('iOS version if detected')
    )
    device_model = models.CharField(
        _('Device Model'),
        max_length=50,
        blank=True,
        help_text=_('Device model if detected')
    )
    is_paired = models.BooleanField(
        _('Is Paired'),
        default=False,
        help_text=_('Whether device is paired with scanning device')
    )
    is_ios_device = models.BooleanField(
        _('Is iOS Device'),
        default=False,
        help_text=_('Whether this is confirmed to be an iOS device')
    )
    additional_info = models.JSONField(
        _('Additional Info'),
        default=dict,
        help_text=_('Additional device information')
    )
    first_seen = models.DateTimeField(_('First Seen'), auto_now_add=True)
    last_seen = models.DateTimeField(_('Last Seen'), auto_now=True)
    
    class Meta:
        verbose_name = _('Detected Device')
        verbose_name_plural = _('Detected Devices')
        ordering = ['-last_seen']
        unique_together = ['scan_session', 'mac_address', 'bluetooth_address']
    
    def __str__(self):
        return f"{self.device_name or 'Unknown'} ({self.device_type}) - {self.connection_type}"


class iOSDeviceProfile(models.Model):
    """
    Model to store iOS device profiles for health data integration
    """
    DEVICE_STATUS_CHOICES = [
        ('DISCOVERED', _('Discovered')),
        ('PAIRED', _('Paired')),
        ('CONNECTED', _('Connected')),
        ('SYNCING', _('Syncing')),
        ('DISCONNECTED', _('Disconnected')),
        ('ERROR', _('Error')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ios_device_profiles'
    )
    detected_device = models.OneToOneField(
        DetectedDevice,
        on_delete=models.CASCADE,
        related_name='ios_profile',
        blank=True,
        null=True
    )
    device_name = models.CharField(
        _('Device Name'),
        max_length=100,
        help_text=_('User-friendly device name')
    )
    device_identifier = models.CharField(
        _('Device Identifier'),
        max_length=100,
        unique=True,
        help_text=_('Unique identifier for the iOS device')
    )
    device_model = models.CharField(
        _('Device Model'),
        max_length=50,
        blank=True
    )
    ios_version = models.CharField(
        _('iOS Version'),
        max_length=20,
        blank=True
    )
    health_app_version = models.CharField(
        _('Health App Version'),
        max_length=20,
        blank=True
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=DEVICE_STATUS_CHOICES,
        default='DISCOVERED'
    )
    last_sync = models.DateTimeField(
        _('Last Sync'),
        blank=True,
        null=True
    )
    sync_frequency = models.IntegerField(
        _('Sync Frequency (minutes)'),
        default=60,
        help_text=_('How often to sync data in minutes')
    )
    available_health_data = models.JSONField(
        _('Available Health Data'),
        default=list,
        help_text=_('List of health data types available from this device')
    )
    permissions_granted = models.JSONField(
        _('Permissions Granted'),
        default=dict,
        help_text=_('Health data permissions granted by user')
    )
    sync_settings = models.JSONField(
        _('Sync Settings'),
        default=dict,
        help_text=_('Device-specific sync settings')
    )
    is_primary_device = models.BooleanField(
        _('Is Primary Device'),
        default=False,
        help_text=_('Whether this is the user\'s primary health device')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('iOS Device Profile')
        verbose_name_plural = _('iOS Device Profiles')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.device_name} ({self.user.email}) - {self.status}"
