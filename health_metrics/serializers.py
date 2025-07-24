from rest_framework import serializers
from django.utils import timezone
from .models import HealthMetric, HealthMetricTarget, HealthMetricSummary
from iot_devices.models import IoTDevice


class HealthMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for health metric data.
    Matches the structure used in your mobile app HealthMetricsScreen.
    """
    display_value = serializers.ReadOnlyField()
    is_normal_range = serializers.SerializerMethodField()
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = HealthMetric
        fields = [
            'id', 'metric_type', 'value', 'unit', 'systolic_value', 
            'diastolic_value', 'recorded_at', 'is_manual_entry', 
            'device', 'device_name', 'notes', 'confidence_score', 
            'is_anomaly', 'display_value', 'is_normal_range',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_is_normal_range(self, obj):
        """Get whether the metric is in normal range."""
        return obj.is_normal_range()
    
    def validate(self, attrs):
        """Validate health metric data."""
        metric_type = attrs.get('metric_type')
        value = attrs.get('value')
        systolic_value = attrs.get('systolic_value')
        diastolic_value = attrs.get('diastolic_value')
        
        # Blood pressure validation
        if metric_type == 'blood_pressure':
            if not systolic_value or not diastolic_value:
                raise serializers.ValidationError(
                    "Blood pressure readings require both systolic and diastolic values."
                )
            if systolic_value <= diastolic_value:
                raise serializers.ValidationError(
                    "Systolic value must be greater than diastolic value."
                )
            # Set the main value to systolic for blood pressure
            attrs['value'] = systolic_value
        else:
            if not value:
                raise serializers.ValidationError(
                    "Value is required for this metric type."
                )
        
        # Validate recorded_at is not in the future
        recorded_at = attrs.get('recorded_at')
        if recorded_at and recorded_at > timezone.now():
            raise serializers.ValidationError(
                "Recorded time cannot be in the future."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create a new health metric."""
        # Set the user from the request
        validated_data['user'] = self.context['request'].user
        
        # Set default recorded_at if not provided
        if not validated_data.get('recorded_at'):
            validated_data['recorded_at'] = timezone.now()
        
        return super().create(validated_data)


class HealthMetricCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating health metrics.
    Matches the data structure from your mobile app.
    """
    patient_id = serializers.CharField(write_only=True, required=False)
    value = serializers.FloatField(required=False)  # Make value optional for blood pressure
    
    class Meta:
        model = HealthMetric
        fields = [
            'metric_type', 'value', 'unit', 'systolic_value', 
            'diastolic_value', 'recorded_at', 'is_manual_entry',
            'notes', 'patient_id'
        ]
    
    def validate(self, attrs):
        """Validate health metric data."""
        metric_type = attrs.get('metric_type')
        value = attrs.get('value')
        systolic_value = attrs.get('systolic_value')
        diastolic_value = attrs.get('diastolic_value')
        
        # Blood pressure validation
        if metric_type == 'blood_pressure':
            if not systolic_value or not diastolic_value:
                raise serializers.ValidationError(
                    "Blood pressure readings require both systolic and diastolic values."
                )
            if systolic_value <= diastolic_value:
                raise serializers.ValidationError(
                    "Systolic value must be greater than diastolic value."
                )
            # Set the main value to systolic for blood pressure
            attrs['value'] = systolic_value
        else:
            if not value:
                raise serializers.ValidationError(
                    "Value is required for this metric type."
                )
        
        # Validate recorded_at is not in the future
        recorded_at = attrs.get('recorded_at')
        if recorded_at and recorded_at > timezone.now():
            raise serializers.ValidationError(
                "Recorded time cannot be in the future."
            )
        
        return attrs

    def create(self, validated_data):
        """Create health metric with proper user assignment."""
        # Remove patient_id and use request user
        validated_data.pop('patient_id', None)
        validated_data['user'] = self.context['request'].user
        
        # Set default recorded_at if not provided
        if not validated_data.get('recorded_at'):
            validated_data['recorded_at'] = timezone.now()
        
        # Handle blood pressure logic
        if validated_data.get('metric_type') == 'blood_pressure':
            if validated_data.get('systolic_value'):
                validated_data['value'] = validated_data['systolic_value']
        
        return HealthMetric.objects.create(**validated_data)


class HealthMetricTargetSerializer(serializers.ModelSerializer):
    """
    Serializer for health metric targets/goals.
    """
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    target_type_display = serializers.CharField(source='get_target_type_display', read_only=True)
    
    class Meta:
        model = HealthMetricTarget
        fields = [
            'id', 'metric_type', 'metric_type_display', 'target_value', 
            'target_unit', 'target_systolic', 'target_diastolic',
            'target_type', 'target_type_display', 'min_value', 'max_value',
            'target_date', 'is_active', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create a new health metric target."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HealthMetricSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for health metric summaries and analytics.
    """
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    period_type_display = serializers.CharField(source='get_period_type_display', read_only=True)
    trend_direction_display = serializers.CharField(source='get_trend_direction_display', read_only=True)
    
    class Meta:
        model = HealthMetricSummary
        fields = [
            'id', 'metric_type', 'metric_type_display', 'period_type', 
            'period_type_display', 'period_start', 'period_end',
            'reading_count', 'average_value', 'min_value', 'max_value',
            'avg_systolic', 'avg_diastolic', 'trend_direction',
            'trend_direction_display', 'variance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class HealthMetricBulkCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating health metrics (for IoT device data).
    """
    device_id = serializers.UUIDField()
    metrics = HealthMetricCreateSerializer(many=True)
    
    def validate_device_id(self, value):
        """Validate that the device exists and belongs to the user."""
        try:
            device = IoTDevice.objects.get(device_id=value)
            if device.owner != self.context['request'].user:
                raise serializers.ValidationError("Device does not belong to the authenticated user.")
            return value
        except IoTDevice.DoesNotExist:
            raise serializers.ValidationError("Device not found.")
    
    def create(self, validated_data):
        """Create multiple health metrics from device data."""
        device_id = validated_data['device_id']
        metrics_data = validated_data['metrics']
        
        device = IoTDevice.objects.get(device_id=device_id)
        user = self.context['request'].user
        
        created_metrics = []
        for metric_data in metrics_data:
            metric_data['user'] = user
            metric_data['device'] = device
            metric_data['is_manual_entry'] = False
            
            if not metric_data.get('recorded_at'):
                metric_data['recorded_at'] = timezone.now()
            
            # Handle blood pressure logic
            if metric_data.get('metric_type') == 'blood_pressure':
                if metric_data.get('systolic_value'):
                    metric_data['value'] = metric_data['systolic_value']
            
            metric = HealthMetric.objects.create(**metric_data)
            created_metrics.append(metric)
        
        # Update device last_seen
        device.last_seen = timezone.now()
        device.save()
        
        return {
            'device_id': device_id,
            'metrics_created': len(created_metrics),
            'metrics': created_metrics
        }


class HealthMetricStatsSerializer(serializers.Serializer):
    """
    Serializer for health metric statistics and analytics.
    """
    metric_type = serializers.CharField()
    total_readings = serializers.IntegerField()
    latest_reading = HealthMetricSerializer()
    average_value = serializers.FloatField(allow_null=True)
    min_value = serializers.FloatField(allow_null=True)
    max_value = serializers.FloatField(allow_null=True)
    trend_direction = serializers.CharField()
    normal_range_percentage = serializers.FloatField(allow_null=True)
    
    # Blood pressure specific
    average_systolic = serializers.FloatField(allow_null=True)
    average_diastolic = serializers.FloatField(allow_null=True)


class HealthMetricFilterSerializer(serializers.Serializer):
    """
    Serializer for filtering health metrics.
    """
    metric_type = serializers.ChoiceField(
        choices=HealthMetric.METRIC_TYPE_CHOICES,
        required=False
    )
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    is_manual_entry = serializers.BooleanField(required=False)
    device_id = serializers.UUIDField(required=False)
    limit = serializers.IntegerField(min_value=1, max_value=100, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)
    
    def validate(self, attrs):
        """Validate date range."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "Start date must be before end date."
            )
        
        return attrs
