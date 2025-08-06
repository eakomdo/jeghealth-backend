from rest_framework import generics, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import logging

from providers.models import HealthcareProvider
from .models import Appointment, AppointmentFile, AppointmentRating
from .serializers import (
    AppointmentSerializer, AppointmentListSerializer, AppointmentCreateSerializer,
    AppointmentUpdateSerializer, AppointmentFileSerializer, AppointmentRatingSerializer,
    AppointmentStatsSerializer
)

logger = logging.getLogger(__name__)


class AppointmentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Appointment Views
class AppointmentListView(generics.ListAPIView):
    """List user's appointments"""
    serializer_class = AppointmentListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'appointment_type', 'priority', 'healthcare_provider', 'payment_status']
    search_fields = ['chief_complaint', 'healthcare_provider__first_name', 'healthcare_provider__last_name']
    ordering_fields = ['appointment_date', 'created_at', 'status']
    ordering = ['-appointment_date']
    pagination_class = AppointmentPagination

    def get_queryset(self):
        """Filter appointments by current user"""
        queryset = Appointment.objects.filter(patient=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(appointment_date__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(appointment_date__lte=end_date)
            except ValueError:
                pass
        
        # Filter by upcoming appointments
        if self.request.query_params.get('upcoming'):
            queryset = queryset.filter(appointment_date__gte=timezone.now())
        
        # Filter by past appointments
        if self.request.query_params.get('past'):
            queryset = queryset.filter(appointment_date__lt=timezone.now())
            
        # Filter by today's appointments
        if self.request.query_params.get('today'):
            today = timezone.now().date()
            queryset = queryset.filter(appointment_date__date=today)
            
        return queryset.select_related('healthcare_provider', 'created_by').prefetch_related('files', 'rating')


class AppointmentDetailView(generics.RetrieveAPIView):
    """Get appointment details"""
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter appointments by current user"""
        return Appointment.objects.filter(patient=self.request.user).select_related(
            'healthcare_provider', 'created_by'
        ).prefetch_related('files', 'rating')


class AppointmentCreateView(generics.CreateAPIView):
    """Create a new appointment"""
    serializer_class = AppointmentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Save appointment with current user as patient"""
        try:
            appointment = serializer.save()
            logger.info(f"Appointment created: {appointment.id} for user {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error creating appointment for user {self.request.user.email}: {str(e)}")
            raise


class AppointmentUpdateView(generics.UpdateAPIView):
    """Update an appointment"""
    serializer_class = AppointmentUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter appointments by current user"""
        return Appointment.objects.filter(patient=self.request.user)

    def perform_update(self, serializer):
        """Update appointment with logging"""
        try:
            appointment = serializer.save()
            logger.info(f"Appointment updated: {appointment.id} by user {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error updating appointment for user {self.request.user.email}: {str(e)}")
            raise


class AppointmentDeleteView(generics.DestroyAPIView):
    """Cancel an appointment"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter appointments by current user"""
        return Appointment.objects.filter(patient=self.request.user)

    def perform_destroy(self, instance):
        """Cancel appointment instead of deleting"""
        if not instance.can_be_cancelled():
            raise serializers.ValidationError("This appointment cannot be cancelled")
        
        instance.status = 'cancelled'
        instance.save(update_fields=['status', 'updated_at'])
        logger.info(f"Appointment cancelled: {instance.id} by user {self.request.user.email}")


# Appointment Files Views
class AppointmentFileListView(generics.ListCreateAPIView):
    """List and upload appointment files"""
    serializer_class = AppointmentFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get files for specific appointment owned by current user"""
        appointment_id = self.kwargs.get('appointment_id')
        return AppointmentFile.objects.filter(
            appointment_id=appointment_id,
            appointment__patient=self.request.user
        ).select_related('uploaded_by', 'appointment')

    def perform_create(self, serializer):
        """Create file for specific appointment"""
        appointment_id = self.kwargs.get('appointment_id')
        try:
            # Verify appointment belongs to current user
            appointment = Appointment.objects.get(id=appointment_id, patient=self.request.user)
            serializer.save(appointment=appointment)
            logger.info(f"File uploaded for appointment {appointment_id} by user {self.request.user.email}")
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("Appointment not found")


class AppointmentFileDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete appointment file"""
    serializer_class = AppointmentFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get files for appointments owned by current user"""
        return AppointmentFile.objects.filter(
            appointment__patient=self.request.user
        ).select_related('uploaded_by', 'appointment')


# Appointment Rating Views
class AppointmentRatingCreateView(generics.CreateAPIView):
    """Create appointment rating"""
    serializer_class = AppointmentRatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Create rating for specific appointment"""
        appointment_id = self.kwargs.get('appointment_id')
        try:
            # Verify appointment belongs to current user and is completed
            appointment = Appointment.objects.get(
                id=appointment_id, 
                patient=self.request.user,
                status='completed'
            )
            serializer.save(appointment=appointment)
            logger.info(f"Rating created for appointment {appointment_id} by user {self.request.user.email}")
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("Completed appointment not found")


class AppointmentRatingUpdateView(generics.UpdateAPIView):
    """Update appointment rating"""
    serializer_class = AppointmentRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get ratings for appointments owned by current user"""
        return AppointmentRating.objects.filter(
            appointment__patient=self.request.user
        ).select_related('appointment')


# Statistics and Analytics Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_stats(request):
    """Get appointment statistics for current user"""
    try:
        user = request.user
        appointments = Appointment.objects.filter(patient=user)
        
        # Basic counts
        total_appointments = appointments.count()
        scheduled_appointments = appointments.filter(status='scheduled').count()
        completed_appointments = appointments.filter(status='completed').count()
        cancelled_appointments = appointments.filter(status='cancelled').count()
        
        # Date-based counts
        now = timezone.now()
        upcoming_appointments = appointments.filter(appointment_date__gte=now).count()
        today_appointments = appointments.filter(appointment_date__date=now.date()).count()
        
        # Ratings and financial stats
        completed_apps = appointments.filter(status='completed')
        ratings = AppointmentRating.objects.filter(appointment__in=completed_apps)
        average_rating = ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        total_spent = completed_apps.aggregate(
            total=Sum('consultation_fee')
        )['total'] or 0
        
        # Most visited specialization
        specialization_stats = appointments.values(
            'healthcare_provider__specialization'
        ).annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        most_visited_specialization = (
            specialization_stats['healthcare_provider__specialization'] 
            if specialization_stats else "None"
        )
        
        # Appointment types distribution
        appointment_types = appointments.values('appointment_type').annotate(
            count=Count('id')
        )
        appointment_types_distribution = {
            item['appointment_type']: item['count'] 
            for item in appointment_types
        }
        
        # Monthly appointments for the last 6 months
        six_months_ago = now - timedelta(days=180)
        monthly_data = appointments.filter(
            appointment_date__gte=six_months_ago
        ).annotate(
            month=TruncMonth('appointment_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        monthly_appointments = [
            {
                'month': item['month'].strftime('%Y-%m'),
                'count': item['count']
            }
            for item in monthly_data
        ]
        
        stats_data = {
            'total_appointments': total_appointments,
            'scheduled_appointments': scheduled_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'upcoming_appointments': upcoming_appointments,
            'today_appointments': today_appointments,
            'average_rating': round(average_rating, 2),
            'total_spent': total_spent,
            'most_visited_specialization': most_visited_specialization,
            'appointment_types_distribution': appointment_types_distribution,
            'monthly_appointments': monthly_appointments,
        }
        
        serializer = AppointmentStatsSerializer(stats_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating appointment stats for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to generate appointment statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reschedule_appointment(request, appointment_id):
    """Reschedule an appointment"""
    try:
        appointment = Appointment.objects.get(id=appointment_id, patient=request.user)
        
        if not appointment.can_be_rescheduled():
            return Response(
                {'error': 'This appointment cannot be rescheduled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_date = request.data.get('appointment_date')
        if not new_date:
            return Response(
                {'error': 'New appointment date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_date = datetime.fromisoformat(new_date.replace('Z', '+00:00'))
            if new_date <= timezone.now():
                return Response(
                    {'error': 'New appointment date must be in the future'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.appointment_date = new_date
        appointment.status = 'rescheduled'
        appointment.save(update_fields=['appointment_date', 'status', 'updated_at'])
        
        serializer = AppointmentSerializer(appointment)
        logger.info(f"Appointment {appointment_id} rescheduled by user {request.user.email}")
        
        return Response(serializer.data)
        
    except Appointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error rescheduling appointment {appointment_id} for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to reschedule appointment'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_appointments(request):
    """Get upcoming appointments for current user"""
    try:
        now = timezone.now()
        upcoming = Appointment.objects.filter(
            patient=request.user,
            appointment_date__gte=now,
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date')[:5]
        
        serializer = AppointmentListSerializer(upcoming, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error fetching upcoming appointments for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to fetch upcoming appointments'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_history(request):
    """Get appointment history for current user"""
    try:
        history = Appointment.objects.filter(
            patient=request.user,
            status='completed'
        ).order_by('-appointment_date')
        
        # Apply pagination
        paginator = AppointmentPagination()
        page = paginator.paginate_queryset(history, request)
        
        if page is not None:
            serializer = AppointmentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = AppointmentSerializer(history, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error fetching appointment history for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to fetch appointment history'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Frontend Compatible Appointment Views
class FrontendAppointmentListCreateView(generics.ListCreateAPIView):
    """
    Frontend-compatible appointment view that accepts the exact structure from your React Native app
    """
    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AppointmentListSerializer
        return AppointmentCreateSerializer
    
    def get_queryset(self):
        queryset = Appointment.objects.filter(patient=self.request.user)
        
        # Frontend-compatible query parameters
        status = self.request.query_params.get('status')
        appointment_type = self.request.query_params.get('type')
        specialty = self.request.query_params.get('specialty')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        search = self.request.query_params.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        if appointment_type:
            queryset = queryset.filter(appointment_type=appointment_type)
        if specialty:
            queryset = queryset.filter(healthcare_provider__specialization__icontains=specialty)
        if date_from:
            queryset = queryset.filter(appointment_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(appointment_date__date__lte=date_to)
        if search:
            queryset = queryset.filter(
                Q(healthcare_provider__first_name__icontains=search) |
                Q(healthcare_provider__last_name__icontains=search) |
                Q(healthcare_provider__hospital_clinic__icontains=search) |
                Q(reason__icontains=search)
            )
        
        return queryset.order_by('-appointment_date')

    def create(self, request, *args, **kwargs):
        """Handle frontend appointment creation with the exact structure you provided"""
        try:
            # Transform frontend data to backend structure
            frontend_data = request.data.copy()
            
            # Map frontend fields to backend fields
            backend_data = {
                'patient': request.user.id,
                'appointment_date': frontend_data.get('appointmentDate'),
                'appointment_type': frontend_data.get('appointmentType', 'consultation'),
                'reason': frontend_data.get('reason', ''),
                'notes': frontend_data.get('notes', ''),
                'duration_minutes': frontend_data.get('duration', 30),
                'status': 'scheduled'
            }
            
            # Handle healthcare provider creation/retrieval
            doctor_name = frontend_data.get('doctorName', '')
            specialty = frontend_data.get('specialty', 'General Practice')
            clinic_name = frontend_data.get('clinicName', '')
            clinic_address = frontend_data.get('clinicAddress', '')
            phone_number = frontend_data.get('phoneNumber', '')
            
            if doctor_name:
                # Split doctor name into first and last name
                name_parts = doctor_name.replace('Dr. ', '').split(' ')
                first_name = name_parts[0] if name_parts else ''
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                
                healthcare_provider, created = HealthcareProvider.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    defaults={
                        'specialization': specialty,
                        'phone_number': phone_number,
                        'hospital_clinic': clinic_name,
                        'address': clinic_address,
                        'email': f"{first_name.lower()}.{last_name.lower()}@clinic.com" if first_name and last_name else '',
                        'is_active': True
                    }
                )
                backend_data['healthcare_provider'] = healthcare_provider.id
            
            serializer = AppointmentCreateSerializer(data=backend_data, context={'request': request})
            if serializer.is_valid():
                appointment = serializer.save()
                return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creating appointment: {str(e)}")
            return Response({'error': 'Failed to create appointment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def frontend_appointment_choices(request):
    """Get available choices for appointment fields in frontend-compatible format"""
    appointment_types = [
        {'value': 'consultation', 'label': 'General Consultation'},
        {'value': 'follow_up', 'label': 'Follow-up'},
        {'value': 'emergency', 'label': 'Emergency'},
        {'value': 'checkup', 'label': 'Routine Checkup'},
        {'value': 'surgery', 'label': 'Surgery'},
        {'value': 'therapy', 'label': 'Therapy'},
        {'value': 'vaccination', 'label': 'Vaccination'},
        {'value': 'diagnostic', 'label': 'Diagnostic Test'}
    ]
    
    specialties = [
        'General Practice', 'Cardiology', 'Dermatology', 'Endocrinology',
        'Gastroenterology', 'Neurology', 'Oncology', 'Orthopedics',
        'Pediatrics', 'Psychiatry', 'Radiology', 'Surgery'
    ]
    
    status_choices = [
        {'value': 'scheduled', 'label': 'Scheduled'},
        {'value': 'confirmed', 'label': 'Confirmed'},
        {'value': 'completed', 'label': 'Completed'},
        {'value': 'cancelled', 'label': 'Cancelled'}
    ]
    
    return Response({
        'appointmentTypes': appointment_types,
        'specialties': specialties,
        'statusValues': status_choices
    })


# Doctor-specific appointment views
class DoctorAppointmentListView(generics.ListAPIView):
    """
    List all appointments for a specific doctor
    URL: /api/v1/appointments/doctor/{doctor_id}/
    """
    serializer_class = AppointmentListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'appointment_type', 'priority', 'payment_status']
    search_fields = ['patient__first_name', 'patient__last_name', 'chief_complaint']
    ordering_fields = ['appointment_date', 'created_at', 'status']
    ordering = ['appointment_date']
    pagination_class = AppointmentPagination

    def get_queryset(self):
        """Filter appointments by the specified doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        queryset = Appointment.objects.filter(healthcare_provider_id=doctor_id)
        
        # Additional query parameters
        status = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(appointment_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(appointment_date__date__lte=date_to)
            
        return queryset


class DoctorTodaysAppointmentsView(generics.ListAPIView):
    """
    Get today's appointments for a specific doctor
    URL: /api/v1/appointments/doctor/{doctor_id}/today/
    """
    serializer_class = AppointmentListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination
    
    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        today = timezone.now().date()
        return Appointment.objects.filter(
            healthcare_provider_id=doctor_id,
            appointment_date__date=today
        ).order_by('appointment_date')


class DoctorUpcomingAppointmentsView(generics.ListAPIView):
    """
    Get upcoming appointments for a specific doctor (next 7 days)
    URL: /api/v1/appointments/doctor/{doctor_id}/upcoming/
    """
    serializer_class = AppointmentListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination
    
    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        now = timezone.now()
        week_from_now = now + timedelta(days=7)
        return Appointment.objects.filter(
            healthcare_provider_id=doctor_id,
            appointment_date__range=[now, week_from_now],
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date')


class DoctorAppointmentStatsView(generics.GenericAPIView):
    """
    Get appointment statistics for a specific doctor
    URL: /api/v1/appointments/doctor/{doctor_id}/stats/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, doctor_id):
        try:
            # Get doctor info
            doctor = HealthcareProvider.objects.get(id=doctor_id)
            
            # Basic counts
            total_appointments = Appointment.objects.filter(healthcare_provider_id=doctor_id).count()
            completed_appointments = Appointment.objects.filter(
                healthcare_provider_id=doctor_id, 
                status='completed'
            ).count()
            cancelled_appointments = Appointment.objects.filter(
                healthcare_provider_id=doctor_id, 
                status='cancelled'
            ).count()
            
            # Today's appointments
            today = timezone.now().date()
            todays_appointments = Appointment.objects.filter(
                healthcare_provider_id=doctor_id,
                appointment_date__date=today
            ).count()
            
            # This month's appointments
            current_month = timezone.now().replace(day=1)
            this_month_appointments = Appointment.objects.filter(
                healthcare_provider_id=doctor_id,
                appointment_date__gte=current_month
            ).count()
            
            # Average rating
            from django.db.models import Avg
            avg_rating = Appointment.objects.filter(
                healthcare_provider_id=doctor_id,
                rating__isnull=False
            ).aggregate(avg_rating=Avg('rating__rating'))['avg_rating']
            
            # Revenue (completed appointments)
            total_revenue = Appointment.objects.filter(
                healthcare_provider_id=doctor_id,
                status='completed',
                payment_status='paid'
            ).aggregate(total=Sum('consultation_fee'))['total'] or 0
            
            return Response({
                'doctor': {
                    'id': str(doctor.id),
                    'name': doctor.full_name,
                    'specialization': doctor.specialization,
                },
                'statistics': {
                    'total_appointments': total_appointments,
                    'completed_appointments': completed_appointments,
                    'cancelled_appointments': cancelled_appointments,
                    'todays_appointments': todays_appointments,
                    'this_month_appointments': this_month_appointments,
                    'average_rating': round(avg_rating or 0, 1),
                    'total_revenue': float(total_revenue),
                    'completion_rate': round(
                        (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0, 1
                    )
                }
            })
            
        except HealthcareProvider.DoesNotExist:
            return Response(
                {'error': 'Healthcare provider not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting doctor stats: {str(e)}")
            return Response(
                {'error': 'Failed to fetch statistics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def doctor_update_appointment_status(request, doctor_id, appointment_id):
    """
    Allow doctor to update appointment status and add notes
    URL: /api/v1/appointments/doctor/{doctor_id}/appointment/{appointment_id}/update-status/
    """
    try:
        appointment = get_object_or_404(
            Appointment, 
            id=appointment_id, 
            healthcare_provider_id=doctor_id
        )
        
        # Update status if provided
        new_status = request.data.get('status')
        if new_status and new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
        
        # Update medical details if provided
        if request.data.get('diagnosis'):
            appointment.diagnosis = request.data.get('diagnosis')
        if request.data.get('treatment_plan'):
            appointment.treatment_plan = request.data.get('treatment_plan')
        if request.data.get('prescribed_medications'):
            appointment.prescribed_medications = request.data.get('prescribed_medications')
        if request.data.get('follow_up_instructions'):
            appointment.follow_up_instructions = request.data.get('follow_up_instructions')
        if 'next_appointment_recommended' in request.data:
            appointment.next_appointment_recommended = request.data.get('next_appointment_recommended')
            
        appointment.save()
        
        return Response(AppointmentSerializer(appointment).data)
        
    except Exception as e:
        logger.error(f"Error updating appointment status: {str(e)}")
        return Response(
            {'error': 'Failed to update appointment'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class DoctorAppointmentDetailView(generics.RetrieveAPIView):
    """
    Get detailed appointment information for a doctor
    URL: /api/v1/appointments/doctor/{doctor_id}/appointment/{appointment_id}/
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        doctor_id = self.kwargs.get('doctor_id')
        appointment_id = self.kwargs.get('appointment_id')
        return get_object_or_404(
            Appointment, 
            id=appointment_id, 
            healthcare_provider_id=doctor_id
        )
