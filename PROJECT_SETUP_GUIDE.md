# 🚀 JEGHealth Backend - Complete Setup Guide

## 📋 Overview
This is a comprehensive setup guide for the JEGHealth Backend Django project. This guide includes all the changes and enhancements that were made during development, including the complete healthcare provider system, authentication improvements, and frontend integration capabilities.

---

## 🔧 Prerequisites

### **System Requirements:**
- **Python 3.9+** (Tested with Python 3.11, 3.12)
- **Git** for version control
- **Terminal/Command Line** access

### **Recommended Tools:**
- **VS Code** or **PyCharm** for development
- **Postman** or **Thunder Client** for API testing
- **PostgreSQL** (for production deployment)

---

## ⚡ Quick Setup (Development)

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd jeghealth-backend
```

### **2. Create and Activate Virtual Environment**

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (should show (.venv) in prompt)
which python
```

**On Windows:**
```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Verify activation
where python
```

### **3. Install Dependencies**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all project dependencies
pip install -r requirements.txt
```

### **4. Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
```

**Required .env Configuration:**
```bash
# Django Settings
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (SQLite for development)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# JWT Settings (optional - has defaults)
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=10080

# Email Settings (optional for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Google API (optional)
GOOGLE_API_KEY=your-google-api-key

# AWS S3 (optional for file uploads)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

# Redis (optional for caching)
REDIS_URL=redis://localhost:6379/0

# Celery (optional for background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### **5. Database Setup**
```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### **6. Load Sample Data (Optional)**
```bash
# Create sample healthcare providers
python create_doctors.py

# Create sample health data
python create_sample_data.py
```

### **7. Run the Development Server**
```bash
# Start the Django development server
python manage.py runserver

# Server will start at http://127.0.0.1:8000/
```

### **8. Verify Installation**
Open your browser and visit:
- **API Root:** http://127.0.0.1:8000/api/v1/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API Documentation:** http://127.0.0.1:8000/api/docs/

---

## 📦 Project Structure

```
jeghealth-backend/
├── accounts/                    # User authentication & profiles
├── health_metrics/             # Health data tracking
├── iot_devices/               # IoT device management
├── appointments/              # Appointment scheduling
├── medications/               # Medication management
├── providers/                 # Healthcare providers
├── hospitals/                 # Hospital management
├── dr_jeg/                   # AI chatbot integration
├── jeghealth_backend/        # Main Django project
├── media/                    # User uploads
├── static/                   # Static files
├── logs/                     # Application logs
├── frontend-examples/        # Frontend integration examples
├── requirements.txt          # Python dependencies
├── manage.py                # Django management script
├── .env.example             # Environment template
└── db.sqlite3              # SQLite database (development)
```

---

## 🔍 Key Features & Endpoints

### **🔐 Authentication System**
- **User Registration:** `POST /api/v1/auth/register/`
- **User Login:** `POST /api/v1/auth/login/`
- **Token Refresh:** `POST /api/v1/auth/token/refresh/`
- **Provider Registration:** `POST /api/v1/auth/provider/register/`
- **Provider Dashboard:** `GET /api/v1/auth/provider/dashboard/`

### **🏥 Healthcare Provider System**
- **Provider Directory:** `GET /api/v1/providers/`
- **Provider Search:** `GET /api/v1/providers/search/`
- **Provider Profile:** `GET/PATCH /api/v1/auth/provider/profile/`
- **Provider by Hospital:** `GET /api/v1/providers/hospital/{id}/`

### **📊 Health Metrics**
- **Metrics CRUD:** `/api/v1/health-metrics/`
- **Bulk Upload:** `POST /api/v1/health-metrics/bulk-create/`
- **Statistics:** `GET /api/v1/health-metrics/statistics/`
- **Anomaly Detection:** `GET /api/v1/health-metrics/anomalies/`

### **🔌 IoT Device Integration**
- **Device Management:** `/api/v1/iot-devices/`
- **Device Registration:** `POST /api/v1/iot-devices/register/`
- **Data Upload:** `POST /api/v1/iot-devices/{id}/upload-data/`
- **Device Health Check:** `GET /api/v1/iot-devices/{id}/health/`

### **🤖 AI Chatbot (Dr. JEG)**
- **Chat Interface:** `POST /api/v1/dr-jeg/chat/`
- **Health Analysis:** `POST /api/v1/dr-jeg/analyze-health/`
- **Conversation History:** `GET /api/v1/dr-jeg/conversations/`

---

## 🧪 Testing the System

### **1. API Testing Scripts**
The project includes comprehensive test scripts:

```bash
# Test provider registration and authentication
bash test_real_provider_complete.sh

# Test all provider endpoints
bash test_comprehensive_provider_endpoints.sh

# Test Dr. JEG AI functionality
python test_dr_jeg_api.py

# Test IoT device integration
python test_iot_devices.py
```

### **2. Manual API Testing**
Use Postman or curl to test endpoints:

