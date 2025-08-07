# Healthcare Provider Registration & Management API

## Complete Provider Form Fields (Updated)

### Professional Registration Endpoint

**Endpoint**: `POST /api/v1/auth/provider/register/`

### Required Request Body Structure:

```json
{
  // Personal Information
  "professional_title": "Dr.",          // Required dropdown choice
  "first_name": "Joseph",               // Required text
  "last_name": "Ewool",                 // Required text
  
  // Contact Information  
  "email": "joseph.ewool@hospital.com", // Required email
  "phone_number": "+15551234567",       // Optional phone with country code
  
  // Security
  "username": "joseph_ewool",           // Required username
  "password": "SecurePass123!",         // Required min 8 chars
  "password_confirm": "SecurePass123!", // Required must match
  
  // Professional Information
  "organization_facility": "General Hospital",  // Required organization
  "professional_role": "Physician",             // Required dropdown choice
  "specialization": "Emergency Medicine",       // Optional specialization
  
  // License Verification
  "license_number": "MD123456789",      // Required for verification
  
  // Additional Information
  "additional_information": "Specialized in IoT cardiac monitoring devices and emergency telemedicine applications", // Optional textarea
  
  // Legacy fields (optional - backward compatibility)
  "years_of_experience": 5,             // Optional number
  "consultation_fee": "200.00",         // Optional decimal
  "bio": "Emergency physician with focus on digital health",
  "hospital_clinic": "General Hospital",
  "address": "123 Medical Center Dr, Health City, HC 12345"
}
```

### Professional Title Options:
- `"Dr."` - Dr. (Doctor)
- `"Prof."` - Prof. (Professor)  
- `"RN"` - RN (Registered Nurse)
- `"LPN"` - LPN (Licensed Practical Nurse)
- `"NP"` - NP (Nurse Practitioner)
- `"PA"` - PA (Physician Assistant)
- `"RPh"` - RPh (Pharmacist)
- `"PT"` - PT (Physical Therapist)
- `"OT"` - OT (Occupational Therapist)
- `"RT"` - RT (Respiratory Therapist)
- `"MT"` - MT (Medical Technologist)
- `"RD"` - RD (Registered Dietitian)
- `"MSW"` - MSW (Medical Social Worker)
- `"Mr."` - Mr.
- `"Ms."` - Ms.
- `"Mrs."` - Mrs.

### Professional Role Options:
- `"Physician"`
- `"Registered Nurse"`
- `"Specialist"`
- `"Healthcare Administrator"`
- `"Medical Technician"`
- `"Other"`

---

## Complete Provider Endpoints

### 1. Provider Registration
```
POST /api/v1/auth/provider/register/
Content-Type: application/json
```

### 2. Provider Login (Same as regular login)
```
POST /api/v1/auth/login/
Content-Type: application/json

Body:
{
  "email": "joseph.ewool@hospital.com",
  "password": "SecurePass123!"
}
```

### 3. Provider Profile (Get)
```
GET /api/v1/auth/provider/profile/
Authorization: Bearer <provider_token>
```

### 4. Provider Profile (Update)
```
PATCH /api/v1/auth/provider/profile/
Authorization: Bearer <provider_token>
Content-Type: application/json

Body:
{
  "additional_information": "Updated IoT monitoring specialization",
  "professional_role": "Specialist",
  "consultation_fee": "250.00"
}
```

### 5. Provider Dashboard
```
GET /api/v1/auth/provider/dashboard/
Authorization: Bearer <provider_token>
```

### 6. List All Providers
```
GET /api/v1/providers/
Authorization: Bearer <token>
Query params: ?search=emergency&professional_role=Physician
```

### 7. Provider Details
```
GET /api/v1/providers/{provider_id}/
Authorization: Bearer <token>
```

### 8. Provider Search/Autocomplete
```
GET /api/v1/providers/search/?q=Joseph
Authorization: Bearer <token>
```

### 9. Provider Dropdown
```
GET /api/v1/providers/dropdown/
Authorization: Bearer <token>
Query params: ?professional_role=Physician
```

### 10. Provider Appointments
```
GET /api/v1/appointments/provider-appointments/
Authorization: Bearer <provider_token>
```

---

## Form Validation Rules

