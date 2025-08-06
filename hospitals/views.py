from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Hospital
from .serializers import (
    HospitalSerializer,
    HospitalListSerializer,
    HospitalCreateSerializer,
    HospitalDropdownSerializer
)


class HospitalListCreateView(generics.ListCreateAPIView):
    """
    GET: List all active hospitals
    POST: Create new hospital
    """
    queryset = Hospital.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city', 'region', 'specialties']
    ordering_fields = ['name', 'city', 'established_year', 'bed_capacity']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HospitalCreateSerializer
        return HospitalListSerializer

    def get_queryset(self):
        queryset = Hospital.objects.filter(is_active=True)
        
        # Filter by query parameters
        hospital_type = self.request.query_params.get('type')
        city = self.request.query_params.get('city')
        region = self.request.query_params.get('region')
        emergency_services = self.request.query_params.get('emergency_services')
        
        if hospital_type:
            queryset = queryset.filter(hospital_type=hospital_type)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if region:
            queryset = queryset.filter(region__icontains=region)
        if emergency_services:
            queryset = queryset.filter(emergency_services=emergency_services.lower() == 'true')
            
        return queryset


class HospitalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve hospital details
    PUT/PATCH: Update hospital
    DELETE: Deactivate hospital
    """
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        """Instead of hard delete, just deactivate the hospital"""
        instance.is_active = False
        instance.save()
        return Response(
            {'message': 'Hospital deactivated successfully'}, 
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hospital_dropdown_list(request):
    """
    Get hospitals in dropdown format for frontend selection
    URL: /api/v1/hospitals/dropdown/
    """
    hospitals = Hospital.objects.filter(is_active=True).order_by('name')
    
    # Optional filtering
    city = request.query_params.get('city')
    hospital_type = request.query_params.get('type')
    
    if city:
        hospitals = hospitals.filter(city__icontains=city)
    if hospital_type:
        hospitals = hospitals.filter(hospital_type=hospital_type)
    
    serializer = HospitalDropdownSerializer(hospitals, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hospital_search_autocomplete(request):
    """
    Autocomplete search for hospital names
    URL: /api/v1/hospitals/search/
    """
    query = request.query_params.get('q', '')
    
    if len(query) < 2:
        return Response({'suggestions': []})
    
    hospitals = Hospital.objects.filter(
        name__icontains=query,
        is_active=True
    ).order_by('name')[:10]
    
    suggestions = [
        {
            'id': str(hospital.id),
            'name': hospital.name,
            'city': hospital.city,
            'type': hospital.hospital_type
        }
        for hospital in hospitals
    ]
    
    return Response({'suggestions': suggestions})
