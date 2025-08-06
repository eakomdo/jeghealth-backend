# JEGHealth Backend API

## 🏥 Complete Healthcare Management System

### Recent Updates:
- ✅ Separated healthcare providers into dedicated app
- ✅ Added doctor-specific appointment management
- ✅ Implemented RESTful API design principles
- ✅ Added hospital management with many-to-many relationships
- ✅ Created comprehensive appointment booking system
- ✅ Added analytics and statistics for doctors and patients
- ✅ Added JWT token validation endpoint for frontend integration

### API Endpoints:
- Authentication: `/api/v1/auth/` (login, register, token validation)
- Healthcare Providers: `/api/v1/providers/`
- Appointments: `/api/v1/appointments/`
- Doctor Dashboard: `/api/v1/appointments/doctor/{id}/`
- Hospitals: `/api/v1/hospitals/`

### Authentication:
- JWT authentication via Bearer token for protected endpoints
- Token validation endpoint: `POST /api/v1/auth/token/validate/`
- Token refresh endpoint: `POST /api/v1/auth/token/refresh/`

### Documentation:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`

