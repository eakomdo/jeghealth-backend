from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class HealthMetric(models.Model):
    """
    Model for storing health metric readings.
    Based on the metric types seen in your mobile app HealthMetricsScreen.
    """
    METRIC_TYPE_CHOICES = [
        ('blood_pressure', _('Blood Pressure')),
        ('heart_rate', _('Heart Rate')),
        ('weight', _('Weight')),
        ('blood_sugar', _('Blood Sugar')),
        ('temperature', _('Temperature')),
        ('oxygen_saturation', _('Oxygen Saturation')),
        ('steps', _('Steps')),
        ('sleep_hours', _('Sleep Hours')),
        ('calories_burned', _('Calories Burned')),
        ('body_fat_percentage', _('Body Fat Percentage')),
        ('muscle_mass', _('Muscle Mass')),
        ('bmi', _('BMI')),
    ]
    
    UNIT_CHOICES = [
        ('mmHg', _('mmHg')),
        ('bpm', _('bpm')),
        ('kg', _('kg')),
        ('lbs', _('lbs')),
        ('mg/dL', _('mg/dL')),
        ('mmol/L', _('mmol/L')),
        ('°C', _('°C')),
        ('°F', _('°F')),
        ('%', _('%')),
        ('steps', _('steps')),
        ('hours', _('hours')),
        ('calories', _('calories')),
        ('kg/m²', _('kg/m²')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_metrics',
        verbose_name=_('User')
    )
    
    metric_type = models.CharField(
        _('Metric Type'),
        max_length=20,
        choices=METRIC_TYPE_CHOICES
    )
    
    value = models.FloatField(
        _('Value'),
        validators=[MinValueValidator(0)]
    )
    
    unit = models.CharField(
        _('Unit'),
        max_length=10,
        choices=UNIT_CHOICES
    )
    
    # Special fields for blood pressure
    systolic_value = models.FloatField(
        _('Systolic Value'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(300)]
    )
    
    diastolic_value = models.FloatField(
        _('Diastolic Value'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(200)]
    )
    
    recorded_at = models.DateTimeField(
        _('Recorded At'),
        help_text=_('When this reading was taken')
    )
    
    is_manual_entry = models.BooleanField(
        _('Manual Entry'),
        default=True,
        help_text=_('Whether this was manually entered or from a device')
    )
    
    # Device information (for IoT integration)
    device = models.ForeignKey(
        'iot_devices.IoTDevice',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='health_metrics',
        verbose_name=_('Device')
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        help_text=_('Additional notes about this reading')
    )
    
    # Data quality indicators
    confidence_score = models.FloatField(
        _('Confidence Score'),
        default=1.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text=_('Confidence in reading accuracy (0-1)')
    )
    
    is_anomaly = models.BooleanField(
        _('Is Anomaly'),
        default=False,
        help_text=_('Whether this reading is flagged as unusual')
    )
    
    # System fields
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Health Metric')
        verbose_name_plural = _('Health Metrics')
        db_table = 'health_metrics_healthmetric'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['user', 'metric_type', '-recorded_at']),
            models.Index(fields=['user', '-recorded_at']),
            models.Index(fields=['metric_type', '-recorded_at']),
        ]
    
    def __str__(self):
        if self.metric_type == 'blood_pressure':
            return f"{self.user.email} - {self.get_metric_type_display()}: {self.systolic_value}/{self.diastolic_value} {self.unit} ({self.recorded_at.date()})"
        return f"{self.user.email} - {self.get_metric_type_display()}: {self.value} {self.unit} ({self.recorded_at.date()})"
    
    @property
    def display_value(self):
        """Return a formatted display value for the metric."""
        if self.metric_type == 'blood_pressure':
            return f"{self.systolic_value}/{self.diastolic_value}"
        return str(self.value)
    
    def is_normal_range(self):
        """
        Check if the metric value is within normal ranges.
        Returns None if no normal range is defined for this metric type.
        """
        normal_ranges = {
            'blood_pressure': {
                'systolic_min': 90, 'systolic_max': 140,
                'diastolic_min': 60, 'diastolic_max': 90
            },
            'heart_rate': {'min': 60, 'max': 100},
            'temperature': {'min': 36.1, 'max': 37.2},  # Celsius
            'oxygen_saturation': {'min': 95, 'max': 100},
            'blood_sugar': {'min': 70, 'max': 140},  # mg/dL fasting
        }
        
        if self.metric_type not in normal_ranges:
            return None
        
        ranges = normal_ranges[self.metric_type]
        
        if self.metric_type == 'blood_pressure':
            systolic_normal = ranges['systolic_min'] <= self.systolic_value <= ranges['systolic_max']
            diastolic_normal = ranges['diastolic_min'] <= self.diastolic_value <= ranges['diastolic_max']
            return systolic_normal and diastolic_normal
        else:
            return ranges['min'] <= self.value <= ranges['max']


