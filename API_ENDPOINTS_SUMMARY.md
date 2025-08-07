# JegHealth API - Essential Endpoints Summary

**Base URL**: `http://localhost:8001/api/v1`

## 🔐 Authentication (No Token Required)
```
POST /auth/register/                    - User registration
POST /auth/login/                       - User/Provider login
POST /auth/provider/register/           - Provider registration
POST /auth/token/refresh/               - Refresh access token
```

## 👤 User Management (Token Required)
```
GET  /auth/current-user/                - Get current user info
GET  /auth/profile/                     - Get user profile
PATCH /auth/profile/                    - Update user profile
GET  /auth/profile/basic/               - Get basic info
PATCH /auth/profile/basic/              - Update basic info
GET  /auth/profile/personal/            - Get personal info
PATCH /auth/profile/personal/           - Update personal info
POST /auth/change-password/             - Change password
POST /auth/logout/                      - Logout
```

## 🏥 Providers (Token Required)
```
GET  /providers/                        - List all providers
GET  /providers/{id}/                   - Get provider details
GET  /providers/search/?q=term          - Search providers
GET  /providers/dropdown/               - Providers for dropdown
GET  /providers/hospital/{hospital_id}/ - Providers by hospital
POST /providers/                        - Create provider (admin)

# Provider-specific (Provider Token Required)
GET  /auth/provider/profile/            - Get provider profile
PATCH /auth/provider/profile/           - Update provider profile
GET  /auth/provider/dashboard/          - Provider dashboard
```

## 📅 Appointments (Token Required)
```
GET  /appointments/                     - List user appointments
POST /appointments/                     - Create appointment
GET  /appointments/{id}/                - Get appointment details
PATCH /appointments/{id}/               - Update appointment
DELETE /appointments/{id}/              - Cancel appointment

# Provider-specific
GET  /appointments/provider-appointments/ - Provider's appointments
```

## 📊 Health Data (Token Required)
```
GET  /health-metrics/                   - List health metrics
POST /health-metrics/                   - Add health metric
GET  /health-metrics/{id}/              - Get metric details

GET  /iot-devices/                      - List IoT devices
POST /iot-devices/                      - Add IoT device

GET  /medications/                      - List medications
POST /medications/                      - Add medication

GET  /hospitals/                        - List hospitals
GET  /hospitals/search/?q=term          - Search hospitals
GET  /hospitals/dropdown/               - Hospitals for dropdown
```

---

## 🚀 Quick Start Examples

### Login & Get Token
```javascript
const response = await fetch('/api/v1/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const { tokens, role } = await response.json();
// Store tokens.access for subsequent requests
```

### Authenticated Request
```javascript
const response = await fetch('/api/v1/providers/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});

const providers = await response.json();
```

### Create Appointment
```javascript
const appointment = await fetch('/api/v1/appointments/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    healthcare_provider: 'provider-uuid',
    appointment_date: '2025-08-10T10:00:00Z',
    chief_complaint: 'Regular checkup',
    duration_minutes: 30
  })
});
```

---

## 📱 Role-Based Access

**User Role (`role.name === 'user'`)**:
- All user management endpoints
- View providers, hospitals
- Create/manage own appointments
- Add health metrics, IoT devices

**Provider Role (`role.name === 'provider'`)**:
- All user features +
- Provider profile management
- Provider dashboard
- View all provider appointments
- Access to patient data (with appointments)

---

## 🔧 Frontend Implementation Tips

1. **Store user role** after login to control UI elements
2. **Implement token refresh** for seamless experience
3. **Handle 401 errors** by redirecting to login
4. **Use role-based routing** (user dashboard vs provider dashboard)
5. **Implement search/filtering** for providers and appointments
6. **Add real-time updates** for appointment status changes

---

**🎯 Ready to integrate! Start with authentication, then build user/provider dashboards.**
