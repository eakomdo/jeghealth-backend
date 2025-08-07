# JegHealth Backend - Provider Endpoints Documentation

## Overview
This document provides a comprehensive guide to all provider-related endpoints in the JegHealth backend system, including authentication, profile management, and provider-specific functionalities.

## Base URLs
- **API Base**: `http://localhost:8001/api/v1`
- **Auth Base**: `http://localhost:8001/api/v1/auth`
- **Providers Base**: `http://localhost:8001/api/v1/providers`

## Provider Authentication Endpoints

### 1. Provider Registration
**Endpoint**: `POST /api/v1/auth/provider/register/`
**Description**: Register a new healthcare provider with credentials and professional information.
**Authentication**: Not required

**Request Body**:
```json
{
    "email": "doctor@example.com",
    "username": "dr_username",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!",
    "first_name": "Dr. John",
    "last_name": "Smith",
    "phone_number": "+14155552671",
    "specialization": "Cardiology",
    "license_number": "MD123456789",
    "years_of_experience": 10,
    "consultation_fee": "150.00",
    "bio": "Experienced cardiologist",
    "hospital_clinic": "City Heart Center",
    "address": "123 Medical St, Health City, HC 12345"
}
```

**Success Response**:
```json
{
    "message": "Healthcare provider registered successfully",
    "authUser": {
        "id": 7,
        "email": "doctor@example.com",
        "username": "dr_username",
        "first_name": "Dr. John",
        "last_name": "Smith",
        "roles": ["provider"],
        "permissions": {...}
    },
    "userProfile": null,
    "role": {
        "name": "provider",
        "permissions": {...}
    },
    "tokens": {
        "access": "eyJhbGciOiJIUzI1...",
        "refresh": "eyJhbGciOiJIUzI1..."
    }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8001/api/v1/auth/provider/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "username": "dr_username",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!",
    "first_name": "Dr. John",
    "last_name": "Smith",
    "phone_number": "+14155552671",
    "specialization": "Cardiology",
    "license_number": "MD123456789",
    "years_of_experience": 10,
    "consultation_fee": "150.00",
    "bio": "Experienced cardiologist",
    "hospital_clinic": "City Heart Center",
    "address": "123 Medical St"
  }'
```

### 2. Provider Login
**Endpoint**: `POST /api/v1/auth/login/`
**Description**: Login with provider credentials (same endpoint as regular users)
**Authentication**: Not required

**Request Body**:
```json
{
    "email": "doctor@example.com",
    "password": "SecurePassword123!"
}
```

**Success Response**:
```json
{
    "message": "Login successful",
    "authUser": {...},
    "userProfile": null,
    "role": {
        "name": "provider",
        "permissions": {...}
    },
    "tokens": {
        "access": "eyJhbGciOiJIUzI1...",
        "refresh": "eyJhbGciOiJIUzI1..."
    }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "password": "SecurePassword123!"
  }'
```

## Provider Profile Management

### 3. Get Provider Profile
**Endpoint**: `GET /api/v1/auth/provider/profile/`
**Description**: Get the authenticated provider's profile information
**Authentication**: Required (Provider only)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Success Response**:
```json
{
    "id": "ea32c365-2a62-435c-8e56-8622a1971262",
    "first_name": "Dr. John",
    "last_name": "Smith",
    "email": "doctor@example.com",
    "phone_number": "+14155552671",
    "specialization": "Cardiology",
    "license_number": "MD123456789",
    "hospital_clinic": "City Heart Center",
    "address": "123 Medical St",
    "bio": "Experienced cardiologist",
    "years_of_experience": 10,
    "consultation_fee": "150.00",
    "is_active": true,
    "created_at": "2025-08-07T08:26:28.992860Z",
    "updated_at": "2025-08-07T08:26:32.365681Z"
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8001/api/v1/auth/provider/profile/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json"
```

### 4. Update Provider Profile
**Endpoint**: `PATCH /api/v1/auth/provider/profile/`
**Description**: Update the authenticated provider's profile information
**Authentication**: Required (Provider only)

**Request Body** (partial update supported):
```json
{
    "bio": "Updated bio: Experienced cardiologist specializing in interventional procedures",
    "consultation_fee": "175.00",
    "years_of_experience": 12
}
```

**cURL Example**:
```bash
curl -X PATCH http://localhost:8001/api/v1/auth/provider/profile/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Updated bio",
    "consultation_fee": "175.00"
  }'
```

