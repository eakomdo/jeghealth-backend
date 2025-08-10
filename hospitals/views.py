from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend

from .models import Hospital, Department
from .serializers import (
    HospitalSerializer, HospitalListSerializer,
    DepartmentSerializer, HospitalSearchSerializer
)

class HospitalViewSet(viewsets.ReadOnlyModelViewSet):
    """Hospital API endpoints"""
    queryset = Hospital.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hospital_type', 'emergency_services', 'has_icu', 'has_surgery']
    search_fields = ['name', 'city', 'state', 'address']
    ordering_fields = ['name', 'city', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HospitalListSerializer
        return HospitalSerializer
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced hospital search"""
        serializer = HospitalSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        
        # Filter by location
        location = serializer.validated_data.get('location')
        if location:
            queryset = queryset.filter(
                Q(city__icontains=location) |
                Q(state__icontains=location) |
                Q(postal_code__icontains=location)
            )
        
        # Filter by hospital type
        hospital_type = serializer.validated_data.get('hospital_type')
        if hospital_type:
            queryset = queryset.filter(hospital_type=hospital_type)
        
        # Filter by services
        if serializer.validated_data.get('emergency_services'):
            queryset = queryset.filter(emergency_services=True)
        
        if serializer.validated_data.get('has_icu'):
            queryset = queryset.filter(has_icu=True)
        
        if serializer.validated_data.get('has_surgery'):
            queryset = queryset.filter(has_surgery=True)
        
        # Filter by specialties/departments
        specialties = serializer.validated_data.get('specialties', [])
        if specialties:
            queryset = queryset.filter(
                departments__department_type__in=specialties,
                departments__is_active=True
            ).distinct()
        
        # Serialize results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HospitalListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HospitalListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def departments(self, request, pk=None):
        """Get hospital departments"""
        hospital = self.get_object()
        departments = hospital.departments.filter(is_active=True)
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find nearby hospitals (placeholder for geolocation)"""
        # This would integrate with a geocoding service in production
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius', 25)  # miles
        
        if not lat or not lng:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # For now, return all hospitals (would implement geospatial queries in production)
        queryset = self.get_queryset()[:10]  # Limit to 10 results
        serializer = HospitalListSerializer(queryset, many=True)
        
        return Response({
            'location': {'lat': lat, 'lng': lng, 'radius': radius},
            'hospitals': serializer.data
        })

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Department API endpoints"""
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['hospital', 'department_type']
    search_fields = ['name', 'description']
