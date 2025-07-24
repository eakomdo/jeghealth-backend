from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
import logging
import secrets

from .models import IoTDevice, DeviceDataBatch, DeviceAlert
from .serializers import (
    IoTDeviceSerializer, IoTDeviceListSerializer, DeviceDataBatchSerializer,
    DeviceAlertSerializer, DeviceStatsSerializer, DeviceConfigurationSerializer,
    DeviceRegistrationSerializer, DeviceVerificationSerializer, DeviceHealthCheckSerializer
)

logger = logging.getLogger(__name__)


class IoTDevicePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# IoT Device Views
class IoTDeviceListView(generics.ListAPIView):
    """List user's IoT devices"""
    serializer_class = IoTDeviceListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'manufacturer', 'model', 'location']
    ordering_fields = ['name', 'device_type', 'status', 'last_seen', 'created_at']
    ordering = ['-created_at']
    pagination_class = IoTDevicePagination

    def get_queryset(self):
        """Filter devices by current user"""
        queryset = IoTDevice.objects.filter(owner=self.request.user)
        
        # Filter by device type
        device_type = self.request.query_params.get('device_type')
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by online status
        if self.request.query_params.get('online_only'):
            five_minutes_ago = timezone.now() - timedelta(minutes=5)
            queryset = queryset.filter(last_seen__gte=five_minutes_ago)
        
        # Filter by verified devices
        if self.request.query_params.get('verified_only'):
            queryset = queryset.filter(is_verified=True)
        
        return queryset


class IoTDeviceDetailView(generics.RetrieveAPIView):
    """Get IoT device details"""
    serializer_class = IoTDeviceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'device_id'

    def get_queryset(self):
        """Filter devices by current user"""
        return IoTDevice.objects.filter(owner=self.request.user)


