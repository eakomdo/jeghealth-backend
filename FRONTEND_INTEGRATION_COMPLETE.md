# 🏥 Healthcare Provider Frontend Integration Guide

## Overview
This document provides complete specifications for frontend integration with the healthcare provider backend system. All endpoints have been tested with real data and are ready for production use.

---

## 🔗 Base Configuration

```javascript
// API Configuration
const API_BASE_URL = 'http://localhost:8001/api/v1';
const AUTH_BASE_URL = 'http://localhost:8001/api/v1/auth';

// Headers for authenticated requests
const getAuthHeaders = (token) => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`
});
```

---

## 📝 1. Provider Registration Page Update

### **Endpoint:** `POST /api/v1/auth/provider/register/`

### **Required Form Fields:**
```javascript
const providerRegistrationFields = {
  // Personal Information
  professional_title: {
    type: 'select',
    required: true,
    options: [
      { value: 'Dr.', label: 'Dr. (Doctor)' },
      { value: 'Prof.', label: 'Prof. (Professor)' },
      { value: 'RN', label: 'RN (Registered Nurse)' },
      { value: 'LPN', label: 'LPN (Licensed Practical Nurse)' },
      { value: 'NP', label: 'NP (Nurse Practitioner)' },
      { value: 'PA', label: 'PA (Physician Assistant)' },
      { value: 'RPh', label: 'RPh (Pharmacist)' },
      { value: 'PT', label: 'PT (Physical Therapist)' },
      { value: 'OT', label: 'OT (Occupational Therapist)' },
      { value: 'RT', label: 'RT (Respiratory Therapist)' },
      { value: 'MT', label: 'MT (Medical Technologist)' },
      { value: 'RD', label: 'RD (Registered Dietitian)' },
      { value: 'MSW', label: 'MSW (Medical Social Worker)' },
      { value: 'Mr.', label: 'Mr.' },
      { value: 'Ms.', label: 'Ms.' },
      { value: 'Mrs.', label: 'Mrs.' }
    ]
  },
  first_name: {
    type: 'text',
    required: true,
    placeholder: 'Joseph'
  },
  last_name: {
    type: 'text',
    required: true,
    placeholder: 'Ewool'
  },

  // Contact Information
  email: {
    type: 'email',
    required: true,
    placeholder: 'joseph.ewool@hospital.com'
  },
  phone_number: {
    type: 'tel',
    required: false,
    placeholder: '+1 (555) 123-4567'
  },

  // Security
  username: {
    type: 'text',
    required: false,
    placeholder: 'joseph_ewool (auto-generated from email if empty)'
  },
  password: {
    type: 'password',
    required: true,
    minLength: 8,
    placeholder: 'Minimum 8 characters'
  },
  password_confirm: {
    type: 'password',
    required: true,
    placeholder: 'Re-enter password'
  },

  // Professional Information
  organization_facility: {
    type: 'text',
    required: true,
    placeholder: 'General Hospital, Private Practice, etc.'
  },
  professional_role: {
    type: 'select',
    required: true,
    options: [
      { value: 'Physician', label: 'Physician' },
      { value: 'Registered Nurse', label: 'Registered Nurse' },
      { value: 'Specialist', label: 'Specialist' },
      { value: 'Healthcare Administrator', label: 'Healthcare Administrator' },
      { value: 'Medical Technician', label: 'Medical Technician' },
      { value: 'Other', label: 'Other' }
    ]
  },
  specialization: {
    type: 'text',
    required: false,
    placeholder: 'Emergency Medicine, Cardiology, etc.'
  },

  // License Verification
  license_number: {
    type: 'text',
    required: true,
    placeholder: 'MD123456789'
  },

  // Additional Information
  additional_information: {
    type: 'textarea',
    required: false,
    rows: 4,
    placeholder: 'Tell us about your specific IoT monitoring needs or any questions you have...'
  }
};
```

### **React Registration Component:**
```jsx
import React, { useState } from 'react';
import axios from 'axios';

