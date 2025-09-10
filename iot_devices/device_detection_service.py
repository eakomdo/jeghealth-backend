"""
iOS Device Detection Services
Handles Bluetooth and WiFi scanning for iOS device discovery
"""

import asyncio
import time
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import DeviceScanSession, DetectedDevice, iOSDeviceProfile

logger = logging.getLogger(__name__)


class DeviceDetectionService:
    """
    Service for detecting iOS devices via Bluetooth and WiFi scanning
    """
    
    # Known iOS device identifiers and patterns
    IOS_MANUFACTURERS = [
        'Apple, Inc.',
        'Apple Inc.',
        'Apple',
    ]
    
    IOS_DEVICE_PATTERNS = [
        r'^iPhone.*',
        r'^iPad.*',
        r'^iPod.*',
        r'^Apple Watch.*',
        r'^AirPods.*',
        r'.*iPhone.*',
        r'.*iPad.*',
    ]
    
    IOS_MAC_PREFIXES = [
        '00:03:93',  # Apple
        '00:05:02',  # Apple
        '00:0a:27',  # Apple
        '00:0a:95',  # Apple
        '00:0d:93',  # Apple
        '00:11:24',  # Apple
        '00:14:51',  # Apple
        '00:16:cb',  # Apple
        '00:17:f2',  # Apple
        '00:19:e3',  # Apple
        '00:1b:63',  # Apple
        '00:1c:b3',  # Apple
        '00:1e:c2',  # Apple
        '00:21:e9',  # Apple
        '00:22:41',  # Apple
        '00:23:12',  # Apple
        '00:23:df',  # Apple
        '00:25:00',  # Apple
        '00:25:4b',  # Apple
        '00:25:bc',  # Apple
        '00:26:08',  # Apple
        '00:26:4a',  # Apple
        '00:26:bb',  # Apple
        '04:0c:ce',  # Apple
        '04:15:52',  # Apple
        '04:1e:64',  # Apple
        '04:26:65',  # Apple
        '04:48:9a',  # Apple
        '04:4b:ed',  # Apple
        '04:52:c7',  # Apple
        '04:54:53',  # Apple
        '04:69:f8',  # Apple
        '04:7f:0e',  # Apple
        '04:81:d4',  # Apple
        '04:8d:38',  # Apple
        '04:90:a5',  # Apple
        '04:98:f3',  # Apple
        '04:db:56',  # Apple
        '04:e5:36',  # Apple
        '04:f1:3e',  # Apple
        '04:f7:e4',  # Apple
        '08:00:07',  # Apple
        '08:6d:41',  # Apple
        '08:74:02',  # Apple
        '08:96:d7',  # Apple
        '08:9e:08',  # Apple
        '0c:14:20',  # Apple
        '0c:1d:af',  # Apple
        '0c:30:21',  # Apple
        '0c:4d:e9',  # Apple
        '0c:5b:8f',  # Apple
        '0c:71:33',  # Apple
        '0c:74:c2',  # Apple
        '0c:77:1a',  # Apple
        '0c:d2:92',  # Apple
        '0c:f0:90',  # Apple
    ]
    
    def __init__(self):
        self.scan_timeout = getattr(settings, 'DEVICE_SCAN_TIMEOUT', 30)
        self.max_concurrent_scans = getattr(settings, 'MAX_CONCURRENT_SCANS', 5)
        self.active_scans = {}
    
    async def start_device_scan(self, user, scan_type: str, duration: int = 30) -> DeviceScanSession:
        """
        Start a new device scan session
        
        Args:
            user: Django user object
            scan_type: 'BLUETOOTH', 'WIFI', or 'COMBINED'
            duration: Scan duration in seconds
            
        Returns:
            DeviceScanSession object
        """
        try:
            # Check for existing active scans
            active_scan = DeviceScanSession.objects.filter(
                user=user,
                status__in=['INITIATED', 'SCANNING']
            ).first()
            
            if active_scan:
                raise ValueError(f"User already has an active scan session: {active_scan.id}")
            
            # Create new scan session
            scan_session = DeviceScanSession.objects.create(
                user=user,
                scan_type=scan_type,
                scan_duration=duration,
                status='INITIATED'
            )
            
            logger.info(f"Started {scan_type} scan session {scan_session.id} for user {user.email}")
            
            # Start the actual scanning process
            asyncio.create_task(self._execute_scan(scan_session))
            
            return scan_session
            
        except Exception as e:
            logger.error(f"Error starting device scan: {str(e)}")
            raise
    
    async def _execute_scan(self, scan_session: DeviceScanSession):
        """
        Execute the actual device scanning
        """
        try:
            scan_session.status = 'SCANNING'
            scan_session.save()
            
            detected_devices = []
            
            if scan_session.scan_type in ['BLUETOOTH', 'COMBINED']:
                bluetooth_devices = await self._scan_bluetooth_devices(scan_session.scan_duration)
                detected_devices.extend(bluetooth_devices)
            
            if scan_session.scan_type in ['WIFI', 'COMBINED']:
                wifi_devices = await self._scan_wifi_devices(scan_session.scan_duration)
                detected_devices.extend(wifi_devices)
            
            # Process and save detected devices
            ios_device_count = 0
            for device_data in detected_devices:
                detected_device = await self._create_detected_device(scan_session, device_data)
                if detected_device.is_ios_device:
                    ios_device_count += 1
            
            # Update scan session
            scan_session.status = 'COMPLETED'
            scan_session.devices_found = len(detected_devices)
            scan_session.ios_devices_found = ios_device_count
            scan_session.completed_at = timezone.now()
            scan_session.scan_results = {
                'total_devices': len(detected_devices),
                'ios_devices': ios_device_count,
                'scan_type': scan_session.scan_type,
                'duration': scan_session.scan_duration
            }
            scan_session.save()
            
            logger.info(f"Completed scan session {scan_session.id}: {len(detected_devices)} devices found, {ios_device_count} iOS devices")
            
        except Exception as e:
            logger.error(f"Error executing scan {scan_session.id}: {str(e)}")
            scan_session.status = 'FAILED'
            scan_session.error_message = str(e)
            scan_session.completed_at = timezone.now()
            scan_session.save()
    
    async def _scan_bluetooth_devices(self, duration: int) -> List[Dict]:
        """
        Scan for Bluetooth devices
        
        Note: This is a mock implementation. In a real scenario, you would:
        1. Use system Bluetooth APIs (like BlueZ on Linux)
        2. Use platform-specific libraries (pybluez, bleak, etc.)
        3. Interface with hardware Bluetooth adapters
        """
        logger.info(f"Starting Bluetooth scan for {duration} seconds")
        
        # Simulate scanning delay
        await asyncio.sleep(min(duration, 10))
        
        # Mock detected devices - in reality, this would come from actual Bluetooth scanning
        mock_devices = [
            {
                'name': "John's iPhone",
                'mac_address': '04:81:d4:12:34:56',
                'bluetooth_address': '04:81:d4:12:34:56',
                'signal_strength': -45,
                'connection_type': 'BLUETOOTH',
                'manufacturer': 'Apple Inc.',
                'device_type': 'IOS_PHONE',
                'is_paired': False,
                'additional_info': {
                    'bluetooth_class': '0x020420',
                    'services': ['audio', 'input'],
                    'rssi': -45
                }
            },
            {
                'name': "Sarah's AirPods Pro",
                'mac_address': '04:52:c7:ab:cd:ef',
                'bluetooth_address': '04:52:c7:ab:cd:ef',
                'signal_strength': -35,
                'connection_type': 'BLUETOOTH',
                'manufacturer': 'Apple Inc.',
                'device_type': 'IOS_AIRPODS',
                'is_paired': True,
                'additional_info': {
                    'bluetooth_class': '0x240418',
                    'services': ['audio'],
                    'rssi': -35
                }
            },
            {
                'name': "Apple Watch",
                'mac_address': '08:74:02:11:22:33',
                'bluetooth_address': '08:74:02:11:22:33',
                'signal_strength': -50,
                'connection_type': 'BLUETOOTH',
                'manufacturer': 'Apple Inc.',
                'device_type': 'IOS_WATCH',
                'is_paired': False,
                'additional_info': {
                    'bluetooth_class': '0x020420',
                    'services': ['health', 'fitness'],
                    'rssi': -50
                }
            }
        ]
        
        return mock_devices
    
    async def _scan_wifi_devices(self, duration: int) -> List[Dict]:
        """
        Scan for WiFi devices
        
        Note: This is a mock implementation. In a real scenario, you would:
        1. Use WiFi scanning libraries (scapy, wireless-tools, etc.)
        2. Parse WiFi probe requests and responses
        3. Analyze device fingerprints and MAC addresses
        """
        logger.info(f"Starting WiFi scan for {duration} seconds")
        
        # Simulate scanning delay
        await asyncio.sleep(min(duration, 8))
        
        # Mock detected devices - in reality, this would come from actual WiFi scanning
        mock_devices = [
            {
                'name': "Mike's iPad",
                'mac_address': '0c:74:c2:44:55:66',
                'signal_strength': -40,
                'connection_type': 'WIFI',
                'manufacturer': 'Apple Inc.',
                'device_type': 'IOS_TABLET',
                'additional_info': {
                    'ssid': 'Home_Network',
                    'frequency': '2.4GHz',
                    'encryption': 'WPA2',
                    'rssi': -40
                }
            },
            {
                'name': "",  # Hidden/unnamed device
                'mac_address': '04:f7:e4:77:88:99',
                'signal_strength': -60,
                'connection_type': 'WIFI',
                'manufacturer': 'Apple Inc.',
                'device_type': 'IOS_UNKNOWN',
                'additional_info': {
                    'ssid': '',
                    'frequency': '5GHz',
                    'encryption': 'WPA3',
                    'rssi': -60
                }
            }
        ]
        
        return mock_devices
    
    async def _create_detected_device(self, scan_session: DeviceScanSession, device_data: Dict) -> DetectedDevice:
        """
        Create a DetectedDevice object from scan data
        """
        # Determine if this is an iOS device
        is_ios = self._is_ios_device(device_data)
        
        detected_device = DetectedDevice.objects.create(
            scan_session=scan_session,
            device_name=device_data.get('name', ''),
            device_type=device_data.get('device_type', 'UNKNOWN'),
            mac_address=device_data.get('mac_address', ''),
            bluetooth_address=device_data.get('bluetooth_address', ''),
            signal_strength=device_data.get('signal_strength'),
            connection_type=device_data.get('connection_type', 'UNKNOWN'),
            manufacturer=device_data.get('manufacturer', ''),
            is_paired=device_data.get('is_paired', False),
            is_ios_device=is_ios,
            additional_info=device_data.get('additional_info', {})
        )
        
        return detected_device
    
    def _is_ios_device(self, device_data: Dict) -> bool:
        """
        Determine if a detected device is an iOS device
        """
        # Check manufacturer
        manufacturer = device_data.get('manufacturer', '').lower()
        if any(apple_name.lower() in manufacturer for apple_name in self.IOS_MANUFACTURERS):
            return True
        
        # Check device name patterns
        device_name = device_data.get('name', '')
        if any(re.match(pattern, device_name, re.IGNORECASE) for pattern in self.IOS_DEVICE_PATTERNS):
            return True
        
        # Check MAC address prefix
        mac_address = device_data.get('mac_address', '').upper()
        if mac_address:
            mac_prefix = ':'.join(mac_address.split(':')[:3])
            if mac_prefix in self.IOS_MAC_PREFIXES:
                return True
        
        # Check device type
        device_type = device_data.get('device_type', '')
        if device_type.startswith('IOS_'):
            return True
        
        return False
    
    async def get_scan_status(self, scan_session_id: str) -> Dict:
        """
        Get the status of a scan session
        """
        try:
            scan_session = DeviceScanSession.objects.get(id=scan_session_id)
            
            status_data = {
                'session_id': str(scan_session.id),
                'status': scan_session.status,
                'scan_type': scan_session.scan_type,
                'duration': scan_session.scan_duration,
                'devices_found': scan_session.devices_found,
                'ios_devices_found': scan_session.ios_devices_found,
                'initiated_at': scan_session.initiated_at.isoformat(),
                'completed_at': scan_session.completed_at.isoformat() if scan_session.completed_at else None,
                'error_message': scan_session.error_message
            }
            
            # Add detected devices if scan is completed
            if scan_session.status == 'COMPLETED':
                detected_devices = scan_session.detected_devices.all()
                status_data['detected_devices'] = [
                    {
                        'id': str(device.id),
                        'name': device.device_name,
                        'type': device.device_type,
                        'mac_address': device.mac_address,
                        'signal_strength': device.signal_strength,
                        'connection_type': device.connection_type,
                        'manufacturer': device.manufacturer,
                        'is_ios_device': device.is_ios_device,
                        'is_paired': device.is_paired
                    }
                    for device in detected_devices
                ]
            
            return status_data
            
        except DeviceScanSession.DoesNotExist:
            raise ValueError(f"Scan session {scan_session_id} not found")
    
    async def create_ios_device_profile(self, user, detected_device_id: str, device_name: str = None) -> iOSDeviceProfile:
        """
        Create an iOS device profile from a detected device
        """
        try:
            detected_device = DetectedDevice.objects.get(id=detected_device_id)
            
            if not detected_device.is_ios_device:
                raise ValueError("Device is not confirmed to be an iOS device")
            
            # Generate unique device identifier
            device_identifier = f"ios_{detected_device.mac_address.replace(':', '')}"
            if detected_device.bluetooth_address:
                device_identifier += f"_{detected_device.bluetooth_address.replace(':', '')}"
            
            # Create iOS device profile
            ios_profile = iOSDeviceProfile.objects.create(
                user=user,
                detected_device=detected_device,
                device_name=device_name or detected_device.device_name or f"iOS Device ({detected_device.device_type})",
                device_identifier=device_identifier,
                device_model=detected_device.additional_info.get('model', ''),
                status='DISCOVERED',
                available_health_data=['heart_rate', 'steps', 'sleep', 'activity'],  # Default iOS health data
                permissions_granted={},
                sync_settings={
                    'auto_sync': True,
                    'sync_frequency': 60,
                    'data_types': ['heart_rate', 'steps', 'sleep']
                }
            )
            
            logger.info(f"Created iOS device profile {ios_profile.id} for user {user.email}")
            
            return ios_profile
            
        except DetectedDevice.DoesNotExist:
            raise ValueError(f"Detected device {detected_device_id} not found")


# Initialize the service
device_detection_service = DeviceDetectionService()
