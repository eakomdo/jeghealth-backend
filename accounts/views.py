from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import User, UserProfile, Role, UserRole
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserUpdateSerializer, UserProfileSerializer, ChangePasswordSerializer,
    UserWithRolesSerializer, RoleSerializer, ComprehensiveUserRegistrationSerializer,
    BasicInformationSerializer, PersonalInformationSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    Creates a new user account and returns user data with JWT tokens.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register a new user",
        description="Create a new user account with email, password, and basic information.",
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Received registration request: %s", request.data)
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                user = serializer.save()
                # Assign default 'user' role
                default_role, created = Role.objects.get_or_create(
                    name='user',
                    defaults={
                        'description': 'Default user role',
                        'permissions': {
                            'can_view_own_data': True,
                            'can_edit_own_profile': True,
                            'can_add_health_metrics': True,
                            'can_view_own_health_metrics': True,
                        }
                    }
                )
                UserRole.objects.create(user=user, role=default_role)
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                # Get user with roles for response
                user_serializer = UserWithRolesSerializer(user)
                logger.info("User registered successfully: %s", request.data.get('email'))
                return Response({
                    'message': 'User registered successfully',
                    'authUser': user_serializer.data,
                    'userProfile': user_serializer.data.get('profile'),
                    'role': {
                        'name': user_serializer.data.get('roles', ['user'])[0] if user_serializer.data.get('roles') else 'user',
                        'permissions': user_serializer.data.get('permissions', {})
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Registration error: %s | Data: %s", str(e), request.data)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    User login endpoint.
    Authenticates user and returns JWT tokens with user data.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="User login",
        description="Authenticate user with email and password, returns JWT tokens.",
        request=UserLoginSerializer,
        tags=["Authentication"]
    )
    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Received login request: %s", request.data.get('email', 'No email provided'))
        
        try:
            serializer = UserLoginSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            user = serializer.validated_data['user']
            logger.info("User login successful: %s", user.email)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Get user with roles for response
            user_serializer = UserWithRolesSerializer(user)
            
            return Response({
                'message': 'Login successful',
                'authUser': user_serializer.data,
                'userProfile': user_serializer.data.get('profile'),
                'role': {
                    'name': user_serializer.data.get('roles', ['user'])[0] if user_serializer.data.get('roles') else 'user',
                    'permissions': user_serializer.data.get('permissions', {})
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Login error: %s | Email: %s", str(e), request.data.get('email', 'No email provided'))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    User logout endpoint.
    Blacklists the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @extend_schema(
        summary="User logout",
        description="Logout user and blacklist refresh token.",
        tags=["Authentication"]
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class ValidateTokenView(APIView):
    """
    Validate JWT token endpoint.
    Returns token validity status without requiring full authentication.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Validate JWT token",
        description="Check if a JWT access token is valid and not expired.",
        tags=["Authentication"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'JWT access token to validate'}
                },
                'required': ['token']
            }
        }
    )
    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response({
                'valid': False,
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Try to decode and validate the token
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            
            # If we get here, token is valid
            return Response({
                'valid': True,
                'user_id': access_token['user_id'],
                'expires_at': access_token['exp']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'valid': False,
                'error': 'Token is invalid or expired'
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile information.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's profile information. Requires authentication token.",
        tags=["User Profile"],
        auth=['Bearer']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user profile",
        description="Update the authenticated user's profile information. Requires authentication token.",
        request=UserUpdateSerializer,
        tags=["User Profile"],
        auth=['Bearer']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Get and update detailed user profile information (medical data, preferences, etc.).
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    @extend_schema(
        summary="Get detailed user profile",
        description="Retrieve the authenticated user's detailed profile (medical info, preferences). Requires authentication token.",
        tags=["User Profile"],
        auth=['Bearer']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update detailed user profile",
        description="Update the authenticated user's detailed profile information. Requires authentication token.",
        tags=["User Profile"],
        auth=['Bearer']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """
    Change user password endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @extend_schema(
        summary="Change password",
        description="Change the authenticated user's password. Requires authentication token.",
        request=ChangePasswordSerializer,
        tags=["User Profile"],
        auth=['Bearer']
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    Get current authenticated user with full profile and role information.
    This matches the getCurrentUser function from your mobile app AuthContext.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @extend_schema(
        summary="Get current user",
        description="Get the currently authenticated user with full profile and role information. Requires authentication token.",
        tags=["Authentication"],
        auth=['Bearer']
    )
    def get(self, request):
        user_serializer = UserWithRolesSerializer(request.user)
        
        return Response({
            'authUser': user_serializer.data,
            'userProfile': user_serializer.data.get('profile'),
            'role': {
                'name': user_serializer.data.get('roles', ['user'])[0] if user_serializer.data.get('roles') else 'user',
                'permissions': user_serializer.data.get('permissions', {})
            }
        }, status=status.HTTP_200_OK)


# Admin-only views for role management
class RoleListCreateView(generics.ListCreateAPIView):
    """
    List and create roles (admin only).
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Only admin users can access this endpoint."""
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @extend_schema(
        summary="List roles",
        description="Get list of all roles (authenticated users can view).",
        tags=["Roles"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create role",
        description="Create a new role (admin only).",
        tags=["Roles"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
@extend_schema(
    summary="Assign role to user",
    description="Assign a role to a user (admin only).",
    request={
        'type': 'object',
        'properties': {
            'user_id': {'type': 'integer'},
            'role_id': {'type': 'integer'},
        },
        'required': ['user_id', 'role_id']
    },
    tags=["Roles"]
)
def assign_role_to_user(request):
    """
    Assign a role to a user (admin only).
    """
    user_id = request.data.get('user_id')
    role_id = request.data.get('role_id')
    
    if not user_id or not role_id:
        return Response({
            'error': 'user_id and role_id are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
        role = Role.objects.get(id=role_id)
        
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'assigned_by': request.user}
        )
        
        if created:
            return Response({
                'message': f'Role "{role.name}" assigned to user "{user.email}" successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': f'User "{user.email}" already has role "{role.name}"'
            }, status=status.HTTP_200_OK)
            
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Role.DoesNotExist:
        return Response({
            'error': 'Role not found'
        }, status=status.HTTP_404_NOT_FOUND)


class ComprehensiveRegisterView(generics.CreateAPIView):
    """
    Comprehensive user registration endpoint that includes profile data.
    Creates a new user account along with profile information in a single request.
    """
    queryset = User.objects.all()
    serializer_class = ComprehensiveUserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register a new user with profile data",
        description="Create a new user account with email, password, basic information, and profile data including gender.",
        tags=["Authentication"],
        examples=[
            OpenApiExample(
                'Registration with profile',
                summary='User registration including profile data',
                description='Example of registering a user with profile information',
                value={
                    "email": "user@example.com",
                    "password": "securepassword123",
                    "password_confirm": "securepassword123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone_number": "+1234567890",
                    "date_of_birth": "1990-01-01",
                    "gender": "M",  # M (Male) or F (Female) - case insensitive
                    "height": 175.5,
                    "weight": 70.0,
                    "blood_type": "O+",
                    "medical_conditions": "None",
                    "current_medications": "None",
                    "allergies": "None"
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Received comprehensive registration request: %s", request.data.get('email'))
        
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                user = serializer.save()
                
                # Assign default 'user' role
                default_role, created = Role.objects.get_or_create(
                    name='user',
                    defaults={
                        'description': 'Default user role',
                        'permissions': {
                            'can_view_own_data': True,
                            'can_edit_own_profile': True,
                            'can_add_health_metrics': True,
                            'can_view_own_health_metrics': True,
                        }
                    }
                )
                UserRole.objects.create(user=user, role=default_role)
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                # Get user with roles for response
                user_serializer = UserWithRolesSerializer(user)
                
                logger.info("User registered successfully with profile: %s", request.data.get('email'))
                return Response({
                    'message': 'User registered successfully with profile data',
                    'authUser': user_serializer.data,
                    'userProfile': user_serializer.data.get('profile'),
                    'role': {
                        'name': user_serializer.data.get('roles', ['user'])[0] if user_serializer.data.get('roles') else 'user',
                        'permissions': user_serializer.data.get('permissions', {})
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error("Comprehensive registration error: %s | Data: %s", str(e), request.data)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BasicInformationView(generics.RetrieveUpdateAPIView):
    """
    Get and update basic user information: full name, email, profile image
    """
    serializer_class = BasicInformationSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get basic user information",
        description="Retrieve basic user information: full name, email, profile image. Requires authentication token.",
        tags=["Basic Information"],
        auth=['Bearer']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update basic user information",
        description="Update basic user information: first name, last name, email, profile image. Requires authentication token.",
        request=BasicInformationSerializer,
        tags=["Basic Information"],
        auth=['Bearer']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PersonalInformationView(generics.RetrieveUpdateAPIView):
    """
    Get and update personal information: age, gender, blood type, height, weight
    """
    serializer_class = PersonalInformationSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get personal information",
        description="Retrieve personal information: age, gender, blood type, height, weight, BMI. Requires authentication token.",
        tags=["Personal Information"],
        auth=['Bearer']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update personal information",
        description="Update personal information: date of birth, gender, blood type, height, weight. Age and BMI are calculated automatically. Requires authentication token.",
        request=PersonalInformationSerializer,
        tags=["Personal Information"],
        auth=['Bearer'],
        examples=[
            OpenApiExample(
                'Update personal info',
                summary='Update personal information',
                description='Example of updating personal information',
                value={
                    "date_of_birth": "1990-01-15",
                    "gender": "M",  # M or F (case insensitive)
                    "height": 175.0,  # in cm
                    "weight": 70.0,   # in kg
                    "blood_type": "O+"
                },
                request_only=True,
            ),
        ]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