class IoTDeviceCreateView(generics.CreateAPIView):
    """Register a new IoT device"""
    serializer_class = DeviceRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Save device with current user as owner"""
        try:
            device = serializer.save()
            logger.info(f"IoT device registered: {device.device_id} for user {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error registering IoT device for user {self.request.user.email}: {str(e)}")
            raise


class IoTDeviceUpdateView(generics.UpdateAPIView):
    """Update IoT device"""
    serializer_class = IoTDeviceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'device_id'

    def get_queryset(self):
        """Filter devices by current user"""
        return IoTDevice.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        """Update device with logging"""
        try:
            device = serializer.save()
            logger.info(f"IoT device updated: {device.device_id} by user {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error updating IoT device for user {self.request.user.email}: {str(e)}")
            raise


class IoTDeviceDeleteView(generics.DestroyAPIView):
    """Remove IoT device"""
    permission_classes = [IsAuthenticated]
    lookup_field = 'device_id'

    def get_queryset(self):
        """Filter devices by current user"""
        return IoTDevice.objects.filter(owner=self.request.user)

    def perform_destroy(self, instance):
        """Delete device with logging"""
        device_id = instance.device_id
        super().perform_destroy(instance)
        logger.info(f"IoT device deleted: {device_id} by user {self.request.user.email}")


# Device Data Batch Views
class DeviceDataBatchListView(generics.ListCreateAPIView):
    """List and create device data batches"""
    serializer_class = DeviceDataBatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['received_at', 'batch_start_time', 'data_count']
    ordering = ['-received_at']
    pagination_class = IoTDevicePagination

    def get_queryset(self):
        """Filter batches by current user's devices"""
        queryset = DeviceDataBatch.objects.filter(device__owner=self.request.user)
        
        # Filter by device
        device_id = self.request.query_params.get('device')
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(batch_start_time__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(batch_end_time__lte=end_date)
            except ValueError:
                pass
        
        return queryset.select_related('device')


class DeviceDataBatchDetailView(generics.RetrieveAPIView):
    """Get device data batch details"""
    serializer_class = DeviceDataBatchSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'batch_id'

    def get_queryset(self):
        """Filter batches by current user's devices"""
        return DeviceDataBatch.objects.filter(device__owner=self.request.user).select_related('device')


# Device Alert Views
class DeviceAlertListView(generics.ListAPIView):
    """List device alerts"""
    serializer_class = DeviceAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message', 'device__name']
    ordering_fields = ['created_at', 'severity', 'alert_type']
    ordering = ['-created_at']
    pagination_class = IoTDevicePagination

    def get_queryset(self):
        """Filter alerts by current user's devices"""
        queryset = DeviceAlert.objects.filter(device__owner=self.request.user)
        
        # Filter by device
        device_id = self.request.query_params.get('device')
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        # Filter by alert type
        alert_type = self.request.query_params.get('alert_type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by active alerts
        if self.request.query_params.get('active_only'):
            queryset = queryset.filter(is_active=True)
        
        # Filter by unacknowledged alerts
        if self.request.query_params.get('unacknowledged_only'):
            queryset = queryset.filter(is_acknowledged=False)
        
        return queryset.select_related('device', 'acknowledged_by')


class DeviceAlertDetailView(generics.RetrieveUpdateAPIView):
    """Get or update device alert"""
    serializer_class = DeviceAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter alerts by current user's devices"""
        return DeviceAlert.objects.filter(device__owner=self.request.user).select_related('device', 'acknowledged_by')


# Statistics and Analytics Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_stats(request):
    """Get device statistics for current user"""
    try:
        user = request.user
        devices = IoTDevice.objects.filter(owner=user)
        
        # Basic counts
        total_devices = devices.count()
        active_devices = devices.filter(status='ACTIVE').count()
        verified_devices = devices.filter(is_verified=True).count()
        
        # Online devices (sent data in last 5 minutes)
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        online_devices = devices.filter(last_seen__gte=five_minutes_ago).count()
        
        # Alert counts
        alerts = DeviceAlert.objects.filter(device__owner=user)
        unresolved_alerts = alerts.filter(is_resolved=False).count()
        critical_alerts = alerts.filter(severity='CRITICAL', is_active=True).count()
        
        # Device types distribution
        device_types = devices.values('device_type').annotate(
            count=Count('id')
        )
        device_types_distribution = {
            item['device_type']: item['count']
            for item in device_types
        }
        
        # Data points in last 24 hours
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        data_points_last_24h = DeviceDataBatch.objects.filter(
            device__owner=user,
            received_at__gte=twenty_four_hours_ago
        ).aggregate(
            total=Sum('data_count')
        )['total'] or 0
        
        # Average device accuracy
        average_accuracy = devices.filter(
            accuracy_score__isnull=False
        ).aggregate(
            avg_accuracy=Avg('accuracy_score')
        )['avg_accuracy'] or 0
        
        # Last sync times for devices
        last_sync_times = list(devices.filter(
            last_seen__isnull=False
        ).values('name', 'last_seen').order_by('-last_seen')[:5])
        
        stats_data = {
            'total_devices': total_devices,
            'active_devices': active_devices,
            'online_devices': online_devices,
            'verified_devices': verified_devices,
            'unresolved_alerts': unresolved_alerts,
            'critical_alerts': critical_alerts,
            'device_types_distribution': device_types_distribution,
            'data_points_last_24h': data_points_last_24h,
            'average_accuracy': round(average_accuracy, 3),
            'last_sync_times': last_sync_times,
        }
        
        serializer = DeviceStatsSerializer(stats_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating device stats for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to generate device statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_device(request, device_id):
    """Verify a device with verification code"""
    try:
        device = IoTDevice.objects.get(device_id=device_id, owner=request.user)
        
        serializer = DeviceVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        verification_code = serializer.validated_data['verification_code']
        
        # In a real implementation, you would validate the verification code
        # For now, we'll accept any 6-character alphanumeric code
        if len(verification_code) == 6 and verification_code.isalnum():
            device.is_verified = True
            device.status = 'ACTIVE'
            device.save(update_fields=['is_verified', 'status', 'updated_at'])
            
            logger.info(f"Device verified: {device_id} by user {request.user.email}")
            
            return Response({
                'message': 'Device verified successfully',
                'device_id': device_id,
                'is_verified': True
            })
        else:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except IoTDevice.DoesNotExist:
        return Response(
            {'error': 'Device not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error verifying device {device_id} for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to verify device'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_device_configuration(request, device_id):
    """Update device configuration"""
    try:
        device = IoTDevice.objects.get(device_id=device_id, owner=request.user)
        
        serializer = DeviceConfigurationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        configuration = serializer.validated_data['configuration']
        device.configuration.update(configuration)
        device.save(update_fields=['configuration', 'updated_at'])
        
        logger.info(f"Device configuration updated: {device_id} by user {request.user.email}")
        
        return Response({
            'message': 'Device configuration updated successfully',
            'device_id': device_id,
            'configuration': device.configuration
        })
        
    except IoTDevice.DoesNotExist:
        return Response(
            {'error': 'Device not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error updating device configuration {device_id} for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to update device configuration'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_health_check(request, device_id):
    """Get device health status"""
    try:
        device = IoTDevice.objects.get(device_id=device_id, owner=request.user)
        
        # In a real implementation, this would ping the device or check recent data
        # For now, we'll return mock health data based on device status
        health_data = {
            'status': device.status.lower(),
            'battery_level': 85 if device.is_online else 20,
            'signal_strength': 75 if device.is_online else 10,
            'last_calibration': device.calibration_date,
            'firmware_version': device.firmware_version,
            'sensor_status': {'all_sensors': 'operational' if device.status == 'ACTIVE' else 'error'},
            'memory_usage': 0.65,
            'storage_usage': 0.30
        }
        
        serializer = DeviceHealthCheckSerializer(health_data)
        return Response(serializer.data)
        
    except IoTDevice.DoesNotExist:
        return Response(
            {'error': 'Device not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error checking device health {device_id} for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to check device health'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_device_data(request, device_id):
    """Manually trigger device data sync"""
    try:
        device = IoTDevice.objects.get(device_id=device_id, owner=request.user)
        
        if not device.is_verified:
            return Response(
                {'error': 'Device must be verified before syncing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update last_seen to current time
        device.last_seen = timezone.now()
        device.save(update_fields=['last_seen'])
        
        # In a real implementation, this would trigger actual device sync
        logger.info(f"Device sync triggered: {device_id} by user {request.user.email}")
        
        return Response({
            'message': 'Device sync initiated successfully',
            'device_id': device_id,
            'last_seen': device.last_seen
        })
        
    except IoTDevice.DoesNotExist:
        return Response(
            {'error': 'Device not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error syncing device {device_id} for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to sync device'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