### Required Fields:
- ✅ professional_title (dropdown selection)
- ✅ first_name (text input)
- ✅ last_name (text input)
- ✅ email (valid email format)
- ✅ username (unique)
- ✅ password (minimum 8 characters)
- ✅ password_confirm (must match password)
- ✅ organization_facility (text input)
- ✅ professional_role (dropdown selection)  
- ✅ license_number (unique, for verification)

### Optional Fields:
- phone_number (international format)
- specialization (text input)
- additional_information (textarea)
- years_of_experience (number)
- consultation_fee (decimal)
- bio, hospital_clinic, address (legacy fields)

### Validation Rules:
1. **Password**: Minimum 8 characters, must match confirmation
2. **Email**: Valid email format, unique in system
3. **License Number**: Must be unique across all providers
4. **Phone**: International format validation when provided
5. **Professional Title & Role**: Must be from predefined dropdown options

---

## Success Response Format

### Registration Success:
```json
{
  "message": "Healthcare provider registered successfully",
  "authUser": {
    "id": 8,
    "email": "joseph.ewool@hospital.com",
    "username": "joseph_ewool",
    "first_name": "Joseph",
    "last_name": "Ewool",
    "phone_number": "+15551234567",
    "roles": ["provider"],
    "permissions": {
      "can_view_own_data": true,
      "can_edit_own_profile": true,
      "can_view_appointments": true,
      "can_manage_appointments": true,
      "can_view_patient_data": true,
      "can_add_medical_records": true,
      "can_prescribe_medications": true
    }
  },
  "role": {
    "name": "provider",
    "permissions": {...}
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### Profile Response:
```json
{
  "id": "uuid-string",
  "professional_title": "Dr.",
  "first_name": "Joseph",
  "last_name": "Ewool", 
  "email": "joseph.ewool@hospital.com",
  "phone_number": "+15551234567",
  "organization_facility": "General Hospital",
  "professional_role": "Physician",
  "specialization": "Emergency Medicine",
  "license_number": "MD123456789",
  "license_verified": false,
  "additional_information": "Specialized in IoT cardiac monitoring...",
  "years_of_experience": 5,
  "consultation_fee": "200.00",
  "is_active": true,
  "created_at": "2025-08-07T10:30:00Z",
  "updated_at": "2025-08-07T10:30:00Z"
}
```

---

## Frontend Integration Examples

### React Registration Form:
```jsx
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('/api/v1/auth/provider/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Store tokens and redirect
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('user_role', 'provider');
        window.location.href = '/provider-dashboard';
      }
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Professional Title */}
      <select 
        value={formData.professional_title}
        onChange={(e) => setFormData({...formData, professional_title: e.target.value})}
        required
      >
        <option value="Dr.">Dr. (Doctor)</option>
        <option value="Prof.">Prof. (Professor)</option>
        <option value="RN">RN (Registered Nurse)</option>
        {/* ... other options */}
      </select>

      {/* Name Fields */}
      <input
        type="text"
        placeholder="Joseph"
        value={formData.first_name}
        onChange={(e) => setFormData({...formData, first_name: e.target.value})}
        required
      />
      
      <input
        type="text" 
        placeholder="Ewool"
        value={formData.last_name}
        onChange={(e) => setFormData({...formData, last_name: e.target.value})}
        required
      />

      {/* Email */}
      <input
        type="email"
        placeholder="joseph.ewool@hospital.com"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required
      />

      {/* Professional Role */}
      <select
        value={formData.professional_role}
        onChange={(e) => setFormData({...formData, professional_role: e.target.value})}
        required
      >
        <option value="Physician">Physician</option>
        <option value="Registered Nurse">Registered Nurse</option>
        <option value="Specialist">Specialist</option>
        {/* ... other options */}
      </select>

      {/* License Number */}
      <input
        type="text"
        placeholder="MD123456789"
        value={formData.license_number}
        onChange={(e) => setFormData({...formData, license_number: e.target.value})}
        required
      />

      {/* Additional Info Textarea */}
      <textarea
        rows="4"
        placeholder="Tell us about your specific IoT monitoring needs..."
        value={formData.additional_information}
        onChange={(e) => setFormData({...formData, additional_information: e.target.value})}
      />

      <button type="submit">Register as Healthcare Provider</button>
    </form>
  );
};
```

---

**Ready for implementation with complete professional form validation!** 🏥