class HealthMetricTarget(models.Model):
    """
    User-defined targets/goals for health metrics.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_targets',
        verbose_name=_('User')
    )
    
    metric_type = models.CharField(
        _('Metric Type'),
        max_length=20,
        choices=HealthMetric.METRIC_TYPE_CHOICES
    )
    
    target_value = models.FloatField(
        _('Target Value'),
        validators=[MinValueValidator(0)]
    )
    
    target_unit = models.CharField(
        _('Target Unit'),
        max_length=10,
        choices=HealthMetric.UNIT_CHOICES
    )
    
    # For blood pressure targets
    target_systolic = models.FloatField(
        _('Target Systolic'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(300)]
    )
    
    target_diastolic = models.FloatField(
        _('Target Diastolic'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(200)]
    )
    
    TARGET_TYPE_CHOICES = [
        ('MAINTAIN', _('Maintain')),
        ('INCREASE', _('Increase')),
        ('DECREASE', _('Decrease')),
        ('RANGE', _('Stay in Range')),
    ]
    
    target_type = models.CharField(
        _('Target Type'),
        max_length=10,
        choices=TARGET_TYPE_CHOICES,
        default='MAINTAIN'
    )
    
    # Range targets
    min_value = models.FloatField(
        _('Minimum Value'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    max_value = models.FloatField(
        _('Maximum Value'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    # Goal timeline
    target_date = models.DateField(
        _('Target Date'),
        blank=True,
        null=True,
        help_text=_('When to achieve this target')
    )
    
    is_active = models.BooleanField(
        _('Is Active'),
        default=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        help_text=_('Additional notes about this target')
    )
    
    # System fields
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Health Metric Target')
        verbose_name_plural = _('Health Metric Targets')
        db_table = 'health_metrics_healthmetrictarget'
        unique_together = ['user', 'metric_type']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_metric_type_display()} Target: {self.target_value} {self.target_unit}"


class HealthMetricSummary(models.Model):
    """
    Daily/weekly/monthly summaries of health metrics for analytics.
    """
    PERIOD_CHOICES = [
        ('DAILY', _('Daily')),
        ('WEEKLY', _('Weekly')),
        ('MONTHLY', _('Monthly')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_summaries',
        verbose_name=_('User')
    )
    
    metric_type = models.CharField(
        _('Metric Type'),
        max_length=20,
        choices=HealthMetric.METRIC_TYPE_CHOICES
    )
    
    period_type = models.CharField(
        _('Period Type'),
        max_length=10,
        choices=PERIOD_CHOICES
    )
    
    period_start = models.DateField(_('Period Start'))
    period_end = models.DateField(_('Period End'))
    
    # Statistical data
    reading_count = models.IntegerField(
        _('Reading Count'),
        default=0
    )
    
    average_value = models.FloatField(
        _('Average Value'),
        blank=True,
        null=True
    )
    
    min_value = models.FloatField(
        _('Minimum Value'),
        blank=True,
        null=True
    )
    
    max_value = models.FloatField(
        _('Maximum Value'),
        blank=True,
        null=True
    )
    
    # Blood pressure specific
    avg_systolic = models.FloatField(
        _('Average Systolic'),
        blank=True,
        null=True
    )
    
    avg_diastolic = models.FloatField(
        _('Average Diastolic'),
        blank=True,
        null=True
    )
    
    # Trends
    trend_direction = models.CharField(
        _('Trend Direction'),
        max_length=10,
        choices=[
            ('UP', _('Increasing')),
            ('DOWN', _('Decreasing')),
            ('STABLE', _('Stable')),
            ('UNKNOWN', _('Unknown')),
        ],
        default='UNKNOWN'
    )
    
    variance = models.FloatField(
        _('Variance'),
        blank=True,
        null=True,
        help_text=_('Statistical variance of readings')
    )
    
    # System fields
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Health Metric Summary')
        verbose_name_plural = _('Health Metric Summaries')
        db_table = 'health_metrics_healthmetricsummary'
        unique_together = ['user', 'metric_type', 'period_type', 'period_start']
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['user', 'metric_type', 'period_type', '-period_start']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_metric_type_display()} {self.get_period_type_display()} ({self.period_start} to {self.period_end})"
