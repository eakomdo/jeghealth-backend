# Provider Dashboard - Essential Endpoints

**Base URL**: `http://localhost:8001/api/v1`

## 🔐 Provider Authentication

### 1. Provider Login
```
POST /auth/login/
```
**Body:**
```json
{
  "email": "doctor@example.com",
  "password": "password123"
}
```
**Response:**
```json
{
  "message": "Login successful",
  "authUser": {
    "id": 7,
    "email": "doctor@example.com",
    "first_name": "Dr. John",
    "last_name": "Smith",
    "roles": ["provider"]
  },
  "role": {
    "name": "provider"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### 2. Provider Registration
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

## 🏥 Provider Dashboard Endpoints

### 3. Provider Dashboard (Main)
```
GET /auth/provider/dashboard/
Headers: Authorization: Bearer <provider_token>
```
**Response:**
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

### 4. Provider Profile
```
GET /auth/provider/profile/
Headers: Authorization: Bearer <provider_token>
```
**Response:**
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

### 5. Update Provider Profile
```
PATCH /auth/provider/profile/
Headers: Authorization: Bearer <provider_token>
```
**Body:**
```json
{
  "bio": "Updated bio: Experienced cardiologist specializing in interventional procedures",
  "consultation_fee": "175.00",
  "specialization": "Interventional Cardiology"
}
```

### 6. Provider Appointments
```
GET /appointments/provider-appointments/
Headers: Authorization: Bearer <provider_token>
```
**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": "appointment-uuid",
      "patient": {
        "id": "patient-uuid",
        "full_name": "John Doe",
        "email": "john@example.com"
      },
      "appointment_date": "2025-08-08T10:00:00Z",
      "status": "scheduled",
      "chief_complaint": "Regular checkup",
      "duration_minutes": 30,
      "notes": "Follow-up visit",
      "created_at": "2025-08-07T08:26:28Z"
    }
  ]
}
```

---

## 🚀 React Component Example

### Provider Dashboard Component
```jsx
import React, { useState, useEffect } from 'react';

const ProviderDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8001/api/v1/auth/provider/dashboard/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading dashboard...</div>;

  const { provider, statistics, recent_appointments } = dashboardData;

  return (
    <div className="provider-dashboard">
      {/* Provider Info Card */}
      <div className="provider-info">
        <h1>Welcome, {provider.full_name}</h1>
        <p>{provider.specialization}</p>
        <p>{provider.years_of_experience} years experience</p>
        <p>Consultation Fee: ${provider.consultation_fee}</p>
      </div>

      {/* Statistics Cards */}
      <div className="statistics-grid">
        <div className="stat-card">
          <h3>{statistics.total_appointments}</h3>
          <p>Total Appointments</p>
        </div>
        <div className="stat-card">
          <h3>{statistics.today_appointments}</h3>
          <p>Today's Appointments</p>
        </div>
        <div className="stat-card">
          <h3>{statistics.upcoming_appointments}</h3>
          <p>Upcoming Appointments</p>
        </div>
        <div className="stat-card">
          <h3>{statistics.completed_appointments}</h3>
          <p>Completed Appointments</p>
        </div>
      </div>

      {/* Recent Appointments */}
      <div className="recent-appointments">
        <h2>Recent Appointments</h2>
        {recent_appointments.map(appointment => (
          <div key={appointment.id} className="appointment-card">
            <h4>{appointment.patient_name}</h4>
            <p>Date: {new Date(appointment.appointment_date).toLocaleString()}</p>
            <p>Status: {appointment.status}</p>
            <p>Complaint: {appointment.chief_complaint}</p>
            <p>Duration: {appointment.duration_minutes} minutes</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProviderDashboard;
```

---

## 🔧 API Helper Functions

### Authentication & API Calls
```javascript
// Store provider token after login
const handleProviderLogin = async (credentials) => {
  const response = await fetch('http://localhost:8001/api/v1/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });
  
  const data = await response.json();
  
  if (data.role.name === 'provider') {
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('user_role', 'provider');
    // Redirect to provider dashboard
    window.location.href = '/provider-dashboard';
  }
};

// Authenticated API call helper
const apiCall = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  return fetch(`http://localhost:8001/api/v1${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
};

// Get dashboard data
const getDashboardData = () => apiCall('/auth/provider/dashboard/');

// Get provider profile
const getProviderProfile = () => apiCall('/auth/provider/profile/');

// Update provider profile
const updateProviderProfile = (data) => apiCall('/auth/provider/profile/', {
  method: 'PATCH',
  body: JSON.stringify(data)
});

// Get provider appointments
const getProviderAppointments = () => apiCall('/appointments/provider-appointments/');
```

---

## 🧪 Test the Endpoints

```bash
# Quick test to verify all provider dashboard endpoints work
./test_provider_quick.sh
```

**Manual curl tests:**

```bash
# 1. Login as provider
curl -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "doctor@example.com", "password": "password123"}'

# 2. Get dashboard data (use token from login)
curl -X GET http://localhost:8001/api/v1/auth/provider/dashboard/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 3. Get provider profile
curl -X GET http://localhost:8001/api/v1/auth/provider/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 4. Get provider appointments
curl -X GET http://localhost:8001/api/v1/appointments/provider-appointments/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🎯 Implementation Steps

1. **Implement provider login** - Get JWT token and verify role is "provider"
2. **Create dashboard component** - Fetch and display statistics and recent appointments  
3. **Add profile management** - Allow providers to update their information
4. **Implement appointments view** - Show provider's upcoming and past appointments
5. **Add real-time updates** - Refresh data periodically or use WebSockets

That's it! These 6 endpoints give you everything needed for a complete provider dashboard. 🚀
