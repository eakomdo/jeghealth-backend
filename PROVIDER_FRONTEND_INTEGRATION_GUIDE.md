# 🏥 Healthcare Provider System - Frontend Integration Guide

## 📋 Overview
This comprehensive guide provides frontend teams with all necessary specifications to integrate with the healthcare provider backend system. All endpoints have been tested with real data and are production-ready.

---

## 🔧 Base Configuration

```javascript
// API Configuration
const API_BASE_URL = 'http://localhost:8001/api/v1';
const AUTH_BASE_URL = `${API_BASE_URL}/auth`;
const PROVIDER_BASE_URL = `${API_BASE_URL}/providers`;

// Authentication Headers
const getAuthHeaders = (token) => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`
});

// File Upload Headers
const getFileUploadHeaders = (token) => ({
  'Authorization': `Bearer ${token}`
  // Don't set Content-Type for FormData
});
```

---

## 🚀 1. Provider Registration System

### **Registration Endpoint:** `POST /auth/provider/register/`

### **Form Fields Configuration:**

```javascript
const providerRegistrationForm = {
  // Step 1: Personal Information
  personalInfo: {
    professional_title: {
      type: 'select',
      required: true,
      label: 'Professional Title',
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
      label: 'First Name',
      placeholder: 'Joseph',
      validation: { minLength: 2, maxLength: 100 }
    },
    last_name: {
      type: 'text',
      required: true,
      label: 'Last Name', 
      placeholder: 'Ewool',
      validation: { minLength: 2, maxLength: 100 }
    }
  },

  // Step 2: Contact Information
  contactInfo: {
    email: {
      type: 'email',
      required: true,
      label: 'Professional Email',
      placeholder: 'joseph.ewool@hospital.com',
      validation: { format: 'email', unique: true }
    },
    phone_number: {
      type: 'tel',
      required: false,
      label: 'Phone Number',
      placeholder: '+1 (555) 123-4567',
      validation: { format: 'phone' }
    }
  },

  // Step 3: Account Security
  accountSecurity: {
    username: {
      type: 'text',
      required: false,
      label: 'Username',
      placeholder: 'Auto-generated from email if left empty',
      validation: { unique: true }
    },
    password: {
      type: 'password',
      required: true,
      label: 'Password',
      placeholder: 'Minimum 8 characters',
      validation: { minLength: 8, strength: true }
    },
    password_confirm: {
      type: 'password',
      required: true,
      label: 'Confirm Password',
      placeholder: 'Re-enter password',
      validation: { matches: 'password' }
    }
  },

  // Step 4: Professional Information
  professionalInfo: {
    organization_facility: {
      type: 'text',
      required: true,
      label: 'Organization/Facility',
      placeholder: 'General Hospital, Private Practice, Clinic Name',
      validation: { maxLength: 200 }
    },
    professional_role: {
      type: 'select',
      required: true,
      label: 'Professional Role',
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
      label: 'Specialization',
      placeholder: 'Cardiology, Pediatrics, General Practice, etc.',
      validation: { maxLength: 100 }
    }
  },

  // Step 5: License Information
  licenseInfo: {
    license_number: {
      type: 'text',
      required: true,
      label: 'Professional License Number',
      placeholder: 'Enter your medical license number',
      validation: { unique: true, maxLength: 50 }
    }
  },

  // Step 6: Additional Information (Optional)
  additionalInfo: {
    additional_information: {
      type: 'textarea',
      required: false,
      label: 'Additional Information',
      placeholder: 'Tell us about your specific IoT monitoring needs or any questions you might have',
      validation: { maxLength: 1000 }
    }
  },

  // Legacy Fields (for backward compatibility)
  legacyFields: {
    years_of_experience: {
      type: 'number',
      required: false,
      label: 'Years of Experience',
      default: 0,
      validation: { min: 0 }
    },
    consultation_fee: {
      type: 'number',
      required: false,
      label: 'Consultation Fee',
      default: 0.00,
      validation: { min: 0, decimal: 2 }
    },
    bio: {
      type: 'textarea',
      required: false,
      label: 'Professional Biography',
      placeholder: 'Brief description of your background and expertise'
    }
  }
};
```

### **Registration Implementation Example:**

```javascript
// React Example
const ProviderRegistration = () => {
  const [formData, setFormData] = useState({
    // Initialize all required fields
    professional_title: '',
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    password_confirm: '',
    organization_facility: '',
    professional_role: '',
    license_number: '',
    // Optional fields
    phone_number: '',
    username: '',
    specialization: '',
    additional_information: '',
    years_of_experience: 0,
    consultation_fee: 0.00,
    bio: ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch(`${AUTH_BASE_URL}/provider/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        // Registration successful
        console.log('Provider registered successfully:', data);
        // Redirect to login or dashboard
        window.location.href = '/provider/login';
      } else {
        // Handle validation errors
        setErrors(data);
      }
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ general: 'Network error occurred' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Implement form fields based on configuration above */}
      {/* Add proper validation and error handling */}
    </form>
  );
};
```

---

## 🔐 2. Provider Authentication System

### **Login Endpoint:** `POST /auth/login/`

```javascript
const providerLogin = async (credentials) => {
  try {
    const response = await fetch(`${AUTH_BASE_URL}/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password
      })
    });

    const data = await response.json();

    if (response.ok) {
      // Store tokens securely
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      
      return {
        success: true,
        user: data.user,
        tokens: {
          access: data.access,
          refresh: data.refresh
        }
      };
    } else {
      return {
        success: false,
        errors: data
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    };
  }
};
```

### **Token Validation:** `POST /auth/token/validate/`

```javascript
const validateToken = async (token) => {
  try {
    const response = await fetch(`${AUTH_BASE_URL}/token/validate/`, {
      method: 'POST',
      headers: getAuthHeaders(token)
    });

    return response.ok;
  } catch (error) {
    return false;
  }
};
```

### **Token Refresh:** `POST /auth/token/refresh/`

```javascript
const refreshToken = async (refreshToken) => {
  try {
    const response = await fetch(`${AUTH_BASE_URL}/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh: refreshToken
      })
    });

    const data = await response.json();
    
    if (response.ok) {
      localStorage.setItem('access_token', data.access);
      return data.access;
    } else {
      // Refresh token expired, redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/provider/login';
      return null;
    }
  } catch (error) {
    return null;
  }
};
```

---

## 👤 3. Provider Profile Management

### **Get Profile:** `GET /auth/provider/profile/`

```javascript
const getProviderProfile = async (token) => {
  try {
    const response = await fetch(`${AUTH_BASE_URL}/provider/profile/`, {
      method: 'GET',
      headers: getAuthHeaders(token)
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        profile: data
      };
    } else {
      return {
        success: false,
        errors: data
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    };
  }
};
```

### **Update Profile:** `PUT /auth/provider/profile/` or `PATCH /auth/provider/profile/`

```javascript
const updateProviderProfile = async (token, profileData) => {
  try {
    const response = await fetch(`${AUTH_BASE_URL}/provider/profile/`, {
      method: 'PATCH', // Use PATCH for partial updates
      headers: getAuthHeaders(token),
      body: JSON.stringify(profileData)
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        profile: data
      };
    } else {
      return {
        success: false,
        errors: data
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    };
  }
};
```

---

## 📊 4. Provider Dashboard

### **Dashboard Data:** `GET /auth/provider/dashboard/`

```javascript
const getProviderDashboard = async (token) => {
  try {
    const response = await fetch(`${AUTH_BASE_URL}/provider/dashboard/`, {
      method: 'GET',
      headers: getAuthHeaders(token)
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        dashboard: data
      };
    } else {
      return {
        success: false,
        errors: data
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    };
  }
};
```

### **Dashboard Data Structure:**
```javascript
const dashboardDataStructure = {
  provider_profile: {
    id: "uuid",
    professional_title: "Dr.",
    first_name: "Joseph",
    last_name: "Ewool",
    email: "joseph.ewool@hospital.com",
    organization_facility: "General Hospital",
    professional_role: "Physician",
    specialization: "Cardiology",
    license_verified: false
  },
  stats: {
    total_appointments: 0,
    upcoming_appointments: 0,
    completed_appointments: 0,
    patients_count: 0
  },
  recent_activities: [],
  notifications: [],
  license_status: "pending_verification"
};
```

---

## 🔍 5. Provider Search & Directory

### **Provider List:** `GET /providers/`

```javascript
const getProviders = async (params = {}) => {
  const queryParams = new URLSearchParams(params);
  
  try {
    const response = await fetch(`${PROVIDER_BASE_URL}/?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        providers: data.results || data,
        pagination: {
          count: data.count,
          next: data.next,
          previous: data.previous
        }
      };
    } else {
      return {
        success: false,
        errors: data
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    };
  }
};
```

### **Provider Search:** `GET /providers/search/`

```javascript
const searchProviders = async (searchQuery, filters = {}) => {
  const params = {
    q: searchQuery,
    ...filters
  };

  const queryParams = new URLSearchParams(params);

  try {
    const response = await fetch(`${PROVIDER_BASE_URL}/search/?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        providers: data
      };
    } else {
      return {
        success: false,
        errors: data
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    };
  }
};
```

### **Provider Dropdown:** `GET /providers/dropdown/`

```javascript
const getProviderDropdown = async () => {
  try {
    const response = await fetch(`${PROVIDER_BASE_URL}/dropdown/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        providers: data
      };
    } else {
      return {
        success: false,
        errors: data
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    };
  }
};
```

### **Provider Detail:** `GET /providers/{id}/`

```javascript
const getProviderDetail = async (providerId) => {
  try {
    const response = await fetch(`${PROVIDER_BASE_URL}/${providerId}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        provider: data
      };
    } else {
      return {
        success: false,
        errors: data
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    };
  }
};
```

---

## 🏥 6. Hospital Integration

### **Providers by Hospital:** `GET /providers/hospital/{hospital_id}/`

```javascript
const getProvidersByHospital = async (hospitalId) => {
  try {
    const response = await fetch(`${PROVIDER_BASE_URL}/hospital/${hospitalId}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        providers: data
      };
    } else {
      return {
        success: false,
        errors: data
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error occurred'
    };
  }
};
```

---

## 🎨 7. Frontend UI/UX Guidelines

### **Provider Registration Form Design:**
```javascript
const registrationSteps = [
  {
    step: 1,
    title: "Personal Information",
    description: "Let's start with your basic details",
    fields: ["professional_title", "first_name", "last_name"]
  },
  {
    step: 2,
    title: "Contact Information", 
    description: "How can patients and colleagues reach you?",
    fields: ["email", "phone_number"]
  },
  {
    step: 3,
    title: "Account Security",
    description: "Create a secure account",
    fields: ["username", "password", "password_confirm"]
  },
  {
    step: 4,
    title: "Professional Details",
    description: "Tell us about your professional background",
    fields: ["organization_facility", "professional_role", "specialization"]
  },
  {
    step: 5,
    title: "License Verification",
    description: "Professional license for verification",
    fields: ["license_number"]
  },
  {
    step: 6,
    title: "Additional Information",
    description: "Anything else you'd like us to know? (Optional)",
    fields: ["additional_information"]
  }
];
```

### **Validation Rules:**
```javascript
const validationRules = {
  // Required field validation
  required: {
    professional_title: "Professional title is required",
    first_name: "First name is required",
    last_name: "Last name is required", 
    email: "Email address is required",
    password: "Password is required",
    password_confirm: "Please confirm your password",
    organization_facility: "Organization/Facility is required",
    professional_role: "Professional role is required",
    license_number: "License number is required"
  },

  // Format validation
  email: "Please enter a valid email address",
  password_length: "Password must be at least 8 characters long",
  password_match: "Passwords do not match",
  phone_format: "Please enter a valid phone number",
  license_unique: "A provider with this license number already exists",

  // Character limits
  first_name_max: "First name cannot exceed 100 characters",
  last_name_max: "Last name cannot exceed 100 characters",
  organization_facility_max: "Organization name cannot exceed 200 characters",
  specialization_max: "Specialization cannot exceed 100 characters",
  license_number_max: "License number cannot exceed 50 characters",
  additional_info_max: "Additional information cannot exceed 1000 characters"
};
```

### **Error Handling:**
```javascript
const handleErrors = (errors) => {
  const errorMessages = {};
  
  if (typeof errors === 'object') {
    Object.keys(errors).forEach(field => {
      if (Array.isArray(errors[field])) {
        errorMessages[field] = errors[field][0]; // First error message
      } else {
        errorMessages[field] = errors[field];
      }
    });
  }
  
  return errorMessages;
};
```

---

## 📱 8. State Management (React/Redux Example)

### **Provider State Structure:**
```javascript
const initialProviderState = {
  // Authentication state
  isAuthenticated: false,
  user: null,
  tokens: {
    access: null,
    refresh: null
  },

  // Provider profile state
  profile: null,
  profileLoading: false,
  profileError: null,

  // Dashboard state
  dashboard: null,
  dashboardLoading: false,
  dashboardError: null,

  // Provider directory state
  providers: [],
  providersLoading: false,
  providersError: null,
  searchResults: [],
  searchLoading: false,

  // UI state
  registrationStep: 1,
  registrationErrors: {},
  isSubmitting: false
};
```

### **Provider Actions:**
```javascript
const providerActions = {
  // Authentication actions
  LOGIN_REQUEST: 'PROVIDER_LOGIN_REQUEST',
  LOGIN_SUCCESS: 'PROVIDER_LOGIN_SUCCESS', 
  LOGIN_FAILURE: 'PROVIDER_LOGIN_FAILURE',
  LOGOUT: 'PROVIDER_LOGOUT',

  // Registration actions
  REGISTER_REQUEST: 'PROVIDER_REGISTER_REQUEST',
  REGISTER_SUCCESS: 'PROVIDER_REGISTER_SUCCESS',
  REGISTER_FAILURE: 'PROVIDER_REGISTER_FAILURE',

  // Profile actions
  FETCH_PROFILE_REQUEST: 'FETCH_PROVIDER_PROFILE_REQUEST',
  FETCH_PROFILE_SUCCESS: 'FETCH_PROVIDER_PROFILE_SUCCESS',
  FETCH_PROFILE_FAILURE: 'FETCH_PROVIDER_PROFILE_FAILURE',
  UPDATE_PROFILE_REQUEST: 'UPDATE_PROVIDER_PROFILE_REQUEST',
  UPDATE_PROFILE_SUCCESS: 'UPDATE_PROVIDER_PROFILE_SUCCESS',
  UPDATE_PROFILE_FAILURE: 'UPDATE_PROVIDER_PROFILE_FAILURE',

  // Dashboard actions
  FETCH_DASHBOARD_REQUEST: 'FETCH_PROVIDER_DASHBOARD_REQUEST',
  FETCH_DASHBOARD_SUCCESS: 'FETCH_PROVIDER_DASHBOARD_SUCCESS',
  FETCH_DASHBOARD_FAILURE: 'FETCH_PROVIDER_DASHBOARD_FAILURE',

  // Directory actions
  FETCH_PROVIDERS_REQUEST: 'FETCH_PROVIDERS_REQUEST',
  FETCH_PROVIDERS_SUCCESS: 'FETCH_PROVIDERS_SUCCESS',
  FETCH_PROVIDERS_FAILURE: 'FETCH_PROVIDERS_FAILURE',
  SEARCH_PROVIDERS_REQUEST: 'SEARCH_PROVIDERS_REQUEST',
  SEARCH_PROVIDERS_SUCCESS: 'SEARCH_PROVIDERS_SUCCESS',
  SEARCH_PROVIDERS_FAILURE: 'SEARCH_PROVIDERS_FAILURE'
};
```

---

## 🔧 9. Utility Functions

### **Token Management:**
```javascript
const TokenManager = {
  getAccessToken: () => localStorage.getItem('access_token'),
  getRefreshToken: () => localStorage.getItem('refresh_token'),
  
  setTokens: (access, refresh) => {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  },
  
  clearTokens: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  
  isTokenExpired: (token) => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return Date.now() >= payload.exp * 1000;
    } catch {
      return true;
    }
  }
};
```

### **API Client:**
```javascript
class ProviderAPIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.authURL = AUTH_BASE_URL;
    this.providerURL = PROVIDER_BASE_URL;
  }

  async request(url, options = {}) {
    const token = TokenManager.getAccessToken();
    
    // Check if token needs refresh
    if (token && TokenManager.isTokenExpired(token)) {
      const newToken = await refreshToken(TokenManager.getRefreshToken());
      if (!newToken) {
        throw new Error('Authentication required');
      }
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...getAuthHeaders(TokenManager.getAccessToken()),
        ...options.headers
      }
    });

    if (response.status === 401) {
      // Token expired, try to refresh
      const newToken = await refreshToken(TokenManager.getRefreshToken());
      if (newToken) {
        // Retry request with new token
        return this.request(url, options);
      } else {
        // Redirect to login
        window.location.href = '/provider/login';
        throw new Error('Authentication expired');
      }
    }

    return response;
  }

  // Provider-specific methods
  async register(data) {
    return this.request(`${this.authURL}/provider/register/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async login(credentials) {
    return this.request(`${this.authURL}/login/`, {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
  }

  async getProfile() {
    return this.request(`${this.authURL}/provider/profile/`);
  }

  async updateProfile(data) {
    return this.request(`${this.authURL}/provider/profile/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  async getDashboard() {
    return this.request(`${this.authURL}/provider/dashboard/`);
  }

  async getProviders(params) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${this.providerURL}/?${queryString}`);
  }

  async searchProviders(query, filters) {
    const params = { q: query, ...filters };
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${this.providerURL}/search/?${queryString}`);
  }
}