const ProviderRegistrationForm = () => {
  const [formData, setFormData] = useState({
    professional_title: 'Dr.',
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    username: '',
    password: '',
    password_confirm: '',
    organization_facility: '',
    professional_role: 'Physician',
    specialization: '',
    license_number: '',
    additional_information: ''
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      const response = await axios.post(
        `${AUTH_BASE_URL}/provider/register/`,
        formData
      );

      if (response.data.tokens) {
        // Store tokens
        localStorage.setItem('access_token', response.data.tokens.access);
        localStorage.setItem('refresh_token', response.data.tokens.refresh);
        localStorage.setItem('user_role', 'provider');
        
        // Redirect to provider dashboard
        window.location.href = '/provider/dashboard';
      }
    } catch (error) {
      if (error.response?.data?.details) {
        setErrors(JSON.parse(error.response.data.details));
      } else {
        setErrors({ general: 'Registration failed. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <form onSubmit={handleSubmit} className="provider-registration-form">
      {/* Professional Title */}
      <div className="form-group">
        <label>Professional Title *</label>
        <select 
          name="professional_title"
          value={formData.professional_title}
          onChange={handleChange}
          required
        >
          {/* Add all professional title options */}
        </select>
        {errors.professional_title && <span className="error">{errors.professional_title}</span>}
      </div>

      {/* Add all other form fields following the same pattern */}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Registering...' : 'Register as Healthcare Provider'}
      </button>
    </form>
  );
};

export default ProviderRegistrationForm;
```

---

## 🔐 2. Provider Login Integration

### **Endpoint:** `POST /api/v1/auth/login/`

```javascript
const loginProvider = async (email, password) => {
  try {
    const response = await axios.post(`${AUTH_BASE_URL}/login/`, {
      email,
      password
    });

    if (response.data.tokens && response.data.authUser.roles.includes('provider')) {
      localStorage.setItem('access_token', response.data.tokens.access);
      localStorage.setItem('refresh_token', response.data.tokens.refresh);
      localStorage.setItem('user_role', 'provider');
      localStorage.setItem('provider_id', response.data.authUser.id);
      
      return {
        success: true,
        user: response.data.authUser,
        permissions: response.data.authUser.permissions
      };
    }
    
    throw new Error('Not a provider account');
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.message || 'Login failed'
    };
  }
};
```

---

## 👤 3. Provider Profile Management

### **Get Provider Profile:** `GET /api/v1/auth/provider/profile/`
```javascript
const getProviderProfile = async () => {
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await axios.get(
      `${AUTH_BASE_URL}/provider/profile/`,
      { headers: getAuthHeaders(token) }
    );
    
    return response.data;
  } catch (error) {
    console.error('Failed to fetch provider profile:', error);
    throw error;
  }
};
```

### **Update Provider Profile:** `PATCH /api/v1/auth/provider/profile/`
```javascript
const updateProviderProfile = async (updateData) => {
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await axios.patch(
      `${AUTH_BASE_URL}/provider/profile/`,
      updateData,
      { headers: getAuthHeaders(token) }
    );
    
    return response.data;
  } catch (error) {
    console.error('Failed to update provider profile:', error);
    throw error;
  }
};
```

---

## 📊 4. Provider Dashboard Implementation

### **Endpoint:** `GET /api/v1/auth/provider/dashboard/`

### **Expected Response Structure:**
```json
{
  "provider": {
    "id": "uuid",
    "full_name": "Dr. Joseph Ewool",
    "specialization": "Emergency Medicine",
    "years_of_experience": 8,
    "consultation_fee": "250.00",
    "professional_role": "Physician",
    "organization_facility": "General Hospital"
  },
  "statistics": {
    "total_appointments": 156,
    "today_appointments": 5,
    "week_appointments": 23,
    "month_appointments": 67,
    "upcoming_appointments": 12,
    "completed_appointments": 134,
    "cancelled_appointments": 10,
    "pending_appointments": 3
  },
  "recent_appointments": [
    {
      "id": "appointment_id",
      "patient_name": "John Smith",
      "appointment_date": "2025-08-07T14:30:00Z",
      "duration_minutes": 30,
      "appointment_type": "consultation",
      "status": "confirmed",
      "chief_complaint": "Chest pain monitoring"
    }
  ],
  "todays_schedule": [
    {
      "time": "09:00",
      "patient": "Alice Johnson",
      "type": "Follow-up",
      "status": "confirmed"
    },
    {
      "time": "10:30",
      "patient": "Bob Wilson",
      "type": "Consultation", 
      "status": "pending"
    }
  ]
}
```

### **React Dashboard Component:**
```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProviderDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem('access_token');
    
    try {
      const response = await axios.get(
        `${AUTH_BASE_URL}/provider/dashboard/`,
        { headers: getAuthHeaders(token) }
      );
      
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading dashboard...</div>;
  if (!dashboardData) return <div>Failed to load dashboard</div>;

  const { provider, statistics, recent_appointments, todays_schedule } = dashboardData;

  return (
    <div className="provider-dashboard">
      {/* Provider Info Header */}
      <div className="dashboard-header">
        <h1>Welcome, {provider.full_name}</h1>
        <div className="provider-info">
          <span className="specialization">{provider.specialization}</span>
          <span className="organization">{provider.organization_facility}</span>
          <span className="role">{provider.professional_role}</span>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Today's Appointments</h3>
          <span className="stat-number">{statistics.today_appointments}</span>
        </div>
        <div className="stat-card">
          <h3>This Week</h3>
          <span className="stat-number">{statistics.week_appointments}</span>
        </div>
        <div className="stat-card">
          <h3>This Month</h3>
          <span className="stat-number">{statistics.month_appointments}</span>
        </div>
        <div className="stat-card">
          <h3>Total Appointments</h3>
          <span className="stat-number">{statistics.total_appointments}</span>
        </div>
        <div className="stat-card">
          <h3>Upcoming</h3>
          <span className="stat-number">{statistics.upcoming_appointments}</span>
        </div>
        <div className="stat-card">
          <h3>Completed</h3>
          <span className="stat-number">{statistics.completed_appointments}</span>
        </div>
      </div>

      {/* Today's Schedule */}
      <div className="todays-schedule">
        <h2>Today's Schedule</h2>
        {todays_schedule && todays_schedule.length > 0 ? (
          <div className="schedule-list">
            {todays_schedule.map((appointment, index) => (
              <div key={index} className={`schedule-item ${appointment.status}`}>
                <div className="time">{appointment.time}</div>
                <div className="patient">{appointment.patient}</div>
                <div className="type">{appointment.type}</div>
                <div className={`status ${appointment.status}`}>
                  {appointment.status}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No appointments scheduled for today</p>
        )}
      </div>

      {/* Recent Appointments */}
      <div className="recent-appointments">
        <h2>Recent Appointments</h2>
        {recent_appointments && recent_appointments.length > 0 ? (
          <div className="appointments-list">
            {recent_appointments.map((appointment) => (
              <div key={appointment.id} className="appointment-item">
                <div className="appointment-info">
                  <h4>{appointment.patient_name}</h4>
                  <p>{appointment.chief_complaint}</p>
                  <span className="appointment-meta">
                    {new Date(appointment.appointment_date).toLocaleDateString()} • 
                    {appointment.duration_minutes} min • 
                    {appointment.appointment_type}
                  </span>
                </div>
                <div className={`status ${appointment.status}`}>
                  {appointment.status}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No recent appointments</p>
        )}
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <button onClick={() => window.location.href = '/provider/appointments'}>
          View All Appointments
        </button>
        <button onClick={() => window.location.href = '/provider/schedule'}>
          Manage Schedule
        </button>
        <button onClick={() => window.location.href = '/provider/profile'}>
          Update Profile
        </button>
      </div>
    </div>
  );
};

export default ProviderDashboard;
```

---

## 📅 5. Provider Appointments Management

### **Get Provider's Appointments:** `GET /api/v1/appointments/provider-appointments/`
```javascript
const getProviderAppointments = async (filters = {}) => {
  const token = localStorage.getItem('access_token');
  const queryParams = new URLSearchParams(filters).toString();
  
  try {
    const response = await axios.get(
      `${API_BASE_URL}/appointments/provider-appointments/?${queryParams}`,
      { headers: getAuthHeaders(token) }
    );
    
    return response.data;
  } catch (error) {
    console.error('Failed to fetch appointments:', error);
    throw error;
  }
};

// Usage examples:
// getProviderAppointments({ status: 'confirmed' })
// getProviderAppointments({ date: '2025-08-07' })
// getProviderAppointments({ patient: 'John Smith' })
```

### **Update Appointment Status:**
```javascript
const updateAppointmentStatus = async (appointmentId, status, notes = '') => {
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await axios.patch(
      `${API_BASE_URL}/appointments/${appointmentId}/`,
      { status, notes },
      { headers: getAuthHeaders(token) }
    );
    
    return response.data;
  } catch (error) {
    console.error('Failed to update appointment:', error);
    throw error;
  }
};
```

---

## 🔍 6. Provider Directory & Search

### **Search Providers:** `GET /api/v1/providers/`
```javascript
const searchProviders = async (searchParams) => {
  const token = localStorage.getItem('access_token');
  const queryString = new URLSearchParams(searchParams).toString();
  
  try {
    const response = await axios.get(
      `${API_BASE_URL}/providers/?${queryString}`,
      { headers: getAuthHeaders(token) }
    );
    
    return response.data;
  } catch (error) {
    console.error('Failed to search providers:', error);
    throw error;
  }
};

// Usage examples:
// searchProviders({ search: 'cardiology' })
// searchProviders({ professional_role: 'Physician' })
// searchProviders({ specialization: 'Emergency Medicine' })
```

### **Provider Autocomplete:** `GET /api/v1/providers/search/`
```javascript
const getProviderSuggestions = async (query) => {
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await axios.get(
      `${API_BASE_URL}/providers/search/?q=${encodeURIComponent(query)}`,
      { headers: getAuthHeaders(token) }
    );
    
    return response.data.suggestions;
  } catch (error) {
    console.error('Failed to get suggestions:', error);
    return [];
  }
};
```

---

## 🏥 7. Hospital Integration

### **Get Providers by Hospital:** `GET /api/v1/providers/hospital/{hospital_id}/`
```javascript
const getProvidersByHospital = async (hospitalId) => {
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await axios.get(
      `${API_BASE_URL}/providers/hospital/${hospitalId}/`,
      { headers: getAuthHeaders(token) }
    );
    
    return response.data;
  } catch (error) {
    console.error('Failed to get providers by hospital:', error);
    throw error;
  }
};
```

---

## 🔐 8. Authentication & Token Management

### **Token Validation:** `POST /api/v1/auth/token/validate/`
```javascript
const validateToken = async () => {
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await axios.post(
      `${AUTH_BASE_URL}/token/validate/`,
      {},
      { headers: getAuthHeaders(token) }
    );
    
    return response.data.valid;
  } catch (error) {
    return false;
  }
};
```

### **Token Refresh:** `POST /api/v1/auth/token/refresh/`
```javascript
const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  try {
    const response = await axios.post(`${AUTH_BASE_URL}/token/refresh/`, {
      refresh: refreshToken
    });
    
    localStorage.setItem('access_token', response.data.access);
    return response.data.access;
  } catch (error) {
    // Refresh token expired, redirect to login
    localStorage.clear();
    window.location.href = '/login';
    throw error;
  }
};
```

---

## 🎨 9. Frontend Page Updates Required

### **9.1 Update Provider Registration Page:**
- Replace current form fields with the professional form fields above
- Add all 16 professional title options dropdown
- Add all 6 professional role options dropdown  
- Add license number field with uniqueness validation
- Add organization/facility field
- Add additional information textarea
- Update validation to match backend requirements

### **9.2 Update Provider Dashboard:**
- Replace mock data with real API calls to `/api/v1/auth/provider/dashboard/`
- Display provider information (name, title, organization, role)
- Show appointment statistics (today, week, month, total)
- Display today's schedule with real appointment data
- Show recent appointments list
- Add quick action buttons for appointment management

### **9.3 Update Provider Profile Page:**
- Fetch profile data from `/api/v1/auth/provider/profile/`
- Allow editing of professional information
- Add license verification status display
- Enable profile updates with API call
- Show professional credentials and organization info

### **9.4 Add Provider Appointments Page:**
- Create new page for appointment management
- Display all provider's appointments with filtering
- Allow status updates (confirmed, completed, cancelled)
- Show patient information and appointment details
- Add calendar view for appointments

### **9.5 Update Provider Search/Directory:**
- Use real API calls to `/api/v1/providers/`
- Add search functionality with autocomplete
- Filter by professional role, specialization
- Display provider cards with complete information
- Add pagination for large result sets

---

## 🚀 10. Implementation Checklist

### **Backend Integration:**
- [ ] Update API base URLs to match backend
- [ ] Replace all mock data with real API calls
- [ ] Implement JWT token management
- [ ] Add error handling for all API calls
- [ ] Test all endpoints with real data

### **Form Updates:**
- [ ] Update provider registration form fields
- [ ] Add all dropdown options for professional title/role
- [ ] Implement form validation matching backend rules
- [ ] Add license number uniqueness check
- [ ] Update password requirements (min 8 chars)

### **Dashboard Updates:**
- [ ] Replace dashboard mock data with API calls
- [ ] Display real appointment statistics
- [ ] Show today's schedule from backend
- [ ] Add recent appointments list
- [ ] Implement quick actions

### **Authentication:**
- [ ] Update login flow for provider accounts
- [ ] Implement JWT token storage and refresh
- [ ] Add provider role checking
- [ ] Handle authentication errors properly

### **UI/UX Improvements:**
- [ ] Add loading states for all API calls
- [ ] Implement proper error messages
- [ ] Add success notifications
- [ ] Ensure responsive design for all pages

---

## 💻 11. Sample API Integration Service

```javascript
// services/providerService.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';
const AUTH_BASE_URL = 'http://localhost:8001/api/v1/auth';

class ProviderService {
  constructor() {
    this.setupInterceptors();
  }

  setupInterceptors() {
    // Request interceptor to add auth token
    axios.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor to handle token refresh
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          try {
            await this.refreshToken();
            return axios.request(error.config);
          } catch (refreshError) {
            this.logout();
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async register(providerData) {
    const response = await axios.post(`${AUTH_BASE_URL}/provider/register/`, providerData);
    return response.data;
  }

  async login(email, password) {
    const response = await axios.post(`${AUTH_BASE_URL}/login/`, { email, password });
    return response.data;
  }

  async getProfile() {
    const response = await axios.get(`${AUTH_BASE_URL}/provider/profile/`);
    return response.data;
  }

  async updateProfile(data) {
    const response = await axios.patch(`${AUTH_BASE_URL}/provider/profile/`, data);
    return response.data;
  }

  async getDashboard() {
    const response = await axios.get(`${AUTH_BASE_URL}/provider/dashboard/`);
    return response.data;
  }

  async getAppointments(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const response = await axios.get(`${API_BASE_URL}/appointments/provider-appointments/?${params}`);
    return response.data;
  }

  async searchProviders(searchParams) {
    const params = new URLSearchParams(searchParams).toString();
    const response = await axios.get(`${API_BASE_URL}/providers/?${params}`);
    return response.data;
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await axios.post(`${AUTH_BASE_URL}/token/refresh/`, {
      refresh: refreshToken
    });
    localStorage.setItem('access_token', response.data.access);
    return response.data;
  }

  logout() {
    localStorage.clear();
    window.location.href = '/login';
  }
}

export default new ProviderService();
```

---

## 🎯 Conclusion

This guide provides complete specifications for integrating the frontend with the healthcare provider backend system. All endpoints have been tested with real data and are production-ready.

### **Key Updates Required:**
1. **Replace all mock data** with real API calls
2. **Update registration form** with professional fields
3. **Implement real dashboard** with appointment data
4. **Add proper authentication** with JWT tokens
5. **Create appointment management** functionality

### **Next Steps:**
1. Update each frontend page according to specifications above
2. Test all API integrations thoroughly
3. Implement proper error handling and loading states
4. Ensure responsive design across all devices
5. Deploy and test in production environment

The backend is fully implemented and ready for frontend integration! 🚀
