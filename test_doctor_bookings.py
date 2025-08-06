from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from providers.models import HealthcareProvider
from appointments.models import Appointment
import json

User = get_user_model()


class DoctorBookingsTestCase(APITestCase):
    """Comprehensive test suite for doctor booking endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.patient_user = User.objects.create_user(
            email='patient@test.com',
            username='patient_test',
            password='testpass123',
            first_name='John',
            last_name='Patient'
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            username='admin_test',
            password='adminpass123',
            is_staff=True
        )
        
        # Create test healthcare providers (doctors)
        self.doctor1 = HealthcareProvider.objects.create(
            first_name='Sarah',
            last_name='Johnson',
            email='sarah.johnson@hospital.com',
            specialization='Cardiology',
            license_number='MD12345',
            hospital_clinic='City Medical Center',
            phone_number='+233501234567',
            years_of_experience=10,
            consultation_fee=200.00
        )
        
        self.doctor2 = HealthcareProvider.objects.create(
            first_name='Michael',
            last_name='Brown',
            email='michael.brown@clinic.com',
            specialization='Pediatrics',
            license_number='MD67890',
            hospital_clinic='Children Hospital',
            phone_number='+233501234568',
            years_of_experience=15,
            consultation_fee=180.00
        )
        
        # Create test appointments for different scenarios
        now = timezone.now()
        
        # Today's appointments
        self.appointment_today = Appointment.objects.create(
            patient=self.patient_user,
            healthcare_provider=self.doctor1,
            appointment_date=now.replace(hour=10, minute=0),
            appointment_type='consultation',
            chief_complaint='Heart checkup',
            status='scheduled',
            duration_minutes=30,
            consultation_fee=200.00
        )
        
        # Past appointment (completed)
        self.appointment_completed = Appointment.objects.create(
            patient=self.patient_user,
            healthcare_provider=self.doctor1,
            appointment_date=now - timedelta(days=7),
            appointment_type='follow_up',
            chief_complaint='Follow-up consultation',
            status='completed',
            duration_minutes=45,
            consultation_fee=200.00,
            diagnosis='Normal recovery progress',
            treatment_plan='Continue medication'
        )
        
        # Future appointment
        self.appointment_future = Appointment.objects.create(
            patient=self.patient_user,
            healthcare_provider=self.doctor1,
            appointment_date=now + timedelta(days=3),
            appointment_type='checkup',
            chief_complaint='Routine checkup',
            status='confirmed',
            duration_minutes=30,
            consultation_fee=200.00
        )
        
        # Appointment for different doctor
        self.appointment_doctor2 = Appointment.objects.create(
            patient=self.patient_user,
            healthcare_provider=self.doctor2,
            appointment_date=now + timedelta(days=1),
            appointment_type='consultation',
            chief_complaint='Child wellness check',
            status='scheduled',
            duration_minutes=30,
            consultation_fee=180.00
        )

    def get_auth_token(self, user):
        """Helper method to get JWT token for user"""
        url = reverse('token_obtain_pair')
        data = {
            'email': user.email,
            'password': 'testpass123' if not user.is_staff else 'adminpass123'
        }
        response = self.client.post(url, data, format='json')
        return response.data['access'] if response.status_code == 200 else None

    def test_doctor_get_all_appointments(self):
        """Test doctor fetching all their appointments"""
        # Authenticate
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Test endpoint
        url = reverse('doctor-appointment-list', kwargs={'doctor_id': self.doctor1.id})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # 3 appointments for doctor1
        
        # Verify response structure
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        
        # Verify appointment data
        appointments = response.data['results']
        appointment_ids = [apt['id'] for apt in appointments]
        self.assertIn(str(self.appointment_today.id), appointment_ids)
        self.assertIn(str(self.appointment_completed.id), appointment_ids)
        self.assertIn(str(self.appointment_future.id), appointment_ids)

    def test_doctor_get_todays_appointments(self):
        """Test doctor fetching today's appointments only"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('doctor-todays-appointments', kwargs={'doctor_id': self.doctor1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)  # Only today's appointment
        
        # Verify it's the correct appointment
        appointment = response.data['results'][0]
        self.assertEqual(appointment['id'], str(self.appointment_today.id))
        self.assertEqual(appointment['patient_name'], 'John Patient')
        self.assertEqual(appointment['chief_complaint'], 'Heart checkup')

    def test_doctor_get_upcoming_appointments(self):
        """Test doctor fetching upcoming appointments (next 7 days)"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('doctor-upcoming-appointments', kwargs={'doctor_id': self.doctor1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include today's appointment and future appointment
        appointment_ids = [apt['id'] for apt in response.data['results']]
        self.assertIn(str(self.appointment_today.id), appointment_ids)
        self.assertIn(str(self.appointment_future.id), appointment_ids)
        
        # Should not include completed (past) appointment
        self.assertNotIn(str(self.appointment_completed.id), appointment_ids)

    def test_doctor_get_appointment_statistics(self):
        """Test doctor fetching their appointment statistics"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('doctor-appointment-stats', kwargs={'doctor_id': self.doctor1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response structure
        self.assertIn('doctor', response.data)
        self.assertIn('statistics', response.data)
        
        # Verify doctor info
        doctor_info = response.data['doctor']
        self.assertEqual(doctor_info['name'], 'Sarah Johnson')
        self.assertEqual(doctor_info['specialization'], 'Cardiology')
        
        # Verify statistics
        stats = response.data['statistics']
        self.assertEqual(stats['total_appointments'], 3)
        self.assertEqual(stats['completed_appointments'], 1)
        self.assertEqual(stats['cancelled_appointments'], 0)
        self.assertIn('completion_rate', stats)
        self.assertIn('total_revenue', stats)

    def test_doctor_filter_appointments_by_status(self):
        """Test doctor filtering appointments by status"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Filter by completed status
        url = reverse('doctor-appointment-list', kwargs={'doctor_id': self.doctor1.id})
        response = self.client.get(url, {'status': 'completed'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        appointment = response.data['results'][0]
        self.assertEqual(appointment['status'], 'completed')
        self.assertEqual(appointment['id'], str(self.appointment_completed.id))

    def test_doctor_filter_appointments_by_date_range(self):
        """Test doctor filtering appointments by date range"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Filter for future appointments
        tomorrow = timezone.now() + timedelta(days=1)
        next_week = timezone.now() + timedelta(days=7)
        
        url = reverse('doctor-appointment-list', kwargs={'doctor_id': self.doctor1.id})
        response = self.client.get(url, {
            'date_from': tomorrow.date().isoformat(),
            'date_to': next_week.date().isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)  # Only future appointment
        
        appointment = response.data['results'][0]
        self.assertEqual(appointment['id'], str(self.appointment_future.id))

    def test_doctor_search_appointments_by_patient(self):
        """Test doctor searching appointments by patient name"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('doctor-appointment-list', kwargs={'doctor_id': self.doctor1.id})
        response = self.client.get(url, {'search': 'John'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)
        
        # All results should contain the patient
        for appointment in response.data['results']:
            self.assertIn('John', appointment['patient_name'])

    def test_doctor_get_specific_appointment_details(self):
        """Test doctor getting specific appointment details"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('doctor-appointment-detail', kwargs={
            'doctor_id': self.doctor1.id,
            'appointment_id': self.appointment_completed.id
        })
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify detailed appointment data
        appointment = response.data
        self.assertEqual(appointment['id'], str(self.appointment_completed.id))
        self.assertEqual(appointment['diagnosis'], 'Normal recovery progress')
        self.assertEqual(appointment['treatment_plan'], 'Continue medication')
        self.assertEqual(appointment['status'], 'completed')

    def test_doctor_update_appointment_status(self):
        """Test doctor updating appointment status and medical notes"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('doctor-update-appointment-status', kwargs={
            'doctor_id': self.doctor1.id,
            'appointment_id': self.appointment_today.id
        })
        
        update_data = {
            'status': 'completed',
            'diagnosis': 'Normal heart function detected',
            'treatment_plan': 'Continue healthy lifestyle',
            'prescribed_medications': 'Aspirin 81mg daily',
            'follow_up_instructions': 'Return in 6 months',
            'next_appointment_recommended': True
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify appointment was updated
        updated_appointment = response.data
        self.assertEqual(updated_appointment['status'], 'completed')
        self.assertEqual(updated_appointment['diagnosis'], 'Normal heart function detected')
        self.assertEqual(updated_appointment['prescribed_medications'], 'Aspirin 81mg daily')
        self.assertTrue(updated_appointment['next_appointment_recommended'])

    def test_doctor_access_only_their_appointments(self):
        """Test that doctor can only access their own appointments"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Doctor1 trying to access Doctor2's appointments
        url = reverse('doctor-appointment-list', kwargs={'doctor_id': self.doctor2.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)  # Only doctor2's appointment
        
        appointment = response.data['results'][0]
        self.assertEqual(appointment['healthcare_provider_name'], 'Michael Brown')
        self.assertEqual(appointment['id'], str(self.appointment_doctor2.id))

    def test_unauthorized_access_to_doctor_bookings(self):
        """Test unauthorized access to doctor booking endpoints"""
        # No authentication
        url = reverse('doctor-appointment-list', kwargs={'doctor_id': self.doctor1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_doctor_id(self):
        """Test accessing bookings with invalid doctor ID"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Use non-existent doctor ID
        invalid_id = '99999999-9999-9999-9999-999999999999'
        url = reverse('doctor-appointment-list', kwargs={'doctor_id': invalid_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)  # No appointments found

    def test_doctor_booking_response_structure(self):
        """Test the structure of doctor booking response"""
        token = self.get_auth_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('doctor-appointment-list', kwargs={'doctor_id': self.doctor1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify pagination structure
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        
        # Verify appointment structure
        if response.data['results']:
            appointment = response.data['results'][0]
            required_fields = [
                'id', 'patient_name', 'healthcare_provider_name',
                'appointment_date', 'appointment_type', 'status',
                'chief_complaint', 'consultation_fee'
            ]
            
            for field in required_fields:
                self.assertIn(field, appointment)


class DoctorBookingsIntegrationTest(TestCase):
    """Integration tests for doctor bookings using curl-like requests"""

    def setUp(self):
        """Set up test data for integration tests"""
        # Create test user and provider
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.doctor = HealthcareProvider.objects.create(
            first_name='Test',
            last_name='Doctor',
            email='doctor@test.com',
            specialization='General Practice',
            license_number='TEST123',
            hospital_clinic='Test Hospital'
        )

    def test_curl_like_doctor_bookings_flow(self):
        """Simulate curl-like requests for doctor booking flow"""
        from django.test import Client
        import json
        
        client = Client()
        
        # 1. Login to get token
        login_response = client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        self.assertEqual(login_response.status_code, 200)
        
        # Extract token (simulating curl)
        login_data = json.loads(login_response.content)
        token = login_data['tokens']['access']
        
        # 2. Create appointment
        appointment_data = {
            'healthcare_provider': str(self.doctor.id),
            'appointment_date': '2025-08-15T10:00:00Z',
            'appointment_type': 'consultation',
            'chief_complaint': 'Test appointment',
            'duration_minutes': 30
        }
        
        create_response = client.post(
            '/api/v1/appointments/create/',
            appointment_data,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(create_response.status_code, 201)
        
        # 3. Doctor fetches their bookings
        bookings_response = client.get(
            f'/api/v1/appointments/doctor/{self.doctor.id}/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(bookings_response.status_code, 200)
        
        # Verify booking was created
        bookings_data = json.loads(bookings_response.content)
        self.assertEqual(bookings_data['count'], 1)
        self.assertEqual(bookings_data['results'][0]['chief_complaint'], 'Test appointment')


if __name__ == '__main__':
    import unittest
    unittest.main()