### 5. Provider Dashboard
**Endpoint**: `GET /api/v1/auth/provider/dashboard/`
**Description**: Get dashboard statistics and data for healthcare providers
**Authentication**: Required (Provider only)

**Success Response**:
```json
{
    "provider": {
        "id": "ea32c365-2a62-435c-8e56-8622a1971262",
        "full_name": "Dr. John Smith",
        "specialization": "Cardiology",
        "years_of_experience": 10,
        "consultation_fee": "175.00"
    },
    "statistics": {
        "total_appointments": 15,
        "today_appointments": 3,
        "week_appointments": 8,
        "month_appointments": 15,
        "upcoming_appointments": 5,
        "completed_appointments": 10
    },
    "recent_appointments": [
        {
            "id": "appointment-uuid",
            "patient_name": "John Doe",
            "appointment_date": "2025-08-08T10:00:00Z",
            "status": "scheduled",
            "chief_complaint": "Regular checkup",
            "duration_minutes": 30
        }
    ]
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8001/api/v1/auth/provider/dashboard/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json"
```

## Provider Directory Endpoints

### 6. List All Providers
**Endpoint**: `GET /api/v1/providers/`
**Description**: Get a paginated list of all active healthcare providers
**Authentication**: Required

**Query Parameters**:
- `search`: Search by name, specialization, or hospital
- `specialization`: Filter by specialization
- `hospital_clinic`: Filter by hospital/clinic
- `ordering`: Sort by fields (last_name, specialization, years_of_experience, consultation_fee)
- `page`: Page number for pagination

**Success Response**:
```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "provider-uuid",
            "full_name": "Dr. John Smith",
            "specialization": "Cardiology",
            "hospital_names": "",
            "years_of_experience": 10,
            "consultation_fee": "175.00",
            "is_active": true
        }
    ]
}
```

**cURL Example**:
```bash
# List all providers
curl -X GET http://localhost:8001/api/v1/providers/ \
  -H "Authorization: Bearer <your_access_token>"

# Search providers
curl -X GET "http://localhost:8001/api/v1/providers/?search=cardiology" \
  -H "Authorization: Bearer <your_access_token>"

# Filter and sort
curl -X GET "http://localhost:8001/api/v1/providers/?specialization=Cardiology&ordering=consultation_fee" \
  -H "Authorization: Bearer <your_access_token>"
```

### 7. Get Provider Details
**Endpoint**: `GET /api/v1/providers/{provider_id}/`
**Description**: Get detailed information about a specific provider
**Authentication**: Required

**Success Response**:
```json
{
    "id": "provider-uuid",
    "first_name": "Dr. John",
    "last_name": "Smith",
    "full_name": "Dr. John Smith",
    "email": "doctor@example.com",
    "phone_number": "+14155552671",
    "specialization": "Cardiology",
    "license_number": "MD123456789",
    "hospitals": [],
    "hospital_names": "",
    "primary_hospital": null,
    "hospital_clinic": "City Heart Center",
    "address": "123 Medical St",
    "bio": "Experienced cardiologist",
    "years_of_experience": 10,
    "consultation_fee": "175.00",
    "is_active": true,
    "created_at": "2025-08-07T08:26:28.992860Z",
    "updated_at": "2025-08-07T08:26:32.365681Z"
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8001/api/v1/providers/ea32c365-2a62-435c-8e56-8622a1971262/ \
  -H "Authorization: Bearer <your_access_token>"
```

### 8. Create New Provider (Admin)
**Endpoint**: `POST /api/v1/providers/`
**Description**: Create a new provider profile (requires authentication)
**Authentication**: Required

**Request Body**:
```json
{
    "email": "new.doctor@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "specialization": "Pediatrics",
    "license_number": "MD987654321",
    "years_of_experience": 8,
    "consultation_fee": "125.00",
    "bio": "Experienced pediatrician",
    "hospital_clinic": "Children's Hospital",
    "address": "456 Kids St",
    "phone_number": "+19876543210"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8001/api/v1/providers/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new.doctor@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "specialization": "Pediatrics",
    "license_number": "MD987654321",
    "years_of_experience": 8,
    "consultation_fee": "125.00",
    "bio": "Experienced pediatrician",
    "hospital_clinic": "Children Hospital",
    "address": "456 Kids St",
    "phone_number": "+19876543210"
  }'
```

