# Frontend Integration - API Endpoints Reference

## 🚀 JegHealth Backend API Endpoints

**Base URL**: `http://localhost:8001/api/v1`  
**Authentication**: Bearer Token (JWT)

---

## 🔐 Authentication Endpoints

### 1. User Registration
```
POST /auth/register/
```
**Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "Password123!",
  "password_confirm": "Password123!",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Response:**
```json
{
  "message": "User registered successfully",
  "authUser": {...},
  "userProfile": {...},
  "role": {"name": "user"},
  "tokens": {
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token"
  }
}
```

### 2. User Login
```
POST /auth/login/
```
**Body:**
```json
{
  "email": "user@example.com",
  "password": "Password123!"
}
```
**Response:**
```json
{
  "message": "Login successful",
  "authUser": {...},
  "userProfile": {...},
  "role": {"name": "user"},
  "tokens": {
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token"
  }
}
```

### 3. Provider Registration
```
POST /auth/provider/register/
```
**Body:**
```json
{
  "email": "doctor@example.com",
  "username": "dr_username",
  "password": "Password123!",
  "password_confirm": "Password123!",
  "first_name": "Dr. John",
  "last_name": "Smith",
  "phone_number": "+14155552671",
  "specialization": "Cardiology",
  "license_number": "MD123456789",
  "years_of_experience": 10,
  "consultation_fee": "150.00",
  "bio": "Experienced cardiologist",
  "hospital_clinic": "City Heart Center",
  "address": "123 Medical St, Health City"
}
```

### 4. Token Refresh
```
POST /auth/token/refresh/
```
**Body:**
```json
{
  "refresh": "refresh_token_here"
}
```

### 5. Logout
```
POST /auth/logout/
Headers: Authorization: Bearer <token>
```

---

## 👤 User Profile Endpoints

### 6. Get Current User
```
GET /auth/current-user/
Headers: Authorization: Bearer <token>
```

### 7. Get User Profile
```
GET /auth/profile/
Headers: Authorization: Bearer <token>
```

### 8. Update User Profile
```
PATCH /auth/profile/
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "first_name": "Updated Name",
  "last_name": "Updated Last",
  "phone_number": "+14155551234"
}
```

### 9. Get Basic Information
```
GET /auth/profile/basic/
Headers: Authorization: Bearer <token>
```

### 10. Update Basic Information
```
PATCH /auth/profile/basic/
Headers: Authorization: Bearer <token>
```

### 11. Get Personal Information
```
GET /auth/profile/personal/
Headers: Authorization: Bearer <token>
```

### 12. Update Personal Information
```
PATCH /auth/profile/personal/
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "date_of_birth": "1990-01-15",
  "gender": "M",
  "height": 175.0,
  "weight": 70.0,
  "blood_type": "O+"
}
```

### 13. Change Password
```
POST /auth/change-password/
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!",
  "new_password_confirm": "NewPassword123!"
}
```

---

## 🏥 Provider Endpoints

### 14. Get Provider Profile
```
GET /auth/provider/profile/
Headers: Authorization: Bearer <provider_token>
```

### 15. Update Provider Profile
```
PATCH /auth/provider/profile/
Headers: Authorization: Bearer <provider_token>
```
**Body:**
```json
{
  "bio": "Updated bio",
  "consultation_fee": "175.00",
  "specialization": "Updated Specialization"
}
```

### 16. Provider Dashboard
```
GET /auth/provider/dashboard/
Headers: Authorization: Bearer <provider_token>
```
**Response:**
```json
{
  "provider": {
    "id": "uuid",
    "full_name": "Dr. John Smith",
    "specialization": "Cardiology",
    "consultation_fee": "175.00"
  },
  "statistics": {
    "total_appointments": 15,
    "today_appointments": 3,
    "week_appointments": 8,
    "upcoming_appointments": 5,
    "completed_appointments": 10
  },
  "recent_appointments": [...]
}
```

### 17. List All Providers
```
GET /providers/
Headers: Authorization: Bearer <token>
Query Params: ?search=cardiology&ordering=consultation_fee&page=1
```

### 18. Get Provider Details
```
GET /providers/{provider_id}/
Headers: Authorization: Bearer <token>
```

### 19. Provider Search/Autocomplete
```
GET /providers/search/?q=Dr
Headers: Authorization: Bearer <token>
```

### 20. Provider Dropdown
```
GET /providers/dropdown/
Headers: Authorization: Bearer <token>
Query Params: ?specialization=cardiology
```

### 21. Providers by Hospital
```
GET /providers/hospital/{hospital_id}/
Headers: Authorization: Bearer <token>
```

---

## 📅 Appointment Endpoints

### 22. List User Appointments
```
GET /appointments/
Headers: Authorization: Bearer <token>
```

### 23. Create Appointment
```
POST /appointments/
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "healthcare_provider": "provider_uuid",
  "appointment_date": "2025-08-10T10:00:00Z",
  "chief_complaint": "Regular checkup",
  "duration_minutes": 30,
  "notes": "Follow-up visit"
}
```