// Export singleton instance
export const providerAPI = new ProviderAPIClient();
```

---

## ✅ 10. Implementation Checklist

### **Phase 1: Registration & Authentication**
- [ ] Update provider registration form with all required fields
- [ ] Implement multi-step registration wizard
- [ ] Add proper form validation with real-time feedback
- [ ] Replace mock login with real authentication endpoints
- [ ] Implement JWT token management with auto-refresh
- [ ] Add password strength validation
- [ ] Add license number uniqueness validation

### **Phase 2: Profile Management**
- [ ] Update provider profile page with new fields
- [ ] Implement profile editing functionality
- [ ] Add license document upload capability
- [ ] Display license verification status
- [ ] Add profile completion progress indicator

### **Phase 3: Dashboard Integration**
- [ ] Replace mock dashboard data with real API calls
- [ ] Implement provider statistics display
- [ ] Add recent activity feed
- [ ] Display license verification status
- [ ] Add quick action buttons (edit profile, view appointments)

### **Phase 4: Provider Directory**
- [ ] Update provider search functionality
- [ ] Implement advanced filtering options
- [ ] Add provider detail view
- [ ] Implement hospital-based provider listing
- [ ] Add provider dropdown for appointment booking

### **Phase 5: Error Handling & UX**
- [ ] Implement comprehensive error handling
- [ ] Add loading states for all async operations
- [ ] Add success/error notifications
- [ ] Implement form validation feedback
- [ ] Add offline handling capabilities

### **Phase 6: Testing & Optimization**
- [ ] Test all provider registration flows
- [ ] Test authentication and token refresh
- [ ] Test profile management operations
- [ ] Test dashboard data loading
- [ ] Test provider search and filtering
- [ ] Performance optimization and caching
- [ ] Mobile responsiveness testing

---

## 🔗 11. Complete Endpoint Reference

### **Authentication Endpoints:**
```
POST   /api/v1/auth/provider/register/     - Provider registration
POST   /api/v1/auth/login/                 - Provider login
POST   /api/v1/auth/logout/                - Provider logout
POST   /api/v1/auth/token/refresh/         - Token refresh
POST   /api/v1/auth/token/validate/        - Token validation
```

### **Provider Profile Endpoints:**
```
GET    /api/v1/auth/provider/profile/      - Get provider profile
PUT    /api/v1/auth/provider/profile/      - Update provider profile (full)
PATCH  /api/v1/auth/provider/profile/      - Update provider profile (partial)
GET    /api/v1/auth/provider/dashboard/    - Get provider dashboard
```

### **Provider Directory Endpoints:**
```
GET    /api/v1/providers/                  - List all providers
POST   /api/v1/providers/                  - Create new provider
GET    /api/v1/providers/{id}/             - Get provider details
PUT    /api/v1/providers/{id}/             - Update provider
DELETE /api/v1/providers/{id}/             - Delete provider
GET    /api/v1/providers/search/           - Search providers
GET    /api/v1/providers/dropdown/         - Provider dropdown list
GET    /api/v1/providers/hospital/{id}/    - Get providers by hospital
```

---

## 🚨 12. Important Notes & Best Practices

### **Security Considerations:**
- Always validate form inputs on both frontend and backend
- Store JWT tokens securely (consider httpOnly cookies for production)
- Implement proper token refresh mechanism
- Validate license numbers for uniqueness
- Sanitize all user inputs to prevent XSS attacks

### **Performance Optimizations:**
- Implement pagination for provider listings
- Use debounced search for provider search functionality
- Cache provider dropdown data
- Optimize image uploads for profile pictures and license documents
- Implement lazy loading for provider directory

### **User Experience:**
- Provide clear validation error messages
- Show loading states during async operations
- Implement auto-save for long forms
- Add progress indicators for multi-step processes
- Provide helpful placeholder text and examples

### **Error Handling:**
- Display user-friendly error messages
- Log detailed errors for debugging
- Implement retry mechanisms for failed requests
- Provide offline capability where possible
- Handle network timeouts gracefully

---

## 📞 13. Support & Troubleshooting

### **Common Issues:**

1. **Registration failing with 400 errors:**
   - Check all required fields are provided
   - Validate email format and uniqueness
   - Ensure license number is unique
   - Verify password meets minimum requirements

2. **Token refresh issues:**
   - Implement proper token expiration handling
   - Check refresh token validity
   - Clear tokens and redirect to login on refresh failure

3. **Profile update failures:**
   - Ensure authenticated requests include valid tokens
   - Check field validation requirements
   - Verify file upload format for license documents

### **Testing Endpoints:**
Use the provided test scripts for comprehensive endpoint testing:
- `test_professional_provider_complete.sh`
- `test_real_provider_complete.sh`

---

## 🎯 14. Next Steps

1. **Frontend Team Actions:**
   - Review this integration guide thoroughly
   - Update all provider-related components
   - Replace mock data with real API calls
   - Implement proper authentication flow
   - Test all user journeys

2. **Backend Support:**
   - All endpoints are implemented and tested
   - Database migrations are applied
   - Comprehensive documentation provided
   - Test scripts available for validation

3. **Deployment Preparation:**
   - Configure production API URLs
   - Set up proper environment variables
   - Implement security headers
   - Set up monitoring and logging

---

**✨ The healthcare provider backend system is fully implemented, tested, and ready for frontend integration. This guide provides everything needed to build a professional, secure, and user-friendly provider registration and management system.**