```bash
# Register a new user
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login and get token
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### **3. Admin Panel Testing**
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Verify all models are accessible and working

---

## 🚨 Common Issues & Solutions

### **Issue 1: ModuleNotFoundError**
```bash
# Solution: Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### **Issue 2: Database Migration Errors**
```bash
# Reset migrations (development only)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

### **Issue 3: Secret Key Error**
```bash
# Generate a new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Add it to your .env file
echo "SECRET_KEY=your-generated-secret-key" >> .env
```

### **Issue 4: Port Already in Use**
```bash
# Use a different port
python manage.py runserver 8001

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### **Issue 5: CORS Issues (Frontend Integration)**
The project is configured to allow all CORS origins in development. If you have issues:

```python
# In settings.py, ensure these are set:
CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['*']  # Development only
```

---

## 🌐 Production Deployment

### **PostgreSQL Setup**
```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Update .env for production:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=jeghealth_db
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### **Production Environment Variables**
```bash
# Security
SECRET_KEY=your-very-secure-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
# ... (PostgreSQL settings)

# Email (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# File Storage (AWS S3)
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-west-2
```

### **Production Commands**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
pip install gunicorn
gunicorn jeghealth_backend.wsgi:application --bind 0.0.0.0:8000
```

---

## 📱 Frontend Integration

### **Frontend Examples Provided**
The project includes complete frontend integration examples:

- **React Components:** `frontend-examples/ProviderRegistration.jsx`
- **API Service:** `frontend-examples/providerAPI.js`
- **CSS Styles:** `frontend-examples/provider-styles.css`
- **Integration Guide:** `PROVIDER_FRONTEND_INTEGRATION_GUIDE.md`

### **Frontend Setup Steps**
```bash
# If using React
npx create-react-app jeghealth-frontend
cd jeghealth-frontend

# Copy the provided frontend examples
cp ../jeghealth-backend/frontend-examples/* src/

# Install additional dependencies
npm install axios react-router-dom

# Start frontend development server
npm start
```

---

## 🔧 Development Tools

### **Django Management Commands**
```bash
# Create new Django app
python manage.py startapp app_name

# Make database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell

# Show URLs
python manage.py show_urls

# Check for issues
python manage.py check
```

### **Database Management**
```bash
# Database shell
python manage.py dbshell

# Reset specific app migrations
python manage.py migrate app_name zero
python manage.py migrate app_name

# Show migration status
python manage.py showmigrations
```

### **Debugging Tools**
```bash
# Run with debugging
python manage.py runserver --settings=jeghealth_backend.settings_debug

# Check installed packages
pip list

# Check for security issues
python manage.py check --deploy
```

---

## 📊 API Documentation

### **Swagger/OpenAPI Documentation**
- **Interactive Docs:** http://127.0.0.1:8000/api/docs/
- **Schema JSON:** http://127.0.0.1:8000/api/schema/

### **Authentication Testing**
```bash
# Get authentication token
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "yourpassword"}'

# Use token in subsequent requests
curl -X GET http://127.0.0.1:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎯 Recent Enhancements

### **Healthcare Provider System** (Major Update)
- Complete professional registration form
- Professional titles and roles
- License verification system
- Organization/facility management
- Provider search and directory
- Dashboard with statistics

### **Authentication Improvements**
- JWT token refresh mechanism
- Password strength validation
- Email uniqueness validation
- Role-based access control

### **Frontend Integration**
- Complete React component examples
- API service layer
- CSS styling framework
- Integration documentation

### **AI Integration (Dr. JEG)**
- Google Gemini AI chatbot
- Health data analysis
- Conversation history
- Medical advice system

---

## 💻 IDE Setup Recommendations

### **VS Code Extensions**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.pylint",
    "batisteo.vscode-django",
    "ms-vscode.vscode-thunder-client",
    "bradlc.vscode-tailwindcss"
  ]
}
```

### **VS Code Settings**
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true
}
```

---

## 🚀 Next Steps After Setup

1. **Test the API endpoints** using the provided test scripts
2. **Explore the admin panel** to understand the data models
3. **Review the API documentation** at `/api/docs/`
4. **Try the frontend integration** using provided examples
5. **Test the AI chatbot** functionality
6. **Set up production environment** when ready to deploy

---

## 📞 Support & Troubleshooting

### **Getting Help**
- Check this setup guide first
- Review the comprehensive API documentation
- Use the provided test scripts to verify functionality
- Check Django logs in the `logs/` directory

### **Common Development Workflow**
```bash
# Daily development routine
source .venv/bin/activate      # Activate environment
git pull origin main           # Get latest changes
pip install -r requirements.txt # Update dependencies
python manage.py migrate       # Apply any new migrations
python manage.py runserver     # Start development server
```

---

**🎉 The JEGHealth Backend is now fully set up and ready for development! This setup includes all the enhancements and features that were added during the development process, including the comprehensive healthcare provider system, AI integration, and frontend-ready API endpoints.**
