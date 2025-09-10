# JEGHealth Backend System Architecture Diagrams

This document contains comprehensive UML and sequence diagrams for the JEGHealth backend system, illustrating the relationships between models, API flows, and system interactions.

## Table of Contents
1. [Entity Relationship Diagram (ERD)](#entity-relationship-diagram-erd)
2. [Class Diagram - Core Models](#class-diagram---core-models)
3. [Authentication Flow Sequence Diagram](#authentication-flow-sequence-diagram)
4. [Appointment Booking Sequence Diagram](#appointment-booking-sequence-diagram)
5. [Dr. Jeg AI Chat Sequence Diagram](#dr-jeg-ai-chat-sequence-diagram)
6. [Health Metrics Recording Sequence Diagram](#health-metrics-recording-sequence-diagram)
7. [Provider Management Flow](#provider-management-flow)
8. [IoT Device Integration Flow](#iot-device-integration-flow)
9. [System Architecture Overview](#system-architecture-overview)

---

## Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    User {
        id UUID PK
        username VARCHAR
        email VARCHAR UK
        first_name VARCHAR
        last_name VARCHAR
        phone_number VARCHAR
        date_of_birth DATE
        profile_image ImageField
        emergency_contact_name VARCHAR
        emergency_contact_phone VARCHAR
        is_email_verified BOOLEAN
        is_phone_verified BOOLEAN
        created_at DATETIME
        updated_at DATETIME
    }
    
    UserProfile {
        id UUID PK
        user_id UUID FK
        gender CHAR
        height FLOAT
        weight FLOAT
        blood_type VARCHAR
        medical_conditions TEXT
        current_medications TEXT
        allergies TEXT
        health_goals TEXT
        activity_level VARCHAR
        email_notifications BOOLEAN
        push_notifications BOOLEAN
        health_reminders BOOLEAN
        created_at DATETIME
        updated_at DATETIME
    }
    
    Role {
        id UUID PK
        name VARCHAR UK
        description TEXT
        permissions JSON
        is_active BOOLEAN
        created_at DATETIME
        updated_at DATETIME
    }
    
    UserRole {
        id UUID PK
        user_id UUID FK
        role_id UUID FK
        assigned_at DATETIME
        assigned_by_id UUID FK
    }
    
    HealthcareProvider {
        id UUID PK
        first_name VARCHAR
        last_name VARCHAR
        email VARCHAR UK
        phone_number VARCHAR
        specialization VARCHAR
        license_number VARCHAR UK
        hospital_clinic VARCHAR
        address TEXT
        bio TEXT
        years_of_experience INTEGER
        consultation_fee DECIMAL
        is_active BOOLEAN
        created_at DATETIME
        updated_at DATETIME
    }
    
    Hospital {
        id UUID PK
        name VARCHAR UK
        hospital_type VARCHAR
        address TEXT
        city VARCHAR
        region VARCHAR
        country VARCHAR
        phone_number VARCHAR
        email VARCHAR
        website URL
        description TEXT
        specialties TEXT
        facilities TEXT
        established_year INTEGER
        bed_capacity INTEGER
        emergency_services BOOLEAN
        appointment_booking_available BOOLEAN
        is_active BOOLEAN
        created_at DATETIME
        updated_at DATETIME
    }
    
    Appointment {
        id UUID PK
        patient_id UUID FK
        healthcare_provider_id UUID FK
        appointment_date DATETIME
        duration_minutes INTEGER
        appointment_type VARCHAR
        status VARCHAR
        priority VARCHAR
        chief_complaint TEXT
        symptoms TEXT
        notes TEXT
        diagnosis TEXT
        treatment_plan TEXT
        prescribed_medications TEXT
        follow_up_instructions TEXT
        next_appointment_recommended BOOLEAN
        consultation_fee DECIMAL
        payment_status VARCHAR
        reminder_sent BOOLEAN
        reminder_sent_at DATETIME
        created_at DATETIME
        updated_at DATETIME
        created_by_id UUID FK
    }
    
    AppointmentFile {
        id UUID PK
        appointment_id UUID FK
        file FileField
        file_name VARCHAR
        file_type VARCHAR
        file_size INTEGER
        description TEXT
        uploaded_by_id UUID FK
        created_at DATETIME
    }
    
    AppointmentRating {
        id UUID PK
        appointment_id UUID FK
        rating INTEGER
        feedback TEXT
        would_recommend BOOLEAN
        punctuality_rating INTEGER
        communication_rating INTEGER
        created_at DATETIME
    }
    
    HealthMetric {
        id UUID PK
        user_id UUID FK
        metric_type VARCHAR
        value FLOAT
        unit VARCHAR
        systolic_value FLOAT
        diastolic_value FLOAT
        recorded_at DATETIME
        is_manual_entry BOOLEAN
        device_id UUID FK
        notes TEXT
        created_at DATETIME
        updated_at DATETIME
    }
    
    IoTDevice {
        id UUID PK
        device_id UUID UK
        name VARCHAR
        device_type VARCHAR
        manufacturer VARCHAR
        model VARCHAR
        firmware_version VARCHAR
        owner_id UUID FK
        status VARCHAR
        is_verified BOOLEAN
        last_seen DATETIME
        api_key VARCHAR
        created_at DATETIME
        updated_at DATETIME
    }
    
    Medication {
        id UUID PK
        name VARCHAR
        generic_name VARCHAR
        brand_name VARCHAR
        category_id UUID FK
        form VARCHAR
        strength VARCHAR
        manufacturer VARCHAR
        description TEXT
        side_effects TEXT
        contraindications TEXT
        interactions TEXT
        storage_instructions TEXT
        requires_prescription BOOLEAN
        is_active BOOLEAN
        created_at DATETIME
        updated_at DATETIME
    }
    
    MedicationCategory {
        id UUID PK
        name VARCHAR UK
        description TEXT
        created_at DATETIME
    }
    
    UserMedication {
        id UUID PK
        user_id UUID FK
        medication_id UUID FK
        prescribed_by_id UUID FK
        dosage VARCHAR
        frequency VARCHAR
        start_date DATE
        end_date DATE
        status VARCHAR
        instructions TEXT
        side_effects_experienced TEXT
        created_at DATETIME
        updated_at DATETIME
    }
    
    Conversation {
        id UUID PK
        user_id UUID FK
        title VARCHAR
        created_at DATETIME
        updated_at DATETIME
        is_active BOOLEAN
    }
    
    Message {
        id UUID PK
        conversation_id UUID FK
        sender VARCHAR
        content TEXT
        timestamp DATETIME
        ai_model VARCHAR
        response_time_ms INTEGER
        tokens_used INTEGER
    }
    
    ConversationAnalytics {
        id UUID PK
        conversation_id UUID FK
        total_messages INTEGER
        total_user_messages INTEGER
        total_bot_messages INTEGER
        total_tokens_used INTEGER
        average_response_time_ms FLOAT
        health_topics JSON
        created_at DATETIME
        updated_at DATETIME
    }
    
    %% Relationships
    User ||--o| UserProfile : has
    User ||--o{ UserRole : has
    Role ||--o{ UserRole : assigned
    User ||--o{ Appointment : books
    User ||--o{ HealthMetric : records
    User ||--o{ IoTDevice : owns
    User ||--o{ UserMedication : takes
    User ||--o{ Conversation : participates
    User ||--o{ AppointmentFile : uploads
    
    HealthcareProvider ||--o{ Appointment : provides
    HealthcareProvider }o--o{ Hospital : works_at
    
    Hospital ||--o{ Appointment : hosts
    
    Appointment ||--o{ AppointmentFile : contains
    Appointment ||--o| AppointmentRating : rated
    
    IoTDevice ||--o{ HealthMetric : generates
    
    MedicationCategory ||--o{ Medication : categorizes
    Medication ||--o{ UserMedication : prescribed
    HealthcareProvider ||--o{ UserMedication : prescribes
    
    Conversation ||--o{ Message : contains
    Conversation ||--o| ConversationAnalytics : analyzed
```

---

## Class Diagram - Core Models

```mermaid
classDiagram
    class User {
        +UUID id
        +String username
        +String email
        +String first_name
        +String last_name
        +String phone_number
        +Date date_of_birth
        +ImageField profile_image
        +String emergency_contact_name
        +String emergency_contact_phone
        +Boolean is_email_verified
        +Boolean is_phone_verified
        +DateTime created_at
        +DateTime updated_at
        +full_name() String
        +save()
    }
    
    class UserProfile {
        +UUID id
        +String gender
        +Float height
        +Float weight
        +String blood_type
        +Text medical_conditions
        +Text current_medications
        +Text allergies
        +Text health_goals
        +String activity_level
        +Boolean email_notifications
        +Boolean push_notifications
        +Boolean health_reminders
        +bmi() Float
    }
    
    class HealthcareProvider {
        +UUID id
        +String first_name
        +String last_name
        +String email
        +String phone_number
        +String specialization
        +String license_number
        +String address
        +Text bio
        +Integer years_of_experience
        +Decimal consultation_fee
        +Boolean is_active
        +full_name() String
        +hospital_names() String
        +primary_hospital() Hospital
        +get_hospitals_in_city(city) QuerySet
    }
    
    class Hospital {
        +UUID id
        +String name
        +String hospital_type
        +String address
        +String city
        +String region
        +String country
        +String phone_number
        +String email
        +String website
        +Text description
        +Text specialties
        +Text facilities
        +Integer established_year
        +Integer bed_capacity
        +Boolean emergency_services
        +Boolean appointment_booking_available
        +Boolean is_active
        +full_address() String
        +specialties_list() List
    }
    
    class Appointment {
        +UUID id
        +DateTime appointment_date
        +Integer duration_minutes
        +String appointment_type
        +String status
        +String priority
        +Text chief_complaint
        +Text symptoms
        +Text notes
        +Text diagnosis
        +Text treatment_plan
        +Text prescribed_medications
        +Text follow_up_instructions
        +Boolean next_appointment_recommended
        +Decimal consultation_fee
        +String payment_status
        +Boolean reminder_sent
        +DateTime reminder_sent_at
        +end_time() DateTime
        +is_past() Boolean
        +is_today() Boolean
        +is_upcoming() Boolean
        +can_be_cancelled() Boolean
        +can_be_rescheduled() Boolean
    }
    
    class HealthMetric {
        +UUID id
        +String metric_type
        +Float value
        +String unit
        +Float systolic_value
        +Float diastolic_value
        +DateTime recorded_at
        +Boolean is_manual_entry
        +Text notes
    }
    
    class IoTDevice {
        +UUID device_id
        +String name
        +String device_type
        +String manufacturer
        +String model
        +String firmware_version
        +String status
        +Boolean is_verified
        +DateTime last_seen
        +String api_key
        +generate_api_key() String
        +update_last_seen()
        +is_online() Boolean
    }
    
    class Conversation {
        +UUID id
        +String title
        +DateTime created_at
        +DateTime updated_at
        +Boolean is_active
        +save()
    }
    
    class Message {
        +UUID id
        +String sender
        +Text content
        +DateTime timestamp
        +String ai_model
        +Integer response_time_ms
        +Integer tokens_used
        +save()
    }
    
    %% Relationships
    User ||--|| UserProfile : profile
    User ||--o{ Appointment : patient
    User ||--o{ HealthMetric : metrics
    User ||--o{ IoTDevice : devices
    User ||--o{ Conversation : conversations
    
    HealthcareProvider ||--o{ Appointment : provider
    HealthcareProvider }o--o{ Hospital : hospitals
    
    Hospital ||--o{ Appointment : location
    
    IoTDevice ||--o{ HealthMetric : device
    
    Conversation ||--o{ Message : messages
```

---

## Authentication Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant Client
    participant AuthAPI
    participant Database
    participant JWTService
    participant EmailService

    Note over Client, EmailService: User Registration Flow
    
    Client->>AuthAPI: POST /api/auth/register/
    AuthAPI->>AuthAPI: Validate input data
    AuthAPI->>Database: Check if email exists
    Database-->>AuthAPI: Email availability
    
    alt Email available
        AuthAPI->>Database: Create User record
        AuthAPI->>Database: Create UserProfile record
        AuthAPI->>Database: Assign default Role
        AuthAPI->>JWTService: Generate JWT tokens
        JWTService-->>AuthAPI: Access & Refresh tokens
        AuthAPI->>EmailService: Send verification email
        AuthAPI-->>Client: 201 Created with tokens & user data
    else Email exists
        AuthAPI-->>Client: 400 Bad Request (Email exists)
    end

    Note over Client, EmailService: User Login Flow
    
    Client->>AuthAPI: POST /api/auth/login/
    AuthAPI->>AuthAPI: Validate credentials
    AuthAPI->>Database: Authenticate user
    Database-->>AuthAPI: User object
    
    alt Valid credentials
        AuthAPI->>JWTService: Generate JWT tokens
        JWTService-->>AuthAPI: Access & Refresh tokens
        AuthAPI->>Database: Update last_login
        AuthAPI-->>Client: 200 OK with tokens & user data
    else Invalid credentials
        AuthAPI-->>Client: 401 Unauthorized
    end

    Note over Client, EmailService: Protected Resource Access
    
    Client->>AuthAPI: GET /api/auth/profile/ (with JWT)
    AuthAPI->>JWTService: Validate JWT token
    
    alt Valid token
        JWTService-->>AuthAPI: User ID from token
        AuthAPI->>Database: Fetch user profile
        Database-->>AuthAPI: User & Profile data
        AuthAPI-->>Client: 200 OK with profile data
    else Invalid/Expired token
        AuthAPI-->>Client: 401 Unauthorized
    end

    Note over Client, EmailService: Token Refresh Flow
    
    Client->>AuthAPI: POST /api/auth/token/refresh/
    AuthAPI->>JWTService: Validate refresh token
    
    alt Valid refresh token
        JWTService-->>AuthAPI: New access token
        AuthAPI-->>Client: 200 OK with new access token
    else Invalid refresh token
        AuthAPI-->>Client: 401 Unauthorized (Re-login required)
    end
```

---

## Appointment Booking Sequence Diagram

```mermaid
sequenceDiagram
    participant Patient as Patient (Mobile)
    participant API as Appointments API
    participant ProviderAPI as Provider API
    participant Database
    participant NotificationService
    participant PaymentService

    Note over Patient, PaymentService: Appointment Booking Flow

    Patient->>API: GET /api/providers/?specialization=cardiology
    API->>Database: Query available providers
    Database-->>API: List of providers
    API-->>Patient: 200 OK with providers list

    Patient->>API: GET /api/providers/{id}/availability/
    API->>Database: Check provider schedule
    Database-->>API: Available time slots
    API-->>Patient: 200 OK with available slots

    Patient->>API: POST /api/appointments/
    Note right of Patient: {<br/>healthcare_provider_id,<br/>appointment_date,<br/>chief_complaint,<br/>appointment_type<br/>}
    
    API->>API: Validate appointment data
    API->>Database: Check provider availability
    Database-->>API: Availability confirmed
    
    alt Time slot available
        API->>Database: Create appointment record
        API->>Database: Update provider schedule
        
        par Notification flows
            API->>NotificationService: Send confirmation to patient
            NotificationService-->>Patient: SMS/Email confirmation
        and
            API->>NotificationService: Notify healthcare provider
            NotificationService-->>ProviderAPI: Provider notification
        end
        
        API-->>Patient: 201 Created with appointment details
        
        Note over Patient, PaymentService: Optional Payment Processing
        
        alt Requires upfront payment
            Patient->>PaymentService: Process consultation fee
            PaymentService-->>API: Payment confirmation
            API->>Database: Update payment_status
        end
        
    else Time slot unavailable
        API-->>Patient: 409 Conflict (Slot no longer available)
    end

    Note over Patient, PaymentService: Appointment Management

    Patient->>API: PUT /api/appointments/{id}/
    API->>Database: Check if can be modified
    
    alt Can be modified
        API->>Database: Update appointment
        API->>NotificationService: Send update notifications
        API-->>Patient: 200 OK with updated details
    else Cannot be modified
        API-->>Patient: 400 Bad Request (Cannot modify)
    end

    Patient->>API: DELETE /api/appointments/{id}/
    API->>Database: Check cancellation policy
    
    alt Can be cancelled
        API->>Database: Update status to 'cancelled'
        API->>NotificationService: Send cancellation notifications
        API->>PaymentService: Process refund if applicable
        API-->>Patient: 200 OK (Appointment cancelled)
    else Cannot be cancelled
        API-->>Patient: 400 Bad Request (Cannot cancel)
    end
```

---

## Dr. Jeg AI Chat Sequence Diagram

```mermaid
sequenceDiagram
    participant User as User (Mobile)
    participant ChatAPI as Dr. Jeg API
    participant Database
    participant GeminiService as Gemini AI Service
    participant HealthMetrics as Health Metrics API
    participant Analytics as Analytics Service

    Note over User, Analytics: AI Chat Conversation Flow

    User->>ChatAPI: POST /api/dr-jeg/conversations/
    ChatAPI->>Database: Create new conversation
    Database-->>ChatAPI: Conversation ID
    ChatAPI-->>User: 201 Created with conversation ID

    User->>ChatAPI: POST /api/dr-jeg/conversations/{id}/chat/
    Note right of User: {<br/>message: "I have been feeling tired lately"<br/>}
    
    ChatAPI->>Database: Save user message
    ChatAPI->>HealthMetrics: GET user's recent health data
    HealthMetrics-->>ChatAPI: Recent metrics & medical history
    
    ChatAPI->>GeminiService: Send request with context
    Note right of ChatAPI: {<br/>user_message,<br/>health_context,<br/>conversation_history<br/>}
    
    activate GeminiService
    GeminiService->>GeminiService: Process with medical knowledge
    GeminiService->>GeminiService: Generate health-focused response
    GeminiService-->>ChatAPI: AI response with metadata
    deactivate GeminiService
    
    ChatAPI->>Database: Save AI response
    ChatAPI->>Analytics: Update conversation analytics
    
    ChatAPI-->>User: 200 OK with AI response
    Note left of ChatAPI: {<br/>response: "Based on your symptoms...",<br/>recommendations: [...],<br/>follow_up_questions: [...]<br/>}

    Note over User, Analytics: Health Analysis Request

    User->>ChatAPI: POST /api/dr-jeg/health-analysis/
    Note right of User: {<br/>symptoms: ["fatigue", "headache"],<br/>duration: "1 week"<br/>}
    
    ChatAPI->>HealthMetrics: GET comprehensive health data
    HealthMetrics-->>ChatAPI: Complete health profile
    
    ChatAPI->>GeminiService: Request detailed health analysis
    Note right of ChatAPI: {<br/>symptoms,<br/>health_history,<br/>current_medications,<br/>recent_metrics<br/>}
    
    activate GeminiService
    GeminiService->>GeminiService: Comprehensive health analysis
    GeminiService->>GeminiService: Generate recommendations
    GeminiService-->>ChatAPI: Detailed analysis response
    deactivate GeminiService
    
    ChatAPI->>Database: Save analysis conversation
    ChatAPI->>Analytics: Record health topic analytics
    
    ChatAPI-->>User: 200 OK with health analysis
    Note left of ChatAPI: {<br/>analysis: "...",<br/>risk_factors: [...],<br/>recommendations: [...],<br/>when_to_see_doctor: "..."<br/>}

    Note over User, Analytics: Conversation History

    User->>ChatAPI: GET /api/dr-jeg/conversations/
    ChatAPI->>Database: Fetch user conversations
    Database-->>ChatAPI: Conversation list with summaries
    ChatAPI-->>User: 200 OK with conversation history

    User->>ChatAPI: GET /api/dr-jeg/conversations/{id}/
    ChatAPI->>Database: Fetch conversation details
    Database-->>ChatAPI: Full conversation with messages
    ChatAPI-->>User: 200 OK with conversation details
```

---

## Health Metrics Recording Sequence Diagram

```mermaid
sequenceDiagram
    participant Device as IoT Device
    participant User as User (Mobile)
    participant MetricsAPI as Health Metrics API
    participant Database
    participant IoTAPI as IoT Device API
    participant NotificationService
    participant AnalyticsService

    Note over Device, AnalyticsService: Automatic IoT Data Recording

    Device->>IoTAPI: POST /api/iot/data/ (with API key)
    Note right of Device: {<br/>device_id,<br/>metric_type: "blood_pressure",<br/>systolic: 120,<br/>diastolic: 80,<br/>timestamp<br/>}
    
    IoTAPI->>Database: Validate device & API key
    Database-->>IoTAPI: Device validation result
    
    alt Valid device
        IoTAPI->>Database: Update device last_seen
        IoTAPI->>MetricsAPI: Forward health data
        MetricsAPI->>Database: Store health metric
        
        MetricsAPI->>AnalyticsService: Analyze new reading
        AnalyticsService->>AnalyticsService: Check for anomalies
        
        alt Abnormal reading detected
            AnalyticsService->>NotificationService: Send health alert
            NotificationService-->>User: Emergency notification
        end
        
        MetricsAPI-->>IoTAPI: 201 Created
        IoTAPI-->>Device: 200 OK (Data received)
    else Invalid device
        IoTAPI-->>Device: 401 Unauthorized
    end

    Note over Device, AnalyticsService: Manual Data Entry

    User->>MetricsAPI: POST /api/health-metrics/
    Note right of User: {<br/>metric_type: "weight",<br/>value: 70.5,<br/>unit: "kg",<br/>recorded_at: "2024-01-15T09:00:00Z"<br/>}
    
    MetricsAPI->>MetricsAPI: Validate metric data
    MetricsAPI->>Database: Store health metric
    
    MetricsAPI->>AnalyticsService: Process new metric
    AnalyticsService->>Database: Calculate trends & insights
    
    alt Milestone achieved
        AnalyticsService->>NotificationService: Send congratulations
        NotificationService-->>User: Achievement notification
    end
    
    MetricsAPI-->>User: 201 Created with metric data

    Note over Device, AnalyticsService: Health Dashboard Data

    User->>MetricsAPI: GET /api/health-metrics/dashboard/
    MetricsAPI->>Database: Fetch recent metrics
    MetricsAPI->>AnalyticsService: Get trends & insights
    
    par Data aggregation
        Database-->>MetricsAPI: Recent readings
    and
        AnalyticsService-->>MetricsAPI: Trends & analytics
    end
    
    MetricsAPI->>MetricsAPI: Combine data for dashboard
    MetricsAPI-->>User: 200 OK with dashboard data
    Note left of MetricsAPI: {<br/>recent_metrics: [...],<br/>trends: {...},<br/>insights: [...],<br/>recommendations: [...]<br/>}

    Note over Device, AnalyticsService: Health Reports

    User->>MetricsAPI: GET /api/health-metrics/report/?period=monthly
    MetricsAPI->>Database: Query metrics for period
    MetricsAPI->>AnalyticsService: Generate report analytics
    
    par Report generation
        Database-->>MetricsAPI: Historical data
    and
        AnalyticsService-->>MetricsAPI: Statistical analysis
    end
    
    MetricsAPI->>MetricsAPI: Generate comprehensive report
    MetricsAPI-->>User: 200 OK with health report
    Note left of MetricsAPI: {<br/>summary: {...},<br/>metrics_chart_data: [...],<br/>improvements: [...],<br/>recommendations: [...]<br/>}
```

---

## Provider Management Flow

```mermaid
sequenceDiagram
    participant Admin as Admin User
    participant ProviderAPI as Provider API
    participant Database
    participant Hospital as Hospital System
    participant NotificationService
    participant VerificationService

    Note over Admin, VerificationService: Provider Registration

    Admin->>ProviderAPI: POST /api/providers/
    Note right of Admin: {<br/>first_name, last_name,<br/>email, specialization,<br/>license_number,<br/>hospital_ids: [...]<br/>}
    
    ProviderAPI->>VerificationService: Verify license number
    VerificationService-->>ProviderAPI: License validation result
    
    alt Valid license
        ProviderAPI->>Database: Create provider record
        ProviderAPI->>Database: Associate with hospitals
        
        ProviderAPI->>NotificationService: Send welcome email
        NotificationService-->>ProviderAPI: Provider welcome notification
        
        ProviderAPI-->>Admin: 201 Created with provider details
    else Invalid license
        ProviderAPI-->>Admin: 400 Bad Request (Invalid license)
    end

    Note over Admin, VerificationService: Provider-Hospital Management

    Admin->>ProviderAPI: PUT /api/providers/{id}/hospitals/
    Note right of Admin: {<br/>hospital_ids: [uuid1, uuid2]<br/>}
    
    ProviderAPI->>Database: Update provider-hospital relationships
    ProviderAPI->>Hospital: Sync provider data
    Hospital-->>ProviderAPI: Confirmation
    
    ProviderAPI-->>Admin: 200 OK with updated associations

    Note over Admin, VerificationService: Provider Schedule Management

    Admin->>ProviderAPI: GET /api/providers/{id}/schedule/
    ProviderAPI->>Database: Fetch provider schedule
    Database-->>ProviderAPI: Schedule data
    ProviderAPI-->>Admin: 200 OK with schedule

    Admin->>ProviderAPI: POST /api/providers/{id}/availability/
    Note right of Admin: {<br/>date: "2024-01-15",<br/>start_time: "09:00",<br/>end_time: "17:00",<br/>hospital_id: uuid<br/>}
    
    ProviderAPI->>Database: Update availability
    ProviderAPI->>NotificationService: Notify existing patients
    
    ProviderAPI-->>Admin: 201 Created (Availability set)

    Note over Admin, VerificationService: Provider Performance Analytics

    Admin->>ProviderAPI: GET /api/providers/{id}/analytics/
    ProviderAPI->>Database: Aggregate appointment data
    ProviderAPI->>Database: Calculate performance metrics
    
    par Analytics calculation
        Database-->>ProviderAPI: Appointment statistics
    and
        Database-->>ProviderAPI: Patient ratings
    and
        Database-->>ProviderAPI: Revenue data
    end
    
    ProviderAPI->>ProviderAPI: Generate analytics report
    ProviderAPI-->>Admin: 200 OK with analytics
    Note left of ProviderAPI: {<br/>total_appointments,<br/>average_rating,<br/>revenue,<br/>patient_satisfaction,<br/>monthly_trends<br/>}
```

---

## IoT Device Integration Flow

```mermaid
sequenceDiagram
    participant Device as IoT Device
    participant User as User (Mobile)
    participant IoTAPI as IoT Device API
    participant Database
    participant MetricsAPI as Health Metrics API
    participant NotificationService
    participant SecurityService

    Note over Device, SecurityService: Device Registration

    User->>IoTAPI: POST /api/iot/devices/register/
    Note right of User: {<br/>device_type: "SMARTWATCH",<br/>manufacturer: "Apple",<br/>model: "Watch Series 9"<br/>}
    
    IoTAPI->>SecurityService: Generate device API key
    SecurityService-->>IoTAPI: Unique API key
    
    IoTAPI->>Database: Create device record
    IoTAPI-->>User: 201 Created with device_id & API key
    
    User->>Device: Configure device with API key
    Device->>IoTAPI: POST /api/iot/devices/verify/
    Note right of Device: {<br/>device_id,<br/>api_key<br/>}
    
    IoTAPI->>Database: Verify device credentials
    Database-->>IoTAPI: Verification result
    
    alt Valid credentials
        IoTAPI->>Database: Mark device as verified
        IoTAPI-->>Device: 200 OK (Device verified)
        Device->>User: Device setup complete
    else Invalid credentials
        IoTAPI-->>Device: 401 Unauthorized
    end

    Note over Device, SecurityService: Continuous Data Streaming

    loop Every measurement
        Device->>Device: Take health measurement
        Device->>IoTAPI: POST /api/iot/data/stream/
        Note right of Device: {<br/>device_id,<br/>api_key,<br/>metrics: [{<br/>  type: "heart_rate",<br/>  value: 75,<br/>  timestamp: "..."<br/>}]<br/>}
        
        IoTAPI->>SecurityService: Validate API key
        SecurityService-->>IoTAPI: Authentication result
        
        alt Valid authentication
            IoTAPI->>Database: Update device last_seen
            IoTAPI->>MetricsAPI: Forward health data
            MetricsAPI->>Database: Store health metrics
            
            MetricsAPI->>MetricsAPI: Analyze for anomalies
            
            alt Anomaly detected
                MetricsAPI->>NotificationService: Send health alert
                NotificationService-->>User: Immediate health notification
            end
            
            IoTAPI-->>Device: 200 OK (Data received)
        else Invalid authentication
            IoTAPI-->>Device: 401 Unauthorized
        end
    end

    Note over Device, SecurityService: Device Status & Health

    User->>IoTAPI: GET /api/iot/devices/
    IoTAPI->>Database: Fetch user's devices
    Database-->>IoTAPI: Device list with status
    IoTAPI-->>User: 200 OK with devices
    Note left of IoTAPI: [{<br/>  device_id,<br/>  name,<br/>  status: "ACTIVE",<br/>  last_seen,<br/>  battery_level<br/>}]

    User->>IoTAPI: GET /api/iot/devices/{id}/health/
    IoTAPI->>Database: Check device diagnostics
    IoTAPI->>MetricsAPI: Get recent data quality
    
    par Device health check
        Database-->>IoTAPI: Device status info
    and
        MetricsAPI-->>IoTAPI: Data quality metrics
    end
    
    IoTAPI-->>User: 200 OK with device health
    Note left of IoTAPI: {<br/>  status: "ACTIVE",<br/>  connectivity: "GOOD",<br/>  data_quality: "HIGH",<br/>  last_maintenance,<br/>  issues: []<br/>}

    Note over Device, SecurityService: Device Maintenance

    alt Device malfunction
        Device->>IoTAPI: POST /api/iot/devices/error/
        Note right of Device: {<br/>error_code: "SENSOR_FAIL",<br/>timestamp<br/>}
        
        IoTAPI->>Database: Log device error
        IoTAPI->>NotificationService: Alert user about device issue
        NotificationService-->>User: Device maintenance required
        
        IoTAPI-->>Device: 200 OK (Error logged)
    end

    User->>IoTAPI: PUT /api/iot/devices/{id}/
    Note right of User: {<br/>name: "Updated Device Name"<br/>}
    
    IoTAPI->>Database: Update device settings
    IoTAPI-->>User: 200 OK (Device updated)
```

---

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Applications"
        MobileApp[Mobile App<br/>React Native]
        WebApp[Web Dashboard<br/>React]
        AdminPanel[Admin Panel<br/>Django Admin]
    end

    subgraph "API Gateway Layer"
        NGINX[NGINX<br/>Load Balancer]
        CORS[CORS Middleware]
        Auth[JWT Authentication]
        RateLimit[Rate Limiting]
    end

    subgraph "Django Backend Services"
        AccountsApp[Accounts App<br/>User Management]
        ProvidersApp[Providers App<br/>Healthcare Providers]
        AppointmentsApp[Appointments App<br/>Booking System]
        HealthMetricsApp[Health Metrics App<br/>Health Data]
        DrJegApp[Dr. Jeg App<br/>AI Chat Service]
        IoTApp[IoT Devices App<br/>Device Management]
        MedicationsApp[Medications App<br/>Prescription Management]
        HospitalsApp[Hospitals App<br/>Hospital Management]
    end

    subgraph "External Services"
        GeminiAI[Google Gemini AI<br/>Medical Assistant]
        EmailService[Email Service<br/>SendGrid/SMTP]
        SMSService[SMS Service<br/>Twilio]
        PaymentGateway[Payment Gateway<br/>Stripe/PayPal]
        CloudStorage[Cloud Storage<br/>AWS S3/GCS]
    end

    subgraph "Database Layer"
        PostgreSQL[(PostgreSQL<br/>Primary Database)]
        Redis[(Redis<br/>Cache & Sessions)]
        FileStorage[(File Storage<br/>Media Files)]
    end

    subgraph "IoT Integration"
        IoTDevices[IoT Health Devices<br/>Smartwatches, Monitors]
        DeviceAPI[Device API Gateway<br/>MQTT/HTTP]
    end

    subgraph "Background Services"
        Celery[Celery<br/>Task Queue]
        CeleryBeat[Celery Beat<br/>Scheduled Tasks]
        NotificationWorker[Notification Worker<br/>Email/SMS Queue]
    end

    %% Client to API connections
    MobileApp --> NGINX
    WebApp --> NGINX
    AdminPanel --> NGINX

    %% API Gateway to services
    NGINX --> CORS
    CORS --> Auth
    Auth --> RateLimit
    RateLimit --> AccountsApp
    RateLimit --> ProvidersApp
    RateLimit --> AppointmentsApp
    RateLimit --> HealthMetricsApp
    RateLimit --> DrJegApp
    RateLimit --> IoTApp
    RateLimit --> MedicationsApp
    RateLimit --> HospitalsApp

    %% Service to external connections
    DrJegApp --> GeminiAI
    AccountsApp --> EmailService
    AppointmentsApp --> SMSService
    AppointmentsApp --> PaymentGateway
    AccountsApp --> CloudStorage

    %% Database connections
    AccountsApp --> PostgreSQL
    ProvidersApp --> PostgreSQL
    AppointmentsApp --> PostgreSQL
    HealthMetricsApp --> PostgreSQL
    DrJegApp --> PostgreSQL
    IoTApp --> PostgreSQL
    MedicationsApp --> PostgreSQL
    HospitalsApp --> PostgreSQL

    %% Cache connections
    AccountsApp --> Redis
    DrJegApp --> Redis
    HealthMetricsApp --> Redis

    %% File storage
    AccountsApp --> FileStorage
    AppointmentsApp --> FileStorage

    %% IoT connections
    IoTDevices --> DeviceAPI
    DeviceAPI --> IoTApp
    IoTApp --> HealthMetricsApp

    %% Background services
    AccountsApp --> Celery
    AppointmentsApp --> Celery
    DrJegApp --> Celery
    Celery --> NotificationWorker
    CeleryBeat --> NotificationWorker
    NotificationWorker --> EmailService
    NotificationWorker --> SMSService

    %% Styling
    classDef clientApp fill:#e1f5fe
    classDef apiService fill:#f3e5f5
    classDef database fill:#e8f5e8
    classDef external fill:#fff3e0
    classDef background fill:#fce4ec

    class MobileApp,WebApp,AdminPanel clientApp
    class AccountsApp,ProvidersApp,AppointmentsApp,HealthMetricsApp,DrJegApp,IoTApp,MedicationsApp,HospitalsApp apiService
    class PostgreSQL,Redis,FileStorage database
    class GeminiAI,EmailService,SMSService,PaymentGateway,CloudStorage external
    class Celery,CeleryBeat,NotificationWorker background
```

---

## API Interaction Flow

```mermaid
flowchart TD
    Start([User Opens App]) --> Auth{Authenticated?}
    
    Auth -->|No| Login[Login/Register Flow]
    Auth -->|Yes| Dashboard[Load Dashboard]
    
    Login --> LoginAPI[POST /api/auth/login/]
    LoginAPI --> TokenReceived{Token Received?}
    TokenReceived -->|Yes| Dashboard
    TokenReceived -->|No| LoginError[Show Error]
    
    Dashboard --> LoadProfile[GET /api/auth/profile/]
    Dashboard --> LoadMetrics[GET /api/health-metrics/]
    Dashboard --> LoadAppointments[GET /api/appointments/]
    
    LoadProfile --> ProfileLoaded[Profile Data Loaded]
    LoadMetrics --> MetricsLoaded[Health Data Loaded]
    LoadAppointments --> AppointmentsLoaded[Appointments Loaded]
    
    ProfileLoaded --> UserActions{User Action}
    MetricsLoaded --> UserActions
    AppointmentsLoaded --> UserActions
    
    UserActions -->|Update Profile| UpdateProfileAPI[PUT /api/auth/profile/]
    UserActions -->|Add Health Data| AddMetricAPI[POST /api/health-metrics/]
    UserActions -->|Book Appointment| BookAppointmentAPI[POST /api/appointments/]
    UserActions -->|Chat with Dr. Jeg| ChatAPI[POST /api/dr-jeg/chat/]
    UserActions -->|Manage IoT Device| IoTAPI[POST /api/iot/devices/]
    
    UpdateProfileAPI --> Success[Success Response]
    AddMetricAPI --> Success
    BookAppointmentAPI --> AppointmentCreated[Appointment Created]
    ChatAPI --> AIResponse[AI Response Received]
    IoTAPI --> DeviceManaged[Device Configured]
    
    AppointmentCreated --> NotificationSent[Notification Sent]
    Success --> Dashboard
    AIResponse --> Dashboard
    DeviceManaged --> Dashboard
    NotificationSent --> Dashboard
    
    LoginError --> Login
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Load Balancer"
            LB[NGINX Load Balancer<br/>SSL Termination]
        end
        
        subgraph "Application Servers"
            App1[Django App Server 1<br/>Gunicorn + Django]
            App2[Django App Server 2<br/>Gunicorn + Django]
            App3[Django App Server 3<br/>Gunicorn + Django]
        end
        
        subgraph "Database Cluster"
            DBMaster[(PostgreSQL Master<br/>Read/Write)]
            DBSlave1[(PostgreSQL Slave 1<br/>Read Only)]
            DBSlave2[(PostgreSQL Slave 2<br/>Read Only)]
        end
        
        subgraph "Cache & Session Store"
            RedisCluster[(Redis Cluster<br/>Cache + Sessions)]
        end
        
        subgraph "Background Processing"
            CeleryWorker1[Celery Worker 1<br/>Background Tasks]
            CeleryWorker2[Celery Worker 2<br/>Background Tasks]
            CeleryBeat[Celery Beat<br/>Scheduler]
            RedisBroker[(Redis Broker<br/>Task Queue)]
        end
        
        subgraph "File Storage"
            S3[AWS S3<br/>Static Files & Media]
            CDN[CloudFront CDN<br/>Global Distribution]
        end
        
        subgraph "Monitoring & Logging"
            Prometheus[Prometheus<br/>Metrics Collection]
            Grafana[Grafana<br/>Dashboards]
            ELK[ELK Stack<br/>Centralized Logging]
        end
    end
    
    subgraph "External Services"
        GeminiAPI[Google Gemini AI]
        SendGrid[SendGrid Email]
        Twilio[Twilio SMS]
        Stripe[Stripe Payments]
    end
    
    Internet([Internet]) --> LB
    LB --> App1
    LB --> App2
    LB --> App3
    
    App1 --> DBMaster
    App1 --> DBSlave1
    App2 --> DBMaster
    App2 --> DBSlave2
    App3 --> DBMaster
    App3 --> DBSlave1
    
    App1 --> RedisCluster
    App2 --> RedisCluster
    App3 --> RedisCluster
    
    App1 --> RedisBroker
    App2 --> RedisBroker
    App3 --> RedisBroker
    
    RedisBroker --> CeleryWorker1
    RedisBroker --> CeleryWorker2
    CeleryBeat --> RedisBroker
    
    App1 --> S3
    App2 --> S3
    App3 --> S3
    S3 --> CDN
    
    App1 --> GeminiAPI
    App1 --> SendGrid
    App1 --> Twilio
    App1 --> Stripe
    
    App1 --> Prometheus
    App2 --> Prometheus
    App3 --> Prometheus
    Prometheus --> Grafana
    
    App1 --> ELK
    App2 --> ELK
    App3 --> ELK
    
    DBMaster --> DBSlave1
    DBMaster --> DBSlave2
    
    classDef server fill:#e3f2fd
    classDef database fill:#e8f5e8
    classDef external fill:#fff3e0
    classDef monitoring fill:#fce4ec
    
    class App1,App2,App3,LB server
    class DBMaster,DBSlave1,DBSlave2,RedisCluster,RedisBroker database
    class GeminiAPI,SendGrid,Twilio,Stripe external
    class Prometheus,Grafana,ELK monitoring
```

---

## Notes

### Model Relationships Summary:
- **User**: Central entity with one-to-one profile and many roles
- **HealthcareProvider**: Many-to-many with hospitals, one-to-many with appointments
- **Appointment**: Links patients (users) with providers, includes files and ratings
- **HealthMetric**: Tracks user health data, can be linked to IoT devices
- **IoTDevice**: Belongs to users, generates health metrics
- **Conversation**: Dr. Jeg chat sessions with messages and analytics
- **Medication**: Can be prescribed to users through UserMedication

### Key Features Illustrated:
1. **Authentication System**: JWT-based with role management
2. **Healthcare Provider Management**: Multi-hospital affiliations
3. **Appointment System**: Complete booking, modification, and rating workflow
4. **AI Health Assistant**: Dr. Jeg with conversation management
5. **Health Metrics**: Manual entry and IoT device integration
6. **Medication Management**: Prescription and tracking system
7. **IoT Integration**: Device registration and data streaming
8. **Notification System**: Multi-channel communication

### Architecture Patterns:
- **Microservices-like Django Apps**: Each domain has its own app
- **RESTful API Design**: Standard HTTP methods and status codes
- **Event-driven Notifications**: Background task processing
- **Caching Strategy**: Redis for performance optimization
- **Scalable Deployment**: Load-balanced application servers
- **Security**: JWT authentication, API key validation for IoT devices

This documentation provides a comprehensive view of the JEGHealth backend system architecture, suitable for developers, system administrators, and stakeholders to understand the system design and interactions.
