from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Min, Max, Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import HealthMetric, HealthMetricTarget, HealthMetricSummary
from .serializers import (
    HealthMetricSerializer, HealthMetricCreateSerializer,
    HealthMetricTargetSerializer, HealthMetricSummarySerializer,
    HealthMetricBulkCreateSerializer, HealthMetricStatsSerializer,
    HealthMetricFilterSerializer
)


class HealthMetricListCreateView(generics.ListCreateAPIView):
    """
    List and create health metrics.
    Matches the functionality from your mobile app HealthMetricsScreen.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HealthMetricCreateSerializer
        return HealthMetricSerializer
    
    def get_queryset(self):
        """Filter health metrics for the authenticated user."""
        queryset = HealthMetric.objects.filter(user=self.request.user)
        
        # Apply filters
        metric_type = self.request.query_params.get('metric_type')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(recorded_at__gte=start_date)
            except ValueError:
                pass
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(recorded_at__lte=end_date)
            except ValueError:
                pass
        
        is_manual = self.request.query_params.get('is_manual_entry')
        if is_manual is not None:
            queryset = queryset.filter(is_manual_entry=is_manual.lower() == 'true')
        
        return queryset.select_related('device').order_by('-recorded_at')
    
    @extend_schema(
        summary="List health metrics",
        description="Get paginated list of health metrics for the authenticated user.",
        parameters=[
            OpenApiParameter('metric_type', OpenApiTypes.STR, description='Filter by metric type'),
            OpenApiParameter('start_date', OpenApiTypes.DATETIME, description='Filter by start date'),
            OpenApiParameter('end_date', OpenApiTypes.DATETIME, description='Filter by end date'),
            OpenApiParameter('is_manual_entry', OpenApiTypes.BOOL, description='Filter by manual entry'),
            OpenApiParameter('limit', OpenApiTypes.INT, description='Number of results per page'),
        ],
        tags=["Health Metrics"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create health metric",
        description="Add a new health metric reading.",
        tags=["Health Metrics"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class HealthMetricDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific health metric.
    """
    serializer_class = HealthMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HealthMetric.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="Get health metric",
        description="Retrieve a specific health metric.",
        tags=["Health Metrics"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update health metric",
        description="Update a specific health metric.",
        tags=["Health Metrics"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete health metric",
        description="Delete a specific health metric.",
        tags=["Health Metrics"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class HealthMetricBulkCreateView(APIView):
    """
    Bulk create health metrics from IoT devices.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Bulk create health metrics",
        description="Create multiple health metrics from IoT device data.",
        request=HealthMetricBulkCreateSerializer,
        tags=["Health Metrics", "IoT Integration"]
    )
    def post(self, request):
        serializer = HealthMetricBulkCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        return Response({
            'message': f"Successfully created {result['metrics_created']} health metrics",
            'device_id': str(result['device_id']),
            'metrics_created': result['metrics_created'],
        }, status=status.HTTP_201_CREATED)


class HealthMetricStatsView(APIView):
    """
    Get statistics and analytics for health metrics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get health metric statistics",
        description="Get statistical overview of health metrics.",
        parameters=[
            OpenApiParameter('metric_type', OpenApiTypes.STR, description='Filter by metric type'),
            OpenApiParameter('days', OpenApiTypes.INT, description='Number of days to include (default: 30)'),
        ],
        tags=["Health Metrics", "Analytics"]
    )
    def get(self, request):
        user = request.user
        metric_type = request.query_params.get('metric_type')
        days = int(request.query_params.get('days', 30))
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base queryset
        queryset = HealthMetric.objects.filter(
            user=user,
            recorded_at__gte=start_date,
            recorded_at__lte=end_date
        )
        
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
            
            # Get statistics for specific metric type
            stats = queryset.aggregate(
                total_readings=Count('id'),
                average_value=Avg('value'),
                min_value=Min('value'),
                max_value=Max('value')
            )
            
            # Get latest reading
            latest_reading = queryset.order_by('-recorded_at').first()
            
            # Calculate normal range percentage
            normal_count = sum(1 for metric in queryset if metric.is_normal_range())
            total_count = stats['total_readings'] or 0
            normal_range_percentage = (normal_count / total_count * 100) if total_count > 0 else None
            
            # Blood pressure specific stats
            avg_systolic = None
            avg_diastolic = None
            if metric_type == 'blood_pressure':
                bp_stats = queryset.aggregate(
                    avg_systolic=Avg('systolic_value'),
                    avg_diastolic=Avg('diastolic_value')
                )
                avg_systolic = bp_stats['avg_systolic']
                avg_diastolic = bp_stats['avg_diastolic']
            
            # Simple trend calculation (comparing first and last week)
            trend_direction = 'STABLE'
            if total_count >= 2:
                recent_avg = queryset.filter(
                    recorded_at__gte=end_date - timedelta(days=7)
                ).aggregate(avg=Avg('value'))['avg']
                
                older_avg = queryset.filter(
                    recorded_at__lt=end_date - timedelta(days=7)
                ).aggregate(avg=Avg('value'))['avg']
                
                if recent_avg and older_avg:
                    if recent_avg > older_avg * 1.05:  # 5% increase
                        trend_direction = 'UP'
                    elif recent_avg < older_avg * 0.95:  # 5% decrease
                        trend_direction = 'DOWN'
            
            result = {
                'metric_type': metric_type,
                'total_readings': stats['total_readings'],
                'latest_reading': HealthMetricSerializer(latest_reading).data if latest_reading else None,
                'average_value': stats['average_value'],
                'min_value': stats['min_value'],
                'max_value': stats['max_value'],
                'trend_direction': trend_direction,
                'normal_range_percentage': normal_range_percentage,
                'average_systolic': avg_systolic,
                'average_diastolic': avg_diastolic,
            }
            
            return Response(result)
        
        else:
            # Get overview statistics for all metric types
            metric_types = queryset.values_list('metric_type', flat=True).distinct()
            overview = []
            
            for mtype in metric_types:
                type_queryset = queryset.filter(metric_type=mtype)
                stats = type_queryset.aggregate(
                    total_readings=Count('id'),
                    average_value=Avg('value')
                )
                
                latest_reading = type_queryset.order_by('-recorded_at').first()
                
                overview.append({
                    'metric_type': mtype,
                    'total_readings': stats['total_readings'],
                    'latest_reading': HealthMetricSerializer(latest_reading).data if latest_reading else None,
                    'average_value': stats['average_value'],
                })
            
            return Response({
                'period_days': days,
                'total_readings': queryset.count(),
                'metric_types': len(metric_types),
                'overview': overview
            })


class HealthMetricTargetListCreateView(generics.ListCreateAPIView):
    """
    List and create health metric targets/goals.
    """
    serializer_class = HealthMetricTargetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HealthMetricTarget.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="List health metric targets",
        description="Get list of health metric targets/goals for the authenticated user.",
        tags=["Health Targets"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create health metric target",
        description="Create a new health metric target/goal.",
        tags=["Health Targets"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class HealthMetricTargetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific health metric target.
    """
    serializer_class = HealthMetricTargetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HealthMetricTarget.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get metric types",
    description="Get list of available health metric types with their units.",
    tags=["Health Metrics"]
)
def get_metric_types(request):
    """
    Get available health metric types and their units.
    """
    metric_types = []
    for choice in HealthMetric.METRIC_TYPE_CHOICES:
        value, label = choice
        
        # Define common units for each metric type
        units = {
            'blood_pressure': 'mmHg',
            'heart_rate': 'bpm',
            'weight': 'kg',
            'blood_sugar': 'mg/dL',
            'temperature': '°C',
            'oxygen_saturation': '%',
            'steps': 'steps',
            'sleep_hours': 'hours',
            'calories_burned': 'calories',
            'body_fat_percentage': '%',
            'muscle_mass': 'kg',
            'bmi': 'kg/m²',
        }
        
        metric_types.append({
            'value': value,
            'label': label,
            'unit': units.get(value, ''),
            'requires_systolic_diastolic': value == 'blood_pressure'
        })
    
    return Response(metric_types)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Generate health metric summaries",
    description="Generate daily/weekly/monthly summaries for health metrics (admin function).",
    tags=["Health Metrics", "Analytics"]
)
def generate_summaries(request):
    """
    Generate health metric summaries for analytics.
    This would typically be run as a scheduled task.
    """
    # This is a simplified version - in production, this would be a Celery task
    user = request.user
    
    # Generate daily summaries for the last 30 days
    summaries_created = 0
    for days_ago in range(30):
        date = timezone.now().date() - timedelta(days=days_ago)
        
        for metric_type, _ in HealthMetric.METRIC_TYPE_CHOICES:
            # Check if summary already exists
            if HealthMetricSummary.objects.filter(
                user=user,
                metric_type=metric_type,
                period_type='DAILY',
                period_start=date
            ).exists():
                continue
            
            # Get metrics for this day
            day_metrics = HealthMetric.objects.filter(
                user=user,
                metric_type=metric_type,
                recorded_at__date=date
            )
            
            if day_metrics.exists():
                stats = day_metrics.aggregate(
                    count=Count('id'),
                    avg_value=Avg('value'),
                    min_value=Min('value'),
                    max_value=Max('value'),
                    avg_systolic=Avg('systolic_value'),
                    avg_diastolic=Avg('diastolic_value')
                )
                
                HealthMetricSummary.objects.create(
                    user=user,
                    metric_type=metric_type,
                    period_type='DAILY',
                    period_start=date,
                    period_end=date,
                    reading_count=stats['count'],
                    average_value=stats['avg_value'],
                    min_value=stats['min_value'],
                    max_value=stats['max_value'],
                    avg_systolic=stats['avg_systolic'],
                    avg_diastolic=stats['avg_diastolic']
                )
                summaries_created += 1
    
    return Response({
        'message': f'Generated {summaries_created} daily summaries',
        'summaries_created': summaries_created
    })