### 9. Provider Search/Autocomplete
**Endpoint**: `GET /api/v1/providers/search/`
**Description**: Autocomplete search for provider names and specializations
**Authentication**: Required

**Query Parameters**:
- `q`: Search query (minimum 2 characters)

**Success Response**:
```json
{
    "suggestions": [
        {
            "id": "provider-uuid",
            "name": "Dr. John Smith",
            "specialization": "Cardiology",
            "hospitals": [
                {
                    "id": "hospital-uuid",
                    "name": "City Heart Center",
                    "city": "Health City"
                }
            ]
        }
    ]
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8001/api/v1/providers/search/?q=Dr" \
  -H "Authorization: Bearer <your_access_token>"
```

### 10. Provider Dropdown List
**Endpoint**: `GET /api/v1/providers/dropdown/`
**Description**: Get providers in dropdown format for frontend selection
**Authentication**: Required

**Query Parameters**:
- `specialization`: Filter by specialization
- `hospital_id`: Filter by hospital ID

**Success Response**:
```json
[
    {
        "id": "provider-uuid",
        "full_name": "Dr. John Smith",
        "specialization": "Cardiology",
        "hospital_names": ""
    }
]
```

**cURL Example**:
```bash
# All providers for dropdown
curl -X GET http://localhost:8001/api/v1/providers/dropdown/ \
  -H "Authorization: Bearer <your_access_token>"

# Filtered dropdown
curl -X GET "http://localhost:8001/api/v1/providers/dropdown/?specialization=cardiology" \
  -H "Authorization: Bearer <your_access_token>"
```

### 11. Providers by Hospital
**Endpoint**: `GET /api/v1/providers/hospital/{hospital_id}/`
**Description**: Get all providers working at a specific hospital
**Authentication**: Required

**Success Response**:
```json
{
    "hospital": {
        "id": "hospital-uuid",
        "name": "City Heart Center",
        "city": "Health City"
    },
    "providers": [
        {
            "id": "provider-uuid",
            "full_name": "Dr. John Smith",
            "specialization": "Cardiology",
            "hospital_names": ""
        }
    ]
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8001/api/v1/providers/hospital/hospital-uuid/ \
  -H "Authorization: Bearer <your_access_token>"
```

## Token Management

### 12. Token Validation
**Endpoint**: `POST /api/v1/auth/token/validate/`
**Description**: Validate the current access token
**Authentication**: Required

**cURL Example**:
```bash
curl -X POST http://localhost:8001/api/v1/auth/token/validate/ \
  -H "Authorization: Bearer <your_access_token>"
```

### 13. Token Refresh
**Endpoint**: `POST /api/v1/auth/token/refresh/`
**Description**: Refresh the access token using refresh token
**Authentication**: Not required

**Request Body**:
```json
{
    "refresh": "your_refresh_token_here"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8001/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token_here"
  }'
```

## Error Responses

### Common Error Codes:
- **400 Bad Request**: Invalid data or validation errors
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Example Error Response:
```json
{
    "error": "Provider profile not found"
}
```

### Validation Error Response:
```json
{
    "phone_number": ["The phone number entered is not valid."],
    "email": ["This field is required."]
}
```

## Testing Scripts

### Comprehensive Test
Run the comprehensive test script to test all endpoints:
```bash
./test_comprehensive_provider_endpoints.sh
```

### Quick Test
Run the quick test script for daily testing:
```bash
./test_provider_quick.sh
```

## Frontend Integration Notes

1. **Store Tokens**: Save both access and refresh tokens securely
2. **Role Checking**: Check the `role.name` field to verify provider access
3. **Token Refresh**: Implement automatic token refresh when access token expires
4. **Error Handling**: Handle all possible error responses gracefully
5. **Permissions**: Use the `permissions` object to control UI features

## Next Steps for Frontend Development

1. Implement provider registration/login screens
2. Create provider dashboard with statistics
3. Build provider profile management interface  
4. Integrate with appointment booking system
5. Add provider search and listing functionality
6. Implement real-time notifications for appointments
7. Add provider availability management

## API Documentation

For interactive API documentation, visit:
- **Swagger UI**: http://localhost:8001/api/docs/
- **ReDoc**: http://localhost:8001/api/redoc/

---

*Last updated: August 7, 2025*
