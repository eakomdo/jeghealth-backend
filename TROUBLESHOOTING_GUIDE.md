# 🚨 Troubleshooting Guide - Post-Pull Issues

## 📋 Overview
This guide addresses common issues that may occur after pulling the latest changes to the JEGHealth Backend project. The project has undergone significant enhancements including a complete healthcare provider system, AI integration, and frontend examples.

---

## 🔍 Quick Diagnosis

### **Step 1: Check Your Current State**
```bash
# Check if you're in the project directory
pwd
# Should show: /path/to/jeghealth-backend

# Check Git status
git status
git log --oneline -5

# Check Python version
python --version
# Should be Python 3.9+ (tested with 3.11, 3.12)

# Check if virtual environment exists
ls -la | grep venv
# Should see .venv/ directory
```

### **Step 2: Verify Environment Setup**
```bash
# Check if virtual environment is activated
which python
# Should show: /path/to/jeghealth-backend/.venv/bin/python

# If not activated, activate it:
source .venv/bin/activate    # macOS/Linux
# OR
.venv\Scripts\activate       # Windows

# Check installed packages
pip list | head -10
```

---

## 🚨 Common Issues & Solutions

### **Issue 1: Virtual Environment Problems**

**Symptoms:**
- `ModuleNotFoundError: No module named 'django'`
- `ImportError: Couldn't import Django`
- Python packages not found

**Solution:**
```bash
# Recreate virtual environment
rm -rf .venv  # Remove old environment
python3 -m venv .venv  # Create new environment
source .venv/bin/activate  # Activate it

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import django; print(django.VERSION)"
```

### **Issue 2: Database Migration Issues**

**Symptoms:**
- `django.db.utils.OperationalError`
- `no such table` errors
- Migration conflicts

**Solution:**
```bash
# Check current migration status
python manage.py showmigrations

# If there are conflicts, reset migrations (DEVELOPMENT ONLY)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations
python manage.py makemigrations accounts
python manage.py makemigrations providers  
python manage.py makemigrations health_metrics
python manage.py makemigrations iot_devices
python manage.py makemigrations appointments
python manage.py makemigrations medications
python manage.py makemigrations hospitals
python manage.py makemigrations dr_jeg

# Apply migrations
python manage.py migrate

# If you get foreign key errors, try:
python manage.py migrate --run-syncdb
```

### **Issue 3: Environment Variables Missing**

**Symptoms:**
- `KeyError: 'SECRET_KEY'`
- `Environment variable not set`
- Settings errors

**Solution:**
```bash
# Check if .env file exists
ls -la | grep .env

# If missing, create from template
cp .env.example .env

# Generate a new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())" >> .env

# Edit .env file with required settings
cat >> .env << EOF
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
EOF
```

### **Issue 4: New Dependencies Not Installed**

**Symptoms:**
- `ModuleNotFoundError` for new packages
- Import errors for new features

**Solution:**
```bash
# Update pip first
pip install --upgrade pip

# Install/update all requirements
pip install -r requirements.txt

# If there are conflicts, use force-reinstall
pip install --force-reinstall -r requirements.txt

# Check specific new dependencies
pip show google-generativeai
pip show django-phonenumber-field
pip show drf-spectacular
```

### **Issue 5: Database Schema Conflicts**

**Symptoms:**
- `IntegrityError`
- `Column doesn't exist` errors
- Foreign key constraint failures

**Solution:**
```bash
# Backup current database (if important)
cp db.sqlite3 db.sqlite3.backup

# Reset database completely (DEVELOPMENT ONLY)
rm db.sqlite3

# Recreate database
python manage.py migrate

# Create new superuser
python manage.py createsuperuser

# Load sample data
python create_doctors.py
python create_sample_data.py
```

### **Issue 6: Port Already in Use**

**Symptoms:**
- `Error: That port is already in use.`
- Server won't start on port 8000

**Solution:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
python manage.py runserver 8001
```

### **Issue 7: Permission Errors**

**Symptoms:**
- Permission denied errors
- Cannot write to directories
- Media/logs folder issues

**Solution:**
```bash
# Fix permissions for media and logs directories
sudo chown -R $USER:$USER media/
sudo chown -R $USER:$USER logs/
sudo chmod -R 755 media/
sudo chmod -R 755 logs/