### 24. Get Appointment Details
```
GET /appointments/{appointment_id}/
Headers: Authorization: Bearer <token>
```

### 25. Update Appointment
```
PATCH /appointments/{appointment_id}/
Headers: Authorization: Bearer <token>
```

### 26. Cancel Appointment
```
DELETE /appointments/{appointment_id}/
Headers: Authorization: Bearer <token>
```

### 27. Provider Appointments
```
GET /appointments/provider-appointments/
Headers: Authorization: Bearer <provider_token>
```

---

## 📊 Health Metrics Endpoints

### 28. List Health Metrics
```
GET /health-metrics/
Headers: Authorization: Bearer <token>
```

### 29. Create Health Metric
```
POST /health-metrics/
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "metric_type": "blood_pressure",
  "value": "120/80",
  "unit": "mmHg",
  "recorded_date": "2025-08-07T10:00:00Z",
  "notes": "Morning reading"
}
```

### 30. Get Health Metric Details
```
GET /health-metrics/{metric_id}/
Headers: Authorization: Bearer <token>
```

---

## 🏥 Hospital Endpoints

### 31. List Hospitals
```
GET /hospitals/
Headers: Authorization: Bearer <token>
```

### 32. Hospital Search
```
GET /hospitals/search/?q=general
Headers: Authorization: Bearer <token>
```

### 33. Hospital Dropdown
```
GET /hospitals/dropdown/
Headers: Authorization: Bearer <token>
```

---

## 📱 IoT Device Endpoints

### 34. List IoT Devices
```
GET /iot-devices/
Headers: Authorization: Bearer <token>
```

### 35. Add IoT Device
```
POST /iot-devices/
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "device_name": "Blood Pressure Monitor",
  "device_type": "blood_pressure",
  "manufacturer": "Omron",
  "model": "HEM-7120"
}
```

---

## 💊 Medication Endpoints

### 36. List Medications
```
GET /medications/
Headers: Authorization: Bearer <token>
```

### 37. Add Medication
```
POST /medications/
Headers: Authorization: Bearer <token>
```

---

## 🔧 Frontend Integration Guide

### Authentication Flow
```javascript
// 1. Login/Register
const response = await fetch('/api/v1/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
const { tokens, authUser, role } = data;

// 2. Store tokens
localStorage.setItem('access_token', tokens.access);
localStorage.setItem('refresh_token', tokens.refresh);
localStorage.setItem('user_role', role.name);

// 3. Use token in subsequent requests
const apiCall = await fetch('/api/v1/providers/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  }
});
```

### Error Handling
```javascript
const handleApiCall = async (url, options) => {
  try {
    const response = await fetch(url, options);
    
    if (response.status === 401) {
      // Token expired, try refresh
      await refreshToken();
      // Retry original request
      return fetch(url, options);
    }
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'API Error');
    }
    
    return response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};
```

### Token Refresh
```javascript
const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('/api/v1/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken })
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
};
```

---

## 📱 React/React Native Examples

### Login Component
```jsx
import React, { useState } from 'react';

const LoginForm = () => {
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('http://localhost:8001/api/v1/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Store tokens and user data
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('user_role', data.role.name);
        
        // Redirect based on role
        if (data.role.name === 'provider') {
          navigate('/provider-dashboard');
        } else {
          navigate('/user-dashboard');
        }
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        placeholder="Email"
        value={credentials.email}
        onChange={(e) => setCredentials({
          ...credentials,
          email: e.target.value
        })}
      />
      <input
        type="password"
        placeholder="Password"
        value={credentials.password}
        onChange={(e) => setCredentials({
          ...credentials,
          password: e.target.value
        })}
      />
      <button type="submit">Login</button>
    </form>
  );
};
```

### Provider List Component
```jsx
const ProviderList = () => {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8001/api/v1/providers/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      setProviders(data.results);
    } catch (error) {
      console.error('Failed to fetch providers:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {providers.map(provider => (
        <div key={provider.id} className="provider-card">
          <h3>{provider.full_name}</h3>
          <p>{provider.specialization}</p>
          <p>Fee: ${provider.consultation_fee}</p>
          <p>Experience: {provider.years_of_experience} years</p>
        </div>
      ))}
    </div>
  );
};
```

---

## 🔍 Testing Your Integration

Use these curl commands to test endpoints:

```bash
# Test login
curl -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Test authenticated endpoint
curl -X GET http://localhost:8001/api/v1/providers/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Run the test scripts:
```bash
# Quick test
./test_provider_quick.sh

# Comprehensive test
./test_comprehensive_provider_endpoints.sh
```

---

## 📚 Additional Resources

- **Full API Documentation**: [PROVIDER_ENDPOINTS_DOCUMENTATION.md](./PROVIDER_ENDPOINTS_DOCUMENTATION.md)
- **Interactive API Docs**: http://localhost:8001/api/docs/
- **ReDoc**: http://localhost:8001/api/redoc/

---

*Ready for frontend integration! 🚀*
