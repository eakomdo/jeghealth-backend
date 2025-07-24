from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, Case, When, FloatField
from django.db.models.functions import TruncMonth, TruncDate
from datetime import datetime, timedelta
import logging

from .models import (
    MedicationCategory, Medication, UserMedication, MedicationLog,
    MedicationReminder, MedicationInteraction
)
from .serializers import (
    MedicationCategorySerializer, MedicationSerializer, MedicationListSerializer,
    UserMedicationSerializer, UserMedicationListSerializer, MedicationLogSerializer,
    MedicationReminderSerializer, MedicationInteractionSerializer,
    MedicationStatsSerializer, AdherenceReportSerializer
)

logger = logging.getLogger(__name__)


class MedicationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Medication Category Views
class MedicationCategoryListView(generics.ListAPIView):
    """List all medication categories"""
    queryset = MedicationCategory.objects.all()
    serializer_class = MedicationCategorySerializer
    permission_classes = [IsAuthenticated]


# Medication Views
class MedicationListView(generics.ListAPIView):
    """List all available medications"""
    queryset = Medication.objects.filter(is_active=True)
    serializer_class = MedicationListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'generic_name', 'brand_name', 'manufacturer']
    ordering_fields = ['name', 'generic_name', 'form']
    ordering = ['name']
    pagination_class = MedicationPagination

    def get_queryset(self):
        """Filter medications by various parameters"""
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by form
        form = self.request.query_params.get('form')
        if form:
            queryset = queryset.filter(form=form)
        
        # Filter by prescription requirement
        requires_prescription = self.request.query_params.get('requires_prescription')
        if requires_prescription is not None:
            queryset = queryset.filter(requires_prescription=requires_prescription.lower() == 'true')
        
        return queryset.select_related('category')


class MedicationDetailView(generics.RetrieveAPIView):
    """Get medication details"""
    queryset = Medication.objects.filter(is_active=True)
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated]


# User Medication Views
class UserMedicationListView(generics.ListAPIView):
    """List user's medications"""
    serializer_class = UserMedicationListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['medication__name', 'medication__generic_name', 'prescribed_by']
    ordering_fields = ['start_date', 'medication__name', 'status']
    ordering = ['-start_date']
    pagination_class = MedicationPagination

    def get_queryset(self):
        """Filter medications by current user"""
        queryset = UserMedication.objects.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by active medications
        if self.request.query_params.get('active_only'):
            today = timezone.now().date()
            queryset = queryset.filter(
                status='active'
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today)
            )
        
        # Filter by medications needing refill
        if self.request.query_params.get('needs_refill'):
            queryset = queryset.filter(remaining_quantity__lte=7, remaining_quantity__gt=0)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_date__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_date__lte=end_date)
            except ValueError:
                pass
        
        return queryset.select_related('medication', 'medication__category').prefetch_related('reminders')


class UserMedicationDetailView(generics.RetrieveAPIView):
    """Get user medication details"""
    serializer_class = UserMedicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter medications by current user"""
        return UserMedication.objects.filter(user=self.request.user).select_related(
            'medication', 'medication__category'
        ).prefetch_related('reminders')


class UserMedicationCreateView(generics.CreateAPIView):
    """Add a new medication for the user"""
    serializer_class = UserMedicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Save medication with current user"""
        try:
            medication = serializer.save()
            logger.info(f"Medication added: {medication.id} for user {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error adding medication for user {self.request.user.email}: {str(e)}")
            raise


class UserMedicationUpdateView(generics.UpdateAPIView):
    """Update user medication"""
    serializer_class = UserMedicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter medications by current user"""
        return UserMedication.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """Update medication with logging"""
        try:
            medication = serializer.save()
            logger.info(f"Medication updated: {medication.id} by user {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error updating medication for user {self.request.user.email}: {str(e)}")
            raise


class UserMedicationDeleteView(generics.DestroyAPIView):
    """Remove user medication"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter medications by current user"""
        return UserMedication.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        """Set medication as discontinued instead of deleting"""
        instance.status = 'discontinued'
        instance.save(update_fields=['status', 'updated_at'])
        logger.info(f"Medication discontinued: {instance.id} by user {self.request.user.email}")


