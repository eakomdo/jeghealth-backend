# JEGHealth Backend API

A comprehensive Django REST API backend for the JEGHealth mobile and web applications, providing secure health data management, IoT device integration, healthcare provider system, AI-powered health assistance, and complete user authentication.

## 🎯 Quick Start

**New to this project? Start here:**
1. 📖 **[Complete Setup Guide](PROJECT_SETUP_GUIDE.md)** - Comprehensive installation and configuration
2. 🧪 **[API Testing](test_real_provider_complete.sh)** - Test all endpoints with real data
3. 💻 **[Frontend Integration](PROVIDER_FRONTEND_INTEGRATION_GUIDE.md)** - Complete frontend examples and docs
4. 🤖 **[AI Chatbot](test_dr_jeg_api.py)** - Test Dr. JEG AI functionality
5. 📱 **[Mobile Integration](#mobile-app-integration)** - Connect your mobile app

---

## 🚀 Features

### ✅ **Completed Features**

#### 🔐 **Authentication & User Management**
- Custom User model with comprehensive health-specific fields
- JWT-based authentication (login, logout, token refresh, validation)
- User registration with email verification
- **Healthcare Provider Registration System** with professional credentials
- Role-based access control (user, admin, provider)
- Comprehensive user profiles with medical information
- Password change functionality with strength validation
- License verification system for healthcare providers

#### 🏥 **Healthcare Provider System** (NEW)
- **Professional Registration Form** with all required fields:
  - Professional titles (Dr., RN, NP, PA, etc.)
  - Organization/Facility information
  - Professional roles and specializations  
  - License number and verification
  - Contact information and credentials
- **Provider Dashboard** with statistics and recent activities
- **Provider Directory & Search** with advanced filtering
- **Provider Profile Management** with real-time updates
- **Hospital Integration** and provider-hospital relationships
- **License Document Upload** and verification workflow

#### 📊 **Health Metrics System**
- Support for 15+ health metric types:
  - Blood Pressure (systolic/diastolic)
  - Heart Rate, Weight, Blood Sugar, Temperature
  - Oxygen Saturation, Steps, Sleep Hours, Calories
  - BMI, Body Fat %, Muscle Mass, Cholesterol
  - Medication Adherence, Exercise Minutes
- Manual entry and IoT device integration
- Bulk health metrics creation for IoT devices
- Health metric targets and goals with progress tracking
- Statistical summaries (daily/weekly/monthly/yearly)
- Advanced filtering and analytics with trend analysis
- Anomaly detection capabilities with alerts

#### 📱 **IoT Device Integration**
- Device registration and management with API keys
- Support for multiple device types (smartwatches, fitness trackers, medical devices)
- Device verification and configuration management
- Batch data upload processing with error handling
- Device status monitoring and health checks
- Device alerts and notifications system
- Complex device configuration support
- Real-time data streaming capabilities

#### 📅 **Appointments System**
- Appointment scheduling and management
- Healthcare provider integration with availability
- Appointment status tracking (scheduled, confirmed, completed, cancelled)
- Statistical reporting and analytics
- Reminder notifications system
- Integration with provider calendars

#### 💊 **Medications Management**
- Medication tracking and adherence monitoring
- Prescription management with provider integration
- Dosage tracking and reminder system
- Side effects and notes documentation
- Integration with health metrics for adherence analysis

#### 🤖 **AI-Powered Health Assistant (Dr. JEG)**
- **Google Gemini AI Integration** for intelligent health advice
- **Conversational Interface** with medical knowledge
- **Health Data Analysis** with personalized insights
- **Symptom Assessment** and recommendation system
- **Conversation History** with context awareness
- **Medical Information** lookup and explanations
- **Health Trend Analysis** with AI-powered insights

#### 🏥 **Hospital Management System**
- Hospital registration and profile management
- Department and service listings
- Provider-hospital relationships and affiliations
- Location and contact information management
- Integration with appointment and provider systems

### 🔄 **Advanced Features**

#### 🔒 **Security & Compliance**
- JWT token management with automatic refresh
- API key authentication for IoT devices
- Role-based permissions system
- Data encryption and secure storage
- HIPAA-compliant data handling practices
- Audit logging for all sensitive operations
- Rate limiting and DDoS protection

#### 📊 **Analytics & Reporting**
- Real-time health metrics dashboards
- Provider performance analytics
- System usage statistics
- Health trend analysis with ML insights
- Custom report generation
- Data export capabilities (CSV, JSON, PDF)

#### 🌐 **API & Integration**
- **RESTful API Design** with consistent endpoints
- **OpenAPI/Swagger Documentation** with interactive testing
- **CORS Configuration** for web application integration
- **Comprehensive Frontend Examples** (React components, CSS, API service)
- **Mobile App Integration** support with secure token management
- **Webhook Support** for real-time notifications
- **Third-party Integration** capabilities (Google Health, Apple HealthKit)

---

## 📂 Project Structure

```
jeghealth-backend/
├── accounts/                    # 👥 User authentication & profiles
│   ├── models.py               # User, UserProfile, Role models
│   ├── serializers.py          # User & provider serializers
│   ├── views.py               # Auth endpoints & provider registration
│   └── urls.py                # Authentication routes
├── providers/                   # 🏥 Healthcare provider system
│   ├── models.py               # HealthcareProvider model
│   ├── serializers.py          # Provider data serializers  
│   ├── views.py               # Provider directory & search
│   └── urls.py                # Provider routes
├── health_metrics/             # 📊 Health data tracking
│   ├── models.py               # HealthMetric, Target, Summary models
│   ├── serializers.py          # Health data serializers
│   ├── views.py               # Health metric endpoints
│   └── urls.py                # Health metrics routes
├── iot_devices/               # 🔌 IoT device integration
│   ├── models.py               # IoTDevice, DataBatch, Alert models
│   ├── serializers.py          # Device data serializers
│   ├── views.py               # Device management endpoints
│   └── urls.py                # IoT device routes
├── appointments/              # 📅 Appointment scheduling
│   ├── models.py               # Appointment, Schedule models
│   ├── serializers.py          # Appointment serializers
│   ├── views.py               # Appointment endpoints
│   └── urls.py                # Appointment routes
├── medications/               # 💊 Medication tracking
│   ├── models.py               # Medication, Prescription models
│   ├── serializers.py          # Medication serializers
│   ├── views.py               # Medication endpoints
│   └── urls.py                # Medication routes
├── hospitals/                 # 🏥 Hospital management
│   ├── models.py               # Hospital, Department models
│   ├── serializers.py          # Hospital serializers
│   ├── views.py               # Hospital endpoints
│   └── urls.py                # Hospital routes
├── dr_jeg/                    # 🤖 AI health assistant
│   ├── models.py               # Conversation, Message models
│   ├── serializers.py          # AI conversation serializers
│   ├── views.py               # AI chat endpoints
│   ├── gemini_service.py      # Google Gemini AI integration
│   └── urls.py                # AI assistant routes
├── frontend-examples/         # 💻 Frontend integration examples
│   ├── ProviderRegistration.jsx   # React registration component
│   ├── ProviderDashboard.jsx      # React dashboard component  
│   ├── ProviderSearch.jsx         # React search component
│   ├── providerAPI.js             # API service layer
│   └── provider-styles.css        # Complete CSS styling
├── jeghealth_backend/         # ⚙️ Main project settings
│   ├── settings.py             # Django configuration
│   ├── urls.py                # Main URL routing
│   └── wsgi.py                # WSGI application
├── media/                     # 📁 User uploads (profile pics, docs)
├── static/                    # 🎨 Static files (CSS, JS, images)  
├── logs/                      # 📋 Application logs
├── requirements.txt           # 📦 Python dependencies
├── .env.example              # 🔧 Environment template
├── PROJECT_SETUP_GUIDE.md    # 📖 Complete setup instructions
├── PROVIDER_FRONTEND_INTEGRATION_GUIDE.md  # 💻 Frontend integration docs
└── manage.py                 # 🐍 Django management script
```

---

## 🛠️ Installation & Setup

### 🚀 Quick Setup (5 minutes)
```bash
# 1. Clone repository
git clone <repository-url>
cd jeghealth-backend

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your settings (SECRET_KEY is required)

# 5. Setup database
python manage.py migrate
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver
```

**🎯 For detailed setup instructions, see [PROJECT_SETUP_GUIDE.md](PROJECT_SETUP_GUIDE.md)**

### 🧪 Test the Installation
```bash
# Test provider registration and authentication
bash test_real_provider_complete.sh

# Test AI chatbot functionality  
python test_dr_jeg_api.py

# Test IoT device integration
python test_iot_devices.py
```

---

## 📚 API Documentation

### 🌐 Base URLs
- **Development:** `http://localhost:8000/api/v1/`  
- **Production:** `https://your-domain.com/api/v1/`

### 📖 Interactive Documentation
- **Swagger UI:** `http://localhost:8000/api/docs/` - Interactive API testing
- **ReDoc:** `http://localhost:8000/api/redoc/` - Beautiful API documentation
- **OpenAPI Schema:** `http://localhost:8000/api/schema/` - Machine-readable API spec

### 🔐 Authentication Endpoints

#### User Registration
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "first_name": "John", 
  "last_name": "Doe",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01"
}
```

#### User Login  
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": { ... }
}
```

