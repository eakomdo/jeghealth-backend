from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from .models import HealthcareProvider
from .serializers import (
    HealthcareProviderSerializer,
    HealthcareProviderCreateSerializer, 
    HealthcareProviderListSerializer,
    ProviderDropdownSerializer
)


class HealthcareProviderListCreateView(generics.ListCreateAPIView):
    """
    GET: List all active healthcare providers
    POST: Create new healthcare provider
    """
    queryset = HealthcareProvider.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'hospital_clinic']
    search_fields = ['first_name', 'last_name', 'specialization', 'hospital_clinic']
    ordering_fields = ['last_name', 'specialization', 'years_of_experience', 'consultation_fee']
    ordering = ['last_name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HealthcareProviderCreateSerializer
        return HealthcareProviderListSerializer


class HealthcareProviderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve healthcare provider details
    PUT/PATCH: Update healthcare provider
    DELETE: Deactivate healthcare provider
    """
    queryset = HealthcareProvider.objects.all()
    serializer_class = HealthcareProviderSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        """Instead of hard delete, just deactivate the provider"""
        # This preserves appointment history
        instance.is_active = False
        instance.save()
        return Response(
            {'message': 'Healthcare provider deactivated successfully'}, 
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_dropdown_list(request):
    """
    Get providers in dropdown format for frontend selection
    URL: /api/v1/providers/dropdown/
    """
    providers = HealthcareProvider.objects.filter(is_active=True).order_by('last_name', 'first_name')
    
    # Optional filtering
    specialization = request.query_params.get('specialization')
    hospital_id = request.query_params.get('hospital_id')
    
    if specialization:
        providers = providers.filter(specialization__icontains=specialization)
    if hospital_id:
        providers = providers.filter(hospitals__id=hospital_id)
    
    serializer = ProviderDropdownSerializer(providers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_search_autocomplete(request):
    """
    Autocomplete search for provider names
    URL: /api/v1/providers/search/
    """
    query = request.query_params.get('q', '')
    
    if len(query) < 2:
        return Response({'suggestions': []})
    
    providers = HealthcareProvider.objects.filter(
        models.Q(first_name__icontains=query) | 
        models.Q(last_name__icontains=query) |
        models.Q(specialization__icontains=query),
        is_active=True
    ).order_by('last_name', 'first_name')[:10]
    
    suggestions = [
        {
            'id': str(provider.id),
            'name': provider.full_name,
            'specialization': provider.specialization,
            'hospitals': [
                {'id': str(h.id), 'name': h.name, 'city': h.city} 
                for h in provider.hospitals.all()
            ]
        }
        for provider in providers
    ]
    
    return Response({'suggestions': suggestions})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def providers_by_hospital(request, hospital_id):
    """
    Get all providers working at a specific hospital
    URL: /api/v1/providers/hospital/{hospital_id}/
    """
    try:
        from hospitals.models import Hospital
        hospital = Hospital.objects.get(id=hospital_id, is_active=True)
        providers = hospital.doctors.filter(is_active=True)
        serializer = ProviderDropdownSerializer(providers, many=True)
        
        return Response({
            'hospital': {
                'id': str(hospital.id),
                'name': hospital.name,
                'city': hospital.city
            },
            'providers': serializer.data
        })
    except Hospital.DoesNotExist:
        return Response({'error': 'Hospital not found'}, status=404)