# Medication Log Views
class MedicationLogListView(generics.ListCreateAPIView):
    """List and create medication logs"""
    serializer_class = MedicationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['scheduled_time', 'actual_time', 'status']
    ordering = ['-scheduled_time']
    pagination_class = MedicationPagination

    def get_queryset(self):
        """Filter logs by current user's medications"""
        queryset = MedicationLog.objects.filter(user_medication__user=self.request.user)
        
        # Filter by medication
        medication_id = self.request.query_params.get('medication')
        if medication_id:
            queryset = queryset.filter(user_medication_id=medication_id)
        
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
                queryset = queryset.filter(scheduled_time__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(scheduled_time__lte=end_date)
            except ValueError:
                pass
        
        return queryset.select_related('user_medication', 'user_medication__medication')


class MedicationLogDetailView(generics.RetrieveUpdateAPIView):
    """Get or update medication log"""
    serializer_class = MedicationLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter logs by current user's medications"""
        return MedicationLog.objects.filter(
            user_medication__user=self.request.user
        ).select_related('user_medication', 'user_medication__medication')


# Statistics and Analytics Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medication_stats(request):
    """Get medication statistics for current user"""
    try:
        user = request.user
        user_medications = UserMedication.objects.filter(user=user)
        
        # Basic counts
        total_medications = user_medications.count()
        active_medications = user_medications.filter(status='active').count()
        
        # Expired medications
        today = timezone.now().date()
        expired_medications = user_medications.filter(
            end_date__lt=today
        ).count()
        
        # Medications needing refill
        medications_needing_refill = user_medications.filter(
            remaining_quantity__lte=7,
            remaining_quantity__gt=0,
            status='active'
        ).count()
        
        # Adherence calculation (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        logs = MedicationLog.objects.filter(
            user_medication__user=user,
            scheduled_time__gte=thirty_days_ago
        )
        
        total_scheduled = logs.count()
        taken_doses = logs.filter(status='taken').count()
        missed_doses = logs.filter(status='missed').count()
        
        adherence_rate = (taken_doses / total_scheduled * 100) if total_scheduled > 0 else 0
        
        # Missed doses last week
        one_week_ago = timezone.now() - timedelta(days=7)
        missed_doses_last_week = logs.filter(
            scheduled_time__gte=one_week_ago,
            status='missed'
        ).count()
        
        # On-time percentage
        on_time_logs = logs.filter(status='taken').filter(
            actual_time__lte=timezone.now()
        ).count()
        on_time_percentage = (on_time_logs / taken_doses * 100) if taken_doses > 0 else 0
        
        # Most common side effect
        side_effects = user_medications.exclude(
            side_effects_experienced=''
        ).values_list('side_effects_experienced', flat=True)
        
        most_common_side_effect = "None reported"
        if side_effects:
            # Simple implementation - in production, you'd want more sophisticated analysis
            all_effects = ' '.join(side_effects).lower()
            common_effects = ['nausea', 'headache', 'dizziness', 'fatigue', 'drowsiness']
            for effect in common_effects:
                if effect in all_effects:
                    most_common_side_effect = effect.title()
                    break
        
        # Medication categories distribution
        categories = user_medications.filter(
            medication__category__isnull=False
        ).values(
            'medication__category__name'
        ).annotate(
            count=Count('id')
        )
        
        medication_categories = {
            item['medication__category__name']: item['count']
            for item in categories
        }
        
        # Frequency distribution
        frequency_dist = user_medications.values('frequency').annotate(
            count=Count('id')
        )
        
        frequency_distribution = {
            item['frequency']: item['count']
            for item in frequency_dist
        }
        
        # Monthly adherence for last 6 months
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_data = logs.filter(
            scheduled_time__gte=six_months_ago
        ).annotate(
            month=TruncMonth('scheduled_time')
        ).values('month').annotate(
            total=Count('id'),
            taken=Count(Case(When(status='taken', then=1)))
        ).annotate(
            adherence=Case(
                When(total=0, then=0.0),
                default=Count(Case(When(status='taken', then=1))) * 100.0 / Count('id'),
                output_field=FloatField()
            )
        ).order_by('month')
        
        monthly_adherence = [
            {
                'month': item['month'].strftime('%Y-%m'),
                'adherence': round(item['adherence'], 2)
            }
            for item in monthly_data
        ]
        
        stats_data = {
            'total_medications': total_medications,
            'active_medications': active_medications,
            'expired_medications': expired_medications,
            'medications_needing_refill': medications_needing_refill,
            'adherence_rate': round(adherence_rate, 2),
            'missed_doses_last_week': missed_doses_last_week,
            'on_time_percentage': round(on_time_percentage, 2),
            'most_common_side_effect': most_common_side_effect,
            'medication_categories': medication_categories,
            'frequency_distribution': frequency_distribution,
            'monthly_adherence': monthly_adherence,
        }
        
        serializer = MedicationStatsSerializer(stats_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating medication stats for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to generate medication statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def adherence_report(request):
    """Get detailed adherence report for date range"""
    try:
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        logs = MedicationLog.objects.filter(
            user_medication__user=user,
            scheduled_time__date__gte=start_date,
            scheduled_time__date__lte=end_date
        ).select_related('user_medication', 'user_medication__medication')
        
        total_scheduled_doses = logs.count()
        taken_doses = logs.filter(status='taken').count()
        missed_doses = logs.filter(status='missed').count()
        
        adherence_percentage = (taken_doses / total_scheduled_doses * 100) if total_scheduled_doses > 0 else 0
        
        # Per-medication breakdown
        medication_adherence = logs.values(
            'user_medication__medication__name'
        ).annotate(
            total=Count('id'),
            taken=Count(Case(When(status='taken', then=1))),
            missed=Count(Case(When(status='missed', then=1)))
        ).annotate(
            adherence=Case(
                When(total=0, then=0.0),
                default=Count(Case(When(status='taken', then=1))) * 100.0 / Count('id'),
                output_field=FloatField()
            )
        )
        
        medications = [
            {
                'name': item['user_medication__medication__name'],
                'total_doses': item['total'],
                'taken_doses': item['taken'],
                'missed_doses': item['missed'],
                'adherence_percentage': round(item['adherence'], 2)
            }
            for item in medication_adherence
        ]
        
        # Daily adherence
        daily_adherence = logs.annotate(
            date=TruncDate('scheduled_time')
        ).values('date').annotate(
            total=Count('id'),
            taken=Count(Case(When(status='taken', then=1)))
        ).annotate(
            adherence=Case(
                When(total=0, then=0.0),
                default=Count(Case(When(status='taken', then=1))) * 100.0 / Count('id'),
                output_field=FloatField()
            )
        ).order_by('date')
        
        daily_data = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'adherence': round(item['adherence'], 2),
                'total_doses': item['total'],
                'taken_doses': item['taken']
            }
            for item in daily_adherence
        ]
        
        report_data = {
            'start_date': start_date,
            'end_date': end_date,
            'total_scheduled_doses': total_scheduled_doses,
            'taken_doses': taken_doses,
            'missed_doses': missed_doses,
            'adherence_percentage': round(adherence_percentage, 2),
            'medications': medications,
            'daily_adherence': daily_data,
        }
        
        serializer = AdherenceReportSerializer(report_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating adherence report for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to generate adherence report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_medication_intake(request):
    """Quick log medication intake"""
    try:
        medication_id = request.data.get('medication_id')
        status_value = request.data.get('status', 'taken')
        notes = request.data.get('notes', '')
        
        if not medication_id:
            return Response(
                {'error': 'medication_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user owns the medication
        try:
            user_medication = UserMedication.objects.get(id=medication_id, user=request.user)
        except UserMedication.DoesNotExist:
            return Response(
                {'error': 'Medication not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create log entry
        log_data = {
            'user_medication': user_medication.id,
            'scheduled_time': timezone.now(),
            'actual_time': timezone.now() if status_value == 'taken' else None,
            'status': status_value,
            'notes': notes
        }
        
        serializer = MedicationLogSerializer(data=log_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Medication intake logged: {medication_id} by user {request.user.email}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error logging medication intake for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to log medication intake'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
