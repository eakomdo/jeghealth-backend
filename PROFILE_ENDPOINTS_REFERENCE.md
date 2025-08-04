# JEGHealth Profile Management API Endpoints

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
All profile endpoints require JWT Bearer token authentication:
```
Authorization: Bearer {access_token}
```

---

## 🔐 Authentication Endpoints

### 1. Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response:** Returns user data + JWT tokens

### 2. Register (Basic)
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### 3. Register with Profile
```http
POST /api/v1/auth/register-with-profile/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "gender": "M",
  "height": 175.0,
  "weight": 70.0
}
```

### 4. Logout
```http
POST /api/v1/auth/logout/
Authorization: Bearer {access_token}
```

### 5. Refresh Token
```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "refresh_token_here"
}
```

---

## 👤 Profile Management Endpoints

### 1. Get Current User (Complete Info)
```http
GET /api/v1/auth/current-user/
Authorization: Bearer {access_token}
```
**Returns:** Complete user + profile + roles + permissions

### 2. Get Basic Profile
```http
GET /api/v1/auth/profile/
Authorization: Bearer {access_token}
```
**Returns:** Basic user information

### 3. Update Basic Profile
```http
PATCH /api/v1/auth/profile/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01"
}
```

### 4. Get Detailed Profile
```http
GET /api/v1/auth/profile/details/
Authorization: Bearer {access_token}
```
**Returns:** Medical info, preferences, BMI, etc.

### 5. Update Detailed Profile ⭐
```http
PATCH /api/v1/auth/profile/details/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "gender": "M",
  "height": 175.0,
  "weight": 70.0,
  "blood_type": "O+",
  "medical_conditions": "None",
  "current_medications": "Multivitamin daily",
  "allergies": "None",
  "health_goals": "Maintain fitness",
  "activity_level": "ACTIVE",
  "email_notifications": true,
  "push_notifications": false,
  "health_reminders": true
}
```

### 6. Change Password
```http
POST /api/v1/auth/change-password/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

---

## 📋 Field Specifications

### Editable Profile Fields

| Field | Type | Allowed Values | Notes |
|-------|------|----------------|-------|
| `gender` | string | M, F | Case insensitive (m→M, f→F) |
| `height` | float | Any positive number | In centimeters |
| `weight` | float | Any positive number | In kilograms |
| `blood_type` | string | A+, A-, B+, B-, AB+, AB-, O+, O-, UNKNOWN | |
| `medical_conditions` | text | Any string | Optional |
| `current_medications` | text | Any string | Optional |
| `allergies` | text | Any string | Optional |
| `health_goals` | text | Any string | Optional |
| `activity_level` | string | SEDENTARY, LIGHT, MODERATE, ACTIVE, VERY_ACTIVE | |
| `email_notifications` | boolean | true, false | |
| `push_notifications` | boolean | true, false | |
| `health_reminders` | boolean | true, false | |

### Read-Only Fields

| Field | Description |
|-------|-------------|
| `bmi` | Auto-calculated from height and weight |
| `created_at` | Profile creation timestamp |
| `updated_at` | Last update timestamp |

---

## 🧪 Test Examples

### Complete Integration Flow
```bash
# 1. Login
TOKEN=$(curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}' \
  | jq -r '.tokens.access')

# 2. Get current user
curl -X GET http://127.0.0.1:8000/api/v1/auth/current-user/ \
  -H "Authorization: Bearer $TOKEN"

# 3. Update profile
curl -X PATCH http://127.0.0.1:8000/api/v1/auth/profile/details/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "F",
    "height": 165.0,
    "weight": 60.0,
    "activity_level": "MODERATE"
  }'
```

### Update Individual Fields
```bash
# Update just gender (case insensitive)
curl -X PATCH http://127.0.0.1:8000/api/v1/auth/profile/details/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"gender": "m"}'

# Update just notifications
curl -X PATCH http://127.0.0.1:8000/api/v1/auth/profile/details/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_notifications": false, "push_notifications": true}'

# Update weight (BMI will auto-calculate)
curl -X PATCH http://127.0.0.1:8000/api/v1/auth/profile/details/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"weight": 65.0}'
```

---

## ⚠️ Error Handling

### Common Validation Errors
```json
// Invalid gender
{
  "gender": ["Invalid gender choice. Must be either 'M' (Male) or 'F' (Female)"]
}

// Invalid activity level
{
  "activity_level": ["\"INVALID\" is not a valid choice."]
}

// Authentication error
{
  "detail": "Authentication credentials were not provided."
}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created (registration)
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid/expired token)
- `403`: Forbidden (insufficient permissions)

---

## 📚 Additional Resources

- **Swagger Documentation**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc Documentation**: `http://127.0.0.1:8000/api/redoc/`
- **OpenAPI Schema**: `http://127.0.0.1:8000/api/schema/`

---

## 🔗 Quick Reference URLs

```
# Authentication
POST   /api/v1/auth/login/
POST   /api/v1/auth/register/
POST   /api/v1/auth/register-with-profile/
POST   /api/v1/auth/logout/
POST   /api/v1/auth/token/refresh/

# Profile Management
GET    /api/v1/auth/current-user/           # Complete user info
GET    /api/v1/auth/profile/                # Basic profile
PATCH  /api/v1/auth/profile/                # Update basic profile
GET    /api/v1/auth/profile/details/        # Detailed profile
PATCH  /api/v1/auth/profile/details/        # Update detailed profile ⭐
POST   /api/v1/auth/change-password/        # Change password
```

The main profile update endpoint you'll use most is:
**`PATCH /api/v1/auth/profile/details/`** ⭐
