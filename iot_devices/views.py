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
import asyncio

from .models import (
    IoTDevice, DeviceDataBatch, DeviceAlert,
    DeviceScanSession, DetectedDevice, iOSDeviceProfile
)
from .serializers import (
    IoTDeviceSerializer, IoTDeviceListSerializer, DeviceDataBatchSerializer,
    DeviceAlertSerializer, DeviceStatsSerializer, DeviceConfigurationSerializer,
    DeviceRegistrationSerializer, DeviceVerificationSerializer, DeviceHealthCheckSerializer,
    DeviceScanSessionSerializer, DeviceScanCreateSerializer, DetectedDeviceSerializer,
    iOSDeviceProfileSerializer, iOSDeviceProfileCreateSerializer, DeviceScanResultsSerializer
)
from .device_detection_service import device_detection_service

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


# Device Detection Views
class DeviceScanSessionListView(generics.ListAPIView):
    """List user's device scan sessions"""
    serializer_class = DeviceScanSessionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = IoTDevicePagination
    ordering = ['-initiated_at']
    
    def get_queryset(self):
        return DeviceScanSession.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_device_scan(request):
    """
    Start a new device scan session for iOS device detection
    
    POST /api/v1/iot-devices/scan/start/
    """
    try:
        serializer = DeviceScanCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid scan parameters', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        scan_type = serializer.validated_data['scan_type']
        duration = serializer.validated_data['duration']
        
        # Check for existing active scans
        active_scan = DeviceScanSession.objects.filter(
            user=request.user,
            status__in=['INITIATED', 'SCANNING']
        ).first()
        
        if active_scan:
            return Response(
                {
                    'error': 'Active scan already exists',
                    'active_scan_id': str(active_scan.id),
                    'message': 'Please wait for the current scan to complete or cancel it first'
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # Start the scan session
        scan_session = asyncio.run(
            device_detection_service.start_device_scan(
                user=request.user,
                scan_type=scan_type,
                duration=duration
            )
        )
        
        response_serializer = DeviceScanSessionSerializer(scan_session)
        
        logger.info(f"Started device scan {scan_session.id} for user {request.user.email}")
        
        return Response({
            'message': 'Device scan started successfully',
            'scan_session': response_serializer.data,
            'status_check_url': f'/api/v1/iot-devices/scan/{scan_session.id}/status/',
            'estimated_completion': (timezone.now() + timedelta(seconds=duration)).isoformat()
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error starting device scan for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to start device scan'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scan_status(request, scan_id):
    """
    Get the status of a device scan session
    
    GET /api/v1/iot-devices/scan/{scan_id}/status/
    """
    try:
        scan_session = DeviceScanSession.objects.get(id=scan_id, user=request.user)
        
        # Get detailed status from the service
        status_data = asyncio.run(
            device_detection_service.get_scan_status(str(scan_session.id))
        )
        
        return Response(status_data, status=status.HTTP_200_OK)
        
    except DeviceScanSession.DoesNotExist:
        return Response(
            {'error': 'Scan session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error getting scan status {scan_id}: {str(e)}")
        return Response(
            {'error': 'Failed to get scan status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scan_results(request, scan_id):
    """
    Get detailed results of a completed device scan
    
    GET /api/v1/iot-devices/scan/{scan_id}/results/
    """
    try:
        scan_session = DeviceScanSession.objects.get(id=scan_id, user=request.user)
        
        if scan_session.status != 'COMPLETED':
            return Response(
                {
                    'error': 'Scan not completed',
                    'current_status': scan_session.status,
                    'message': 'Scan results are only available for completed scans'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get detected devices
        detected_devices = scan_session.detected_devices.all()
        ios_devices = detected_devices.filter(is_ios_device=True)
        
        # Serialize the results
        session_serializer = DeviceScanSessionSerializer(scan_session)
        devices_serializer = DetectedDeviceSerializer(detected_devices, many=True)
        ios_serializer = DetectedDeviceSerializer(ios_devices, many=True)
        
        results_data = {
            'session_info': session_serializer.data,
            'detected_devices': devices_serializer.data,
            'ios_devices': ios_serializer.data
        }
        
        results_serializer = DeviceScanResultsSerializer(results_data)
        
        return Response(results_serializer.data, status=status.HTTP_200_OK)
        
    except DeviceScanSession.DoesNotExist:
        return Response(
            {'error': 'Scan session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error getting scan results {scan_id}: {str(e)}")
        return Response(
            {'error': 'Failed to get scan results'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class DetectedDeviceListView(generics.ListAPIView):
    """List detected devices from user's scan sessions"""
    serializer_class = DetectedDeviceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = IoTDevicePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['device_name', 'manufacturer', 'device_model']
    ordering_fields = ['device_name', 'device_type', 'signal_strength', 'first_seen']
    ordering = ['-last_seen']
    
    def get_queryset(self):
        queryset = DetectedDevice.objects.filter(scan_session__user=self.request.user)
        
        # Filter by iOS devices only
        ios_only = self.request.query_params.get('ios_only')
        if ios_only and ios_only.lower() == 'true':
            queryset = queryset.filter(is_ios_device=True)
        
        # Filter by device type
        device_type = self.request.query_params.get('device_type')
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        
        # Filter by connection type
        connection_type = self.request.query_params.get('connection_type')
        if connection_type:
            queryset = queryset.filter(connection_type=connection_type)
        
        # Filter by scan session
        scan_session_id = self.request.query_params.get('scan_session')
        if scan_session_id:
            queryset = queryset.filter(scan_session_id=scan_session_id)
        
        return queryset


class DetectedDeviceDetailView(generics.RetrieveAPIView):
    """Get details of a detected device"""
    serializer_class = DetectedDeviceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DetectedDevice.objects.filter(scan_session__user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ios_device_profile(request):
    """
    Create an iOS device profile from a detected device
    
    POST /api/v1/iot-devices/ios-profiles/create/
    """
    try:
        serializer = iOSDeviceProfileCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid profile data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        detected_device_id = serializer.validated_data['detected_device_id']
        device_name = serializer.validated_data.get('device_name')
        
        # Check if profile already exists for this device
        existing_profile = iOSDeviceProfile.objects.filter(
            user=request.user,
            detected_device_id=detected_device_id
        ).first()
        
        if existing_profile:
            return Response(
                {
                    'error': 'Profile already exists',
                    'existing_profile_id': str(existing_profile.id),
                    'message': 'An iOS device profile already exists for this detected device'
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # Create the iOS device profile
        ios_profile = asyncio.run(
            device_detection_service.create_ios_device_profile(
                user=request.user,
                detected_device_id=str(detected_device_id),
                device_name=device_name
            )
        )
        
        # Update additional settings if provided
        if 'sync_frequency' in serializer.validated_data:
            ios_profile.sync_frequency = serializer.validated_data['sync_frequency']
        
        if 'health_data_permissions' in serializer.validated_data:
            ios_profile.permissions_granted = serializer.validated_data['health_data_permissions']
        
        if 'is_primary_device' in serializer.validated_data:
            # If setting as primary, remove primary flag from other devices
            if serializer.validated_data['is_primary_device']:
                iOSDeviceProfile.objects.filter(
                    user=request.user,
                    is_primary_device=True
                ).update(is_primary_device=False)
            ios_profile.is_primary_device = serializer.validated_data['is_primary_device']
        
        ios_profile.save()
        
        response_serializer = iOSDeviceProfileSerializer(ios_profile)
        
        logger.info(f"Created iOS device profile {ios_profile.id} for user {request.user.email}")
        
        return Response({
            'message': 'iOS device profile created successfully',
            'profile': response_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error creating iOS device profile for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to create iOS device profile'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class iOSDeviceProfileListView(generics.ListAPIView):
    """List user's iOS device profiles"""
    serializer_class = iOSDeviceProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = IoTDevicePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['device_name', 'device_model']
    ordering_fields = ['device_name', 'status', 'last_sync', 'created_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        queryset = iOSDeviceProfile.objects.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by primary device
        primary_only = self.request.query_params.get('primary_only')
        if primary_only and primary_only.lower() == 'true':
            queryset = queryset.filter(is_primary_device=True)
        
        return queryset


class iOSDeviceProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete an iOS device profile"""
    serializer_class = iOSDeviceProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return iOSDeviceProfile.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_detection_stats(request):
    """
    Get device detection statistics for the user
    
    GET /api/v1/iot-devices/detection-stats/
    """
    try:
        user = request.user
        
        # Get scan session stats
        total_scans = DeviceScanSession.objects.filter(user=user).count()
        completed_scans = DeviceScanSession.objects.filter(user=user, status='COMPLETED').count()
        failed_scans = DeviceScanSession.objects.filter(user=user, status='FAILED').count()
        
        # Get detected device stats
        total_devices = DetectedDevice.objects.filter(scan_session__user=user).count()
        ios_devices = DetectedDevice.objects.filter(
            scan_session__user=user,
            is_ios_device=True
        ).count()
        
        # Get iOS profile stats
        ios_profiles = iOSDeviceProfile.objects.filter(user=user).count()
        active_profiles = iOSDeviceProfile.objects.filter(
            user=user,
            status__in=['PAIRED', 'CONNECTED', 'SYNCING']
        ).count()
        
        # Get recent scan activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_scans = DeviceScanSession.objects.filter(
            user=user,
            initiated_at__gte=thirty_days_ago
        ).count()
        
        # Device type distribution
        device_types = DetectedDevice.objects.filter(
            scan_session__user=user,
            is_ios_device=True
        ).values('device_type').annotate(count=Count('device_type'))
        
        stats = {
            'scan_statistics': {
                'total_scans': total_scans,
                'completed_scans': completed_scans,
                'failed_scans': failed_scans,
                'success_rate': round((completed_scans / total_scans * 100) if total_scans > 0 else 0, 2),
                'recent_scans_30_days': recent_scans
            },
            'device_statistics': {
                'total_devices_detected': total_devices,
                'ios_devices_detected': ios_devices,
                'ios_detection_rate': round((ios_devices / total_devices * 100) if total_devices > 0 else 0, 2),
                'device_profiles_created': ios_profiles,
                'active_profiles': active_profiles
            },
            'device_type_distribution': {
                item['device_type']: item['count'] for item in device_types
            },
            'last_scan': None
        }
        
        # Get last scan info
        last_scan = DeviceScanSession.objects.filter(user=user).order_by('-initiated_at').first()
        if last_scan:
            stats['last_scan'] = {
                'id': str(last_scan.id),
                'scan_type': last_scan.scan_type,
                'status': last_scan.status,
                'devices_found': last_scan.devices_found,
                'ios_devices_found': last_scan.ios_devices_found,
                'initiated_at': last_scan.initiated_at.isoformat()
            }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting device detection stats for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to get device detection statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
