from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import IoTDevice, DeviceDataBatch, DeviceAlert

User = get_user_model()


class IoTDeviceSerializer(serializers.ModelSerializer):
    """Serializer for IoT devices"""
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_online = serializers.ReadOnlyField()
    
    class Meta:
        model = IoTDevice
        fields = [
            'device_id', 'name', 'device_type', 'device_type_display', 'manufacturer',
            'model', 'firmware_version', 'owner', 'status', 'status_display',
            'is_verified', 'last_seen', 'supported_metrics', 'calibration_date',
            'accuracy_score', 'configuration', 'location', 'is_online',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'device_id', 'owner', 'api_key', 'is_online', 'created_at', 'updated_at'
        ]

    def validate_accuracy_score(self, value):
        """Validate accuracy score is between 0 and 1"""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Accuracy score must be between 0 and 1")
        return value

    def validate_supported_metrics(self, value):
        """Validate supported metrics format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Supported metrics must be a list")
        
        # Valid metric types (should match health_metrics app)
        valid_metrics = [
            'heart_rate', 'blood_pressure', 'glucose', 'weight', 'temperature',
            'steps', 'sleep', 'oxygen_saturation', 'calories', 'distance'
        ]
        
        for metric in value:
            if metric not in valid_metrics:
                raise serializers.ValidationError(f"Invalid metric type: {metric}")
        
        return value

    def create(self, validated_data):
        # Set owner to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user
        return super().create(validated_data)


class IoTDeviceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing IoT devices"""
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_online = serializers.ReadOnlyField()
    
    class Meta:
        model = IoTDevice
        fields = [
            'device_id', 'name', 'device_type', 'device_type_display',
            'manufacturer', 'model', 'status', 'status_display', 'is_verified',
            'last_seen', 'is_online', 'location'
        ]


class DeviceDataBatchSerializer(serializers.ModelSerializer):
    """Serializer for device data batches"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DeviceDataBatch
        fields = [
            'batch_id', 'device', 'device_name', 'data_count', 'batch_start_time',
            'batch_end_time', 'status', 'status_display', 'processed_count',
            'error_count', 'raw_data', 'processing_errors', 'checksum',
            'received_at', 'processed_at'
        ]
        read_only_fields = [
            'batch_id', 'device_name', 'status_display', 'processed_count',
            'error_count', 'processing_errors', 'received_at', 'processed_at'
        ]

    def validate_raw_data(self, value):
        """Validate raw data format"""
        if not isinstance(value, (dict, list)):
            raise serializers.ValidationError("Raw data must be a dictionary or list")
        
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    raise serializers.ValidationError("Each data item must be a dictionary")
                if 'timestamp' not in item:
                    raise serializers.ValidationError("Each data item must have a timestamp")
                if 'value' not in item:
                    raise serializers.ValidationError("Each data item must have a value")
        
        return value

    def validate(self, data):
        """Cross-field validation"""
        # Verify device belongs to current user
        device = data.get('device')
        request = self.context.get('request')
        if request and device and device.owner != request.user:
            raise serializers.ValidationError("You can only upload data for your own devices")
        
        # Validate batch time range
        start_time = data.get('batch_start_time')
        end_time = data.get('batch_end_time')
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Batch start time must be before end time")
        
        return data


class DeviceAlertSerializer(serializers.ModelSerializer):
    """Serializer for device alerts"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.get_full_name', read_only=True)
    
    class Meta:
        model = DeviceAlert
        fields = [
            'id', 'device', 'device_name', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'title', 'message', 'is_active',
            'is_acknowledged', 'acknowledged_by', 'acknowledged_by_name',
            'acknowledged_at', 'is_resolved', 'resolved_at', 'resolution_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'device_name', 'alert_type_display', 'severity_display',
            'acknowledged_by_name', 'acknowledged_at', 'resolved_at',
            'created_at', 'updated_at'
        ]

    def update(self, instance, validated_data):
        """Handle acknowledgment and resolution logic"""
        request = self.context.get('request')
        
        # Handle acknowledgment
        if validated_data.get('is_acknowledged') and not instance.is_acknowledged:
            validated_data['acknowledged_by'] = request.user if request else None
            validated_data['acknowledged_at'] = timezone.now()
        elif not validated_data.get('is_acknowledged', True) and instance.is_acknowledged:
            validated_data['acknowledged_by'] = None
            validated_data['acknowledged_at'] = None
        
        # Handle resolution
        if validated_data.get('is_resolved') and not instance.is_resolved:
            validated_data['resolved_at'] = timezone.now()
            validated_data['is_active'] = False
        elif not validated_data.get('is_resolved', True) and instance.is_resolved:
            validated_data['resolved_at'] = None
            if not validated_data.get('is_active', False):
                validated_data['is_active'] = True
        
        return super().update(instance, validated_data)


class DeviceStatsSerializer(serializers.Serializer):
    """Serializer for device statistics"""
    total_devices = serializers.IntegerField()
    active_devices = serializers.IntegerField()
    online_devices = serializers.IntegerField()
    verified_devices = serializers.IntegerField()
    unresolved_alerts = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    device_types_distribution = serializers.DictField()
    data_points_last_24h = serializers.IntegerField()
    average_accuracy = serializers.FloatField()
    last_sync_times = serializers.ListField()


class DeviceConfigurationSerializer(serializers.Serializer):
    """Serializer for device configuration updates"""
    configuration = serializers.JSONField()
    
    def validate_configuration(self, value):
        """Validate configuration format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Configuration must be a dictionary")
        return value


class DeviceRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering new devices"""
    
    class Meta:
        model = IoTDevice
        fields = [
            'device_id', 'name', 'device_type', 'manufacturer', 'model', 'firmware_version',
            'supported_metrics', 'location', 'status', 'is_verified', 'created_at'
        ]
        read_only_fields = ['device_id', 'status', 'is_verified', 'created_at']

    def validate_supported_metrics(self, value):
        """Validate supported metrics format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Supported metrics must be a list")
        
        # Valid metric types (should match health_metrics app)
        valid_metrics = [
            'heart_rate', 'blood_pressure', 'glucose', 'weight', 'temperature',
            'steps', 'sleep', 'oxygen_saturation', 'calories', 'distance'
        ]
        
        for metric in value:
            if metric not in valid_metrics:
                raise serializers.ValidationError(f"Invalid metric type: {metric}")
        
        return value

    def create(self, validated_data):
        # Set owner to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user
        
        # Set initial status
        validated_data['status'] = 'INACTIVE'
        validated_data['is_verified'] = False
        
        return super().create(validated_data)


class DeviceVerificationSerializer(serializers.Serializer):
    """Serializer for device verification"""
    verification_code = serializers.CharField(max_length=10)
    
    def validate_verification_code(self, value):
        """Validate verification code format"""
        if not value.isalnum() or len(value) != 6:
            raise serializers.ValidationError("Verification code must be 6 alphanumeric characters")
        return value


class DeviceHealthCheckSerializer(serializers.Serializer):
    """Serializer for device health check responses"""
    status = serializers.CharField()
    battery_level = serializers.IntegerField(required=False)
    signal_strength = serializers.IntegerField(required=False)
    last_calibration = serializers.DateTimeField(required=False)
    firmware_version = serializers.CharField(required=False)
    sensor_status = serializers.DictField(required=False)
    memory_usage = serializers.FloatField(required=False)
    storage_usage = serializers.FloatField(required=False)