#### Healthcare Provider Registration
```http
POST /api/v1/auth/provider/register/
Content-Type: application/json

{
  "professional_title": "Dr.",
  "first_name": "Joseph",
  "last_name": "Ewool", 
  "email": "joseph.ewool@hospital.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "organization_facility": "General Hospital",
  "professional_role": "Physician",
  "license_number": "MD123456789",
  "specialization": "Cardiology"
}
```

### 🏥 Provider System Endpoints
```http
GET /api/v1/providers/                    # List all providers
GET /api/v1/providers/search/             # Search providers  
GET /api/v1/providers/{id}/               # Provider details
GET /api/v1/auth/provider/profile/        # Current provider profile
PATCH /api/v1/auth/provider/profile/      # Update provider profile
GET /api/v1/auth/provider/dashboard/      # Provider dashboard
```

### 📊 Health Metrics Endpoints
```http
GET /api/v1/health-metrics/               # List health metrics
POST /api/v1/health-metrics/              # Create health metric
GET /api/v1/health-metrics/statistics/    # Get health statistics
POST /api/v1/health-metrics/bulk-create/  # Bulk upload metrics
```

### 🤖 AI Assistant (Dr. JEG) Endpoints
```http
POST /api/v1/dr-jeg/chat/                 # Chat with AI assistant
POST /api/v1/dr-jeg/analyze-health/       # Analyze health data
GET /api/v1/dr-jeg/conversations/         # Get chat history
```

---
