# JEGHealth Backend API

A comprehensive Django REST API backend for the JEGHealth mobile and web applications, providing secure health data management, IoT device integration, and user authentication.

## 🚀 Features

### ✅ **Completed Features**

#### 🔐 **Authentication & User Management**
- Custom User model with health-specific fields
- JWT-based authentication (login, logout, token refresh)
- User registration with email verification
- Role-based access control (user, admin, doctor)
- Comprehensive user profiles with medical information
- Password change functionality

#### 🏥 **Health Metrics System**
- Support for multiple health metric types:
  - Blood Pressure (systolic/diastolic)
  - Heart Rate
  - Weight
  - Blood Sugar
  - Temperature
  - Oxygen Saturation
  - Steps, Sleep Hours, Calories
  - BMI, Body Fat %, Muscle Mass
- Manual entry and IoT device integration
- Bulk health metrics creation for IoT devices
- Health metric targets and goals
- Statistical summaries (daily/weekly/monthly)
- Advanced filtering and analytics
- Anomaly detection capabilities

#### 📱 **IoT Device Integration**
- Device registration and management
- Support for multiple device types (smartwatches, fitness trackers, medical devices)
- Device verification and configuration
- Batch data upload processing
- Device status monitoring and health checks
- Device alerts and notifications
- API key authentication for devices
- Complex device configuration support

#### � **Appointments System**
- Appointment scheduling and management
- Healthcare provider integration
- Appointment status tracking
- Statistical reporting

#### 💊 **Medications Management**
- Medication tracking and reminders
- Medication categories and classifications
- Adherence monitoring
- Statistical reporting

#### �🔧 **Technical Infrastructure**
- PostgreSQL database support (SQLite for development)
- Redis caching and Celery task queue
- File storage with AWS S3 integration
- Comprehensive API documentation with Swagger/ReDoc
- CORS configuration for mobile app integration
- Structured logging system
- Robust error handling and validation
- Security best practices implementation

### � **Advanced Features** (Future Enhancements)
- Calendar integration
- Appointment reminders
- Telemedicine support

#### 💊 **Medication Management**
- Medication tracking and reminders
- Dosage scheduling
- Drug interaction checking
- Prescription management

#### 📊 **Analytics & Reporting**
- Health trend analysis
- Exportable reports (PDF/CSV)
- Dashboard analytics
- Health insights and recommendations

#### 🚨 **Notifications System**
- Email and push notifications
- Health alert thresholds
- Emergency contact notifications
- Medication reminders

## 📁 Project Structure

```
jeghealth_backend/
├── accounts/                 # User authentication & profiles
│   ├── models.py            # User, UserProfile, Role models
│   ├── serializers.py       # API serializers
│   ├── views.py             # Authentication endpoints
│   └── urls.py              # URL routing
├── health_metrics/          # Health data management
│   ├── models.py            # HealthMetric, Target, Summary models
│   ├── serializers.py       # Health data serializers
│   ├── views.py             # Health metric endpoints
│   └── urls.py              # URL routing
├── iot_devices/             # IoT device integration
│   ├── models.py            # IoTDevice, DataBatch, Alert models
│   ├── serializers.py       # Device data serializers
│   ├── views.py             # Device management endpoints
│   └── urls.py              # URL routing
├── appointments/            # Appointment system (planned)
├── medications/             # Medication tracking (planned)
├── jeghealth_backend/       # Main project settings
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI application
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── manage.py                # Django management script
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+ 
- Virtual environment (venv/conda)
- PostgreSQL (for production)
- Redis (for caching and Celery)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd jeghealth_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and configure your settings:

```env
# Database (for production, use PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=jeghealth_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,api.jeghealth.com

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=jeghealth-files

# Redis (for caching and Celery)
REDIS_URL=redis://localhost:6379/0
```

### 3. Database Setup
```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (optional)
python manage.py loaddata fixtures/initial_roles.json
```

### 4. Start Development Server
```bash
# Start Django server
python manage.py runserver

# In another terminal, start Celery worker (for background tasks)
celery -A jeghealth_backend worker -l info

# Start Celery beat (for scheduled tasks)
celery -A jeghealth_backend beat -l info
```

## 📚 API Documentation

### Base URL
- Development: `http://localhost:8000/api/v1/`
- Production: `https://your-domain.com/api/v1/`

### Interactive Documentation
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01"
}
```

#### Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Get Current User (matches your mobile app's getCurrentUser)
```http
GET /api/v1/auth/current-user/
Authorization: Bearer <access_token>
```

### Health Metrics Endpoints (Coming Soon)

#### Add Health Metric
```http
POST /api/v1/health-metrics/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "metric_type": "blood_pressure",
  "systolic_value": 120,
  "diastolic_value": 80,
  "unit": "mmHg",
  "recorded_at": "2025-07-24T12:00:00Z",
  "is_manual_entry": true,
  "notes": "Morning reading"
}
```

#### Get Health Metrics
```http
GET /api/v1/health-metrics/?metric_type=blood_pressure&limit=20
Authorization: Bearer <access_token>
```

## 🔗 Mobile App Integration

### Authentication Flow
Your mobile app can integrate with this backend by replacing Appwrite calls:

```javascript
// Replace AuthService.loginUser() with:
const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: email,
    password: password
  })
});

const data = await response.json();
// Store tokens in secure storage
await SecureStore.setItemAsync('access_token', data.tokens.access);
await SecureStore.setItemAsync('refresh_token', data.tokens.refresh);
```

### Health Metrics Integration
```javascript
// Replace DatabaseService.createHealthMetric() with:
const response = await fetch('http://localhost:8000/api/v1/health-metrics/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify(metricData)
});
```

## 🗄️ Database Models

### User Models
- **User**: Extended Django user with health-specific fields
- **UserProfile**: Detailed health profile (BMI, medical conditions, preferences)
- **Role**: Role-based permissions system
- **UserRole**: User-role assignments

### Health Models
- **HealthMetric**: Individual health readings
- **HealthMetricTarget**: User-defined health goals
- **HealthMetricSummary**: Statistical summaries for analytics

### IoT Models
- **IoTDevice**: Registered health devices
- **DeviceDataBatch**: Batch data uploads from devices
- **DeviceAlert**: Device status alerts and notifications

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Granular permissions system
- **API Key Authentication**: For IoT devices
- **Data Encryption**: Sensitive data encryption at rest
- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: Comprehensive data validation
- **Rate Limiting**: API rate limiting (production)

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML coverage report
```

## 🚀 Deployment

### Using Docker (Recommended)
```bash
# Build and run with docker-compose
docker-compose up -d

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Manual Deployment
1. Set up PostgreSQL and Redis
2. Configure environment variables for production
3. Collect static files: `python manage.py collectstatic`
4. Set up Nginx as reverse proxy
5. Use Gunicorn as WSGI server
6. Set up SSL certificates
7. Configure Celery worker and beat services

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Contact: your-email@example.com
- Documentation: [Link to detailed docs]

## 📄 License

[Your License Here]

---

**Note**: This backend is designed to seamlessly replace Appwrite in your existing JEGHealth mobile app while providing enhanced features, better performance, and full control over your health data infrastructure.