# Create missing directories
mkdir -p media/profile_images
mkdir -p media/license_documents
mkdir -p logs/
```

### **Issue 8: New Model Dependencies**

**Symptoms:**
- Errors with new models (HealthcareProvider, Hospital, etc.)
- Relations not found

**Solution:**
```bash
# Ensure all apps are in INSTALLED_APPS
python -c "
from django.conf import settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeghealth_backend.settings')
import django
django.setup()
print('Installed apps:', settings.INSTALLED_APPS)
"

# Check for missing apps in settings.py
grep -A 20 "INSTALLED_APPS" jeghealth_backend/settings.py

# If apps are missing, they should include:
# 'providers', 'hospitals', 'dr_jeg'
```

---

## 🔧 Complete Reset Procedure (Nuclear Option)

**If nothing else works, use this complete reset:**

```bash
# 1. Backup important data
cp db.sqlite3 backup_db.sqlite3 2>/dev/null || true
cp -r media/ backup_media/ 2>/dev/null || true

# 2. Clean everything
rm -rf .venv/
rm db.sqlite3 2>/dev/null || true
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/__pycache__/*" -delete
find . -name "*.pyc" -delete

# 3. Fresh start
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())" >> .env
echo "DEBUG=True" >> .env
echo "ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0" >> .env
echo "DB_ENGINE=django.db.backends.sqlite3" >> .env
echo "DB_NAME=db.sqlite3" >> .env

# 5. Database setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# 6. Test
python manage.py runserver
```

---

## ✅ Verification Steps

### **After fixing issues, verify everything works:**

```bash
# 1. Check Django setup
python manage.py check

# 2. Test database connection
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
print(f'User model: {User}');
print(f'User count: {User.objects.count()}')
"

# 3. Test API endpoints
curl -X GET http://127.0.0.1:8000/api/v1/

# 4. Test provider registration
bash test_real_provider_complete.sh

# 5. Test admin panel
# Visit http://127.0.0.1:8000/admin/

# 6. Test API documentation
# Visit http://127.0.0.1:8000/api/docs/
```

---

## 📊 New Features to Test

### **Healthcare Provider System:**
```bash
# Test provider registration
curl -X POST http://127.0.0.1:8000/api/v1/auth/provider/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "professional_title": "Dr.",
    "first_name": "Test",
    "last_name": "Doctor",
    "email": "test.doctor@hospital.com",
    "password": "TestPass123",
    "password_confirm": "TestPass123",
    "organization_facility": "Test Hospital",
    "professional_role": "Physician",
    "license_number": "TEST123456"
  }'
```

### **AI Assistant (Dr. JEG):**
```bash
# Test AI chat (requires GOOGLE_API_KEY in .env)
python test_dr_jeg_api.py
```

### **New Models in Admin:**
Visit http://127.0.0.1:8000/admin/ and verify you can see:
- Healthcare Providers
- Hospitals  
- Dr. JEG Conversations
- Updated User Profiles

---

## 🆘 If Issues Persist

### **Collect Debug Information:**
```bash
# System info
python --version
pip --version
which python
echo $VIRTUAL_ENV

# Django info
python manage.py version
python manage.py check --deploy

# Database info
python manage.py dbshell .schema 2>/dev/null | head -20 || echo "SQLite not accessible"

# Environment info
cat .env | grep -v SECRET_KEY | grep -v PASSWORD

# Package versions
pip show django djangorestframework django-cors-headers

# Recent git changes
git log --oneline -10
git diff HEAD~5..HEAD --stat
```

### **Create a Bug Report:**
Include this information:
1. Operating system (macOS, Linux, Windows)
2. Python version
3. Virtual environment status
4. Error messages (full traceback)
5. Debug information from above
6. Steps that led to the issue

---

## 🎯 Success Indicators

**You know it's working when:**
- ✅ `python manage.py runserver` starts without errors
- ✅ http://127.0.0.1:8000/api/v1/ shows the API root
- ✅ http://127.0.0.1:8000/admin/ loads the admin panel
- ✅ http://127.0.0.1:8000/api/docs/ shows API documentation  
- ✅ Test scripts run without errors
- ✅ You can register new users and providers
- ✅ Database queries work in Django shell

---

**📞 Need more help?** 
- Check the logs in `logs/django.log`
- Review the comprehensive setup guide: `PROJECT_SETUP_GUIDE.md`
- Use the provided test scripts to isolate issues
- Check Django's debug output for detailed error information
