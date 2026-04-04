# Hospital Patient Record Management System - Architecture & Design Guide

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER (React SPA)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Dashboard   │  │   Patients   │  │ Appointments │           │
│  │  Components  │  │  Management  │  │  Scheduling  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Medical Rec │  │   Reports    │  │   Settings   │           │
│  │  & Lab Tests │  │  & Analytics │  │ & User Admin │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    API Gateway (Axios)
                           │
├─────────────────────────────────────────────────────────────────┤
│                  API LAYER (Express.js)                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  REST API Endpoints                                    │    │
│  │  ├─ /api/patients (CRUD operations)                   │    │
│  │  ├─ /api/appointments (Scheduling)                    │    │
│  │  ├─ /api/medical-records (Medical history)            │    │
│  │  ├─ /api/lab-tests (Lab testing)                      │    │
│  │  ├─ /api/reports (Analytics)                          │    │
│  │  ├─ /api/auth (Authentication)                        │    │
│  │  └─ /api/users (User management)                      │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Middleware Layer                                      │    │
│  │  ├─ Authentication (JWT)                              │    │
│  │  ├─ Authorization (RBAC)                              │    │
│  │  ├─ Validation                                        │    │
│  │  ├─ Error Handling                                    │    │
│  │  └─ Logging & Audit Trail                             │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Business Logic Layer (Services)                       │    │
│  │  ├─ PatientService                                    │    │
│  │  ├─ AppointmentService                                │    │
│  │  ├─ MedicalRecordService                              │    │
│  │  ├─ ReportService                                     │    │
│  │  └─ NotificationService                               │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
├─────────────────────────────────────────────────────────────────┤
│              DATA ACCESS LAYER (Mongoose ODM)                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Data Access Objects / Repository Pattern             │    │
│  │  ├─ PatientRepository                                 │    │
│  │  ├─ AppointmentRepository                             │    │
│  │  ├─ MedicalRecordRepository                           │    │
│  │  └─ UserRepository                                    │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
├─────────────────────────────────────────────────────────────────┤
│              DATABASE LAYER (MongoDB)                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Collections:                                          │    │
│  │  ├─ Patients                                          │    │
│  │  ├─ Doctors                                           │    │
│  │  ├─ Appointments                                      │    │
│  │  ├─ Medical Records                                   │    │
│  │  ├─ Lab Tests                                         │    │
│  │  ├─ Users                                             │    │
│  │  ├─ Departments                                       │    │
│  │  └─ Vital Signs                                       │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

├─────────────────────────────────────────────────────────────────┤
│              EXTERNAL SERVICES & INTEGRATIONS                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  File Storage      │  Email Service  │  SMS Service    │    │
│  │  AWS S3 / Local    │  Nodemailer     │  Twilio (opt)   │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Monitoring  │  Analytics  │  Error Tracking          │    │
│  │  DataDog     │  Analytics  │  Sentry                  │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Design

### 1. Patient Collection
```javascript
{
  _id: ObjectId,
  
  // Personal Information
  firstName: String,
  lastName: String,
  email: String,
  phone: String,
  dateOfBirth: Date,
  gender: String, // Male, Female, Other
  bloodGroup: String, // A+, B-, etc.
  
  // Address
  address: {
    street: String,
    city: String,
    state: String,
    pincode: String,
    country: String
  },
  
  // Emergency Contact
  emergencyContact: {
    name: String,
    relationship: String,
    phone: String
  },
  
  // Medical Information
  medicalHistory: [
    {
      condition: String,
      diagnosedDate: Date,
      notes: String
    }
  ],
  allergies: [
    {
      allergen: String,
      severity: String, // Mild, Moderate, Severe
      reaction: String
    }
  ],
  currentMedications: [
    {
      medicineName: String,
      dosage: String,
      frequency: String,
      startDate: Date,
      endDate: Date
    }
  ],
  
  // Insurance Information
  insurance: {
    provider: String,
    policyNumber: String,
    groupId: String,
    coveragePercentage: Number,
    validFrom: Date,
    validTo: Date
  },
  
  // Medical Documents
  documents: [
    {
      _id: ObjectId,
      fileName: String,
      fileType: String, // PDF, JPG, etc.
      fileSize: Number,
      url: String,
      category: String, // X-Ray, Lab Report, etc.
      uploadedDate: Date,
      uploadedBy: ObjectId (ref: User)
    }
  ],
  
  // Status & Metadata
  status: String, // Active, Discharged, Transferred
  admissionDate: Date,
  dischargeDate: Date,
  createdAt: Date,
  updatedAt: Date,
  createdBy: ObjectId (ref: User),
  updatedBy: ObjectId (ref: User)
}
```

### 2. Doctor Collection
```javascript
{
  _id: ObjectId,
  firstName: String,
  lastName: String,
  email: String,
  phone: String,
  specialization: String, // Cardiology, Neurology, etc.
  licenseNumber: String,
  department: ObjectId (ref: Department),
  
  // Availability
  availability: {
    monday: { startTime: String, endTime: String, available: Boolean },
    tuesday: { startTime: String, endTime: String, available: Boolean },
    // ... other days
  },
  
  // Appointment Slots
  appointmentDuration: Number, // in minutes (default 30)
  slotIntervals: Number, // 15, 30, 60 minutes
  
  // Status
  isActive: Boolean,
  joiningDate: Date,
  createdAt: Date,
  updatedAt: Date
}
```

### 3. Appointment Collection
```javascript
{
  _id: ObjectId,
  appointmentNumber: String, // Unique identifier (AP-2024-001)
  
  // References
  patient: ObjectId (ref: Patient),
  doctor: ObjectId (ref: Doctor),
  department: ObjectId (ref: Department),
  
  // Appointment Details
  date: Date,
  startTime: String, // HH:MM format
  endTime: String,
  type: String, // Consultation, Follow-up, Surgery, Lab Test
  status: String, // Scheduled, Completed, Cancelled, No-show
  
  // Purpose & Notes
  purpose: String,
  doctorNotes: String,
  
  // Cancellation Info
  cancellationReason: String,
  cancelledBy: ObjectId (ref: User),
  cancelledAt: Date,
  
  // Metadata
  createdAt: Date,
  updatedAt: Date
}
```

### 4. Medical Record Collection
```javascript
{
  _id: ObjectId,
  patient: ObjectId (ref: Patient),
  doctor: ObjectId (ref: Doctor),
  appointment: ObjectId (ref: Appointment),
  
  // Record Details
  date: Date,
  diagnosis: String,
  symptoms: [String],
  treatment: String,
  doctorNotes: String,
  
  // Vital Signs Recorded
  vitals: {
    heartRate: Number,
    bloodPressure: String, // 120/80
    temperature: Number,
    spo2: Number,
    respiratoryRate: Number
  },
  
  // Prescribed Medicines
  medications: [
    {
      name: String,
      dosage: String,
      frequency: String,
      duration: String,
      notes: String
    }
  ],
  
  // Lab Tests Ordered
  labTests: [ObjectId], // ref: LabTest
  
  // Attachments
  attachments: [
    {
      fileName: String,
      fileType: String,
      url: String,
      uploadedAt: Date
    }
  ],
  
  // Status
  status: String, // Active, Completed
  createdAt: Date,
  updatedAt: Date
}
```

### 5. Lab Test Collection
```javascript
{
  _id: ObjectId,
  testNumber: String, // LT-2024-001
  patient: ObjectId (ref: Patient),
  requestedBy: ObjectId (ref: Doctor),
  
  // Test Details
  testType: String, // Blood Test, X-Ray, CT Scan, etc.
  testName: String,
  urgency: String, // Routine, Urgent
  
  // Test Results
  status: String, // Pending, In Progress, Completed
  resultDate: Date,
  results: {
    // Dynamic based on test type
    // e.g., { hemoglobin: 13.5, hematocrit: 40 }
  },
  referenceRange: {
    // Dynamic based on test type
  },
  normalcy: String, // Normal, Abnormal, Critical
  notes: String,
  labTechnician: ObjectId (ref: User),
  
  // Attachments (images, reports)
  attachments: [
    {
      fileName: String,
      fileType: String,
      url: String
    }
  ],
  
  // Metadata
  orderedDate: Date,
  createdAt: Date,
  updatedAt: Date
}
```

### 6. User Collection
```javascript
{
  _id: ObjectId,
  firstName: String,
  lastName: String,
  email: String (unique),
  phone: String,
  password: String (hashed with bcrypt),
  
  // Role & Permissions
  role: String, // Admin, Doctor, Nurse, Receptionist, Patient
  department: ObjectId (ref: Department),
  permissions: [String], // Granular permissions
  
  // Profile
  profilePicture: String, // URL
  
  // Account Status
  isActive: Boolean,
  lastLogin: Date,
  loginAttempts: Number, // For security
  lockedUntil: Date, // Account lockout timestamp
  
  // Password Management
  passwordChangedAt: Date,
  passwordResetToken: String,
  passwordResetExpires: Date,
  
  // Two Factor Auth (optional)
  twoFactorEnabled: Boolean,
  twoFactorSecret: String,
  
  // Audit Trail
  createdAt: Date,
  updatedAt: Date,
  createdBy: ObjectId (ref: User),
  
  // Activity Log
  activityLog: [
    {
      action: String,
      timestamp: Date,
      ipAddress: String,
      userAgent: String
    }
  ]
}
```

### 7. Department Collection
```javascript
{
  _id: ObjectId,
  name: String, // Cardiology, Neurology, etc.
  description: String,
  head: ObjectId (ref: Doctor),
  
  // Department Details
  floor: String,
  phoneNumber: String,
  email: String,
  
  // Working Hours
  workingHours: {
    startTime: String,
    endTime: String
  },
  
  // Beds Available
  totalBeds: Number,
  availableBeds: Number,
  
  // Status
  isActive: Boolean,
  createdAt: Date,
  updatedAt: Date
}
```

### 8. Vital Signs Collection
```javascript
{
  _id: ObjectId,
  patient: ObjectId (ref: Patient),
  recordedBy: ObjectId (ref: User),
  recordedAt: Date,
  
  // Vital Signs
  heartRate: Number, // bpm
  bloodPressure: String, // Systolic/Diastolic
  temperature: Number, // Celsius
  spo2: Number, // Oxygen saturation %
  respiratoryRate: Number, // breaths per minute
  weight: Number, // kg
  height: Number, // cm
  bmi: Number, // Calculated
  
  // Additional Info
  notes: String,
  createdAt: Date
}
```

---

## API Response Structure

### Standard Success Response
```javascript
{
  success: true,
  message: "Operation completed successfully",
  statusCode: 200,
  data: {
    // Response data
  },
  timestamp: "2024-01-15T10:30:00Z"
}
```

### Standard Error Response
```javascript
{
  success: false,
  message: "Error message describing the issue",
  statusCode: 400, // or 401, 403, 404, 500, etc.
  error: {
    code: "VALIDATION_ERROR",
    details: [
      {
        field: "email",
        message: "Invalid email format"
      }
    ]
  },
  timestamp: "2024-01-15T10:30:00Z"
}
```

### Paginated Response
```javascript
{
  success: true,
  message: "Patients retrieved successfully",
  statusCode: 200,
  data: {
    items: [...], // Array of items
    pagination: {
      currentPage: 1,
      pageSize: 10,
      totalItems: 250,
      totalPages: 25,
      hasNext: true,
      hasPrev: false
    }
  },
  timestamp: "2024-01-15T10:30:00Z"
}
```

---

## User Roles & Permissions Matrix

| Permission | Admin | Doctor | Nurse | Receptionist | Patient |
|-----------|-------|--------|-------|--------------|---------|
| View All Patients | ✅ | ✅* | ✅* | ✅ | ❌ |
| Create Patient | ✅ | ❌ | ❌ | ✅ | ❌ |
| Edit Patient | ✅ | ❌ | ❌ | ✅ | ❌ |
| Delete Patient | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create Medical Record | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Medical Record | ✅ | ✅* | ✅* | ❌ | ✅** |
| Create Lab Test | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Lab Results | ✅ | ✅* | ✅ | ❌ | ✅** |
| Schedule Appointment | ✅ | ✅ | ❌ | ✅ | ✅ |
| View Appointments | ✅ | ✅* | ✅ | ✅ | ✅** |
| Record Vital Signs | ✅ | ✅ | ✅ | ❌ | ❌ |
| Generate Reports | ✅ | ✅* | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage Departments | ✅ | ❌ | ❌ | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ | ❌ | ❌ |

\* Own patients/records only  
\*\* Own records only  

---

## Data Flow Diagram: Patient Registration

```
1. User (Receptionist) clicks "Add New Patient"
   │
   ├─→ Frontend: Open Add Patient Form
   │   ├─ Validation rules applied
   │   └─ Form states managed in React State
   │
   └─→ Form Submission
       │
       ├─→ Frontend Validation
       │   ├─ Check required fields
       │   ├─ Validate email/phone format
       │   └─ Show error messages if invalid
       │
       └─→ API Request: POST /api/patients
           │
           ├─→ Backend: Route Handler
           │   ├─ Extract request body
           │   └─ Verify authentication token
           │
           └─→ Middleware: Authorization Check
               ├─ Check user role (Receptionist/Admin allowed)
               └─ Proceed if authorized
           │
           └─→ Middleware: Input Validation
               ├─ Validate all fields using Joi schema
               ├─ Sanitize input (prevent XSS)
               └─ Return validation errors if invalid
           │
           └─→ Business Logic: PatientService.createPatient()
               │
               ├─→ Check for duplicate email
               ├─→ Generate unique patient ID
               ├─→ Hash sensitive data if needed
               └─→ Prepare patient object
           │
           └─→ Data Access: PatientRepository.create()
               │
               ├─→ Save patient to MongoDB
               ├─→ Return created patient with ID
               └─→ Log audit trail
           │
           └─→ Response: Return to Frontend
               ├─ Success response with patient data
               └─ HTTP 201 Created status
           │
           └─→ Frontend: Handle Response
               ├─ Show success notification
               ├─ Redirect to patient detail page
               └─ Clear form data

2. Patient Created Successfully! ✅
```

---

## State Management Architecture (Context API)

```
App
├── AuthContext
│   ├── currentUser
│   ├── isAuthenticated
│   ├── userRole
│   ├── login()
│   ├── logout()
│   └── refreshToken()
│
├── PatientContext
│   ├── patients (array)
│   ├── selectedPatient
│   ├── searchQuery
│   ├── filters
│   ├── pagination
│   ├── fetchPatients()
│   ├── createPatient()
│   ├── updatePatient()
│   ├── deletePatient()
│   └── searchPatients()
│
├── AppointmentContext
│   ├── appointments (array)
│   ├── selectedAppointment
│   ├── fetchAppointments()
│   ├── createAppointment()
│   ├── updateAppointment()
│   └── cancelAppointment()
│
├── UIContext
│   ├── isLoading
│   ├── isError
│   ├── errorMessage
│   ├── showNotification
│   ├── setLoading()
│   ├── setError()
│   └── showToast()
│
└── NotificationContext
    ├── notifications (array)
    ├── addNotification()
    ├── removeNotification()
    └── clearAllNotifications()
```

---

## Frontend Component Structure

```
src/
├── components/
│   ├── Dashboard/
│   │   ├── Dashboard.jsx
│   │   ├── StatCard.jsx
│   │   ├── RecentActivity.jsx
│   │   └── QuickActions.jsx
│   │
│   ├── Patients/
│   │   ├── PatientList.jsx
│   │   ├── PatientForm.jsx
│   │   ├── PatientDetail.jsx
│   │   ├── PatientSearch.jsx
│   │   └── PatientFilters.jsx
│   │
│   ├── Appointments/
│   │   ├── AppointmentList.jsx
│   │   ├── AppointmentForm.jsx
│   │   ├── AppointmentCalendar.jsx
│   │   └── AppointmentDetail.jsx
│   │
│   ├── MedicalRecords/
│   │   ├── MedicalRecordList.jsx
│   │   ├── MedicalRecordForm.jsx
│   │   ├── RecordDetail.jsx
│   │   ├── LabTests.jsx
│   │   └── Prescriptions.jsx
│   │
│   ├── Reports/
│   │   ├── ReportsPage.jsx
│   │   ├── DashboardMetrics.jsx
│   │   ├── ChartComponents.jsx
│   │   └── ReportGenerator.jsx
│   │
│   ├── Common/
│   │   ├── Navigation.jsx
│   │   ├── Sidebar.jsx
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   ├── Modal.jsx
│   │   ├── Toast.jsx
│   │   ├── Spinner.jsx
│   │   ├── Pagination.jsx
│   │   └── DataTable.jsx
│   │
│   └── Settings/
│       ├── SettingsPage.jsx
│       ├── ProfileSettings.jsx
│       ├── UserManagement.jsx
│       ├── DepartmentManagement.jsx
│       └── SystemSettings.jsx
│
├── hooks/
│   ├── useAuth.js
│   ├── usePatient.js
│   ├── useAppointment.js
│   ├── useFetch.js
│   ├── useLocalStorage.js
│   └── useForm.js
│
├── services/
│   ├── api.js (Axios instance)
│   ├── patientService.js
│   ├── appointmentService.js
│   ├── medicalRecordService.js
│   ├── reportService.js
│   ├── userService.js
│   ├── authService.js
│   └── fileUploadService.js
│
├── context/
│   ├── AuthContext.jsx
│   ├── PatientContext.jsx
│   ├── AppointmentContext.jsx
│   ├── UIContext.jsx
│   └── NotificationContext.jsx
│
├── utils/
│   ├── formatters.js
│   ├── validators.js
│   ├── constants.js
│   ├── errorHandler.js
│   └── dateUtils.js
│
├── styles/
│   ├── globals.css
│   ├── variables.css
│   └── tailwind.config.js
│
└── App.jsx
```

---

## Backend Folder Structure

```
src/
├── config/
│   ├── database.js (MongoDB connection)
│   ├── dotenv.js (Environment variables)
│   └── constants.js
│
├── controllers/
│   ├── patientController.js
│   ├── appointmentController.js
│   ├── medicalRecordController.js
│   ├── labTestController.js
│   ├── reportController.js
│   ├── userController.js
│   ├── authController.js
│   └── departmentController.js
│
├── routes/
│   ├── patientRoutes.js
│   ├── appointmentRoutes.js
│   ├── medicalRecordRoutes.js
│   ├── labTestRoutes.js
│   ├── reportRoutes.js
│   ├── userRoutes.js
│   ├── authRoutes.js
│   └── departmentRoutes.js
│
├── models/
│   ├── Patient.js
│   ├── Doctor.js
│   ├── Appointment.js
│   ├── MedicalRecord.js
│   ├── LabTest.js
│   ├── User.js
│   ├── Department.js
│   └── VitalSigns.js
│
├── services/
│   ├── patientService.js
│   ├── appointmentService.js
│   ├── medicalRecordService.js
│   ├── labTestService.js
│   ├── reportService.js
│   ├── userService.js
│   ├── authService.js
│   ├── emailService.js
│   └── notificationService.js
│
├── middleware/
│   ├── auth.js (JWT verification)
│   ├── authorization.js (Role-based access)
│   ├── validation.js (Input validation)
│   ├── errorHandler.js (Global error handling)
│   ├── logging.js (Request logging)
│   └── rateLimiter.js (Rate limiting)
│
├── utils/
│   ├── validators.js
│   ├── formatters.js
│   ├── errorResponse.js
│   ├── successResponse.js
│   ├── hashPassword.js
│   ├── generateToken.js
│   └── logger.js
│
├── jobs/
│   ├── appointmentReminderJob.js
│   └── dataCleanupJob.js
│
└── app.js
```

---

## Error Handling Strategy

### Error Categories
1. **Validation Errors** (400) - Invalid input
2. **Authentication Errors** (401) - Not logged in
3. **Authorization Errors** (403) - No permission
4. **Not Found Errors** (404) - Resource doesn't exist
5. **Conflict Errors** (409) - Duplicate record
6. **Server Errors** (500) - Internal server error

### Error Response Example
```javascript
{
  success: false,
  statusCode: 400,
  error: {
    code: "VALIDATION_ERROR",
    message: "Invalid input provided",
    details: [
      {
        field: "email",
        message: "Invalid email format",
        value: "invalid-email"
      }
    ]
  },
  timestamp: "2024-01-15T10:30:00Z"
}
```

---

## Security Layers

1. **Frontend Security**
   - HTTPS enforcement
   - XSS prevention (input sanitization)
   - CSRF tokens
   - Secure localStorage usage

2. **API Security**
   - JWT authentication
   - Rate limiting
   - Input validation
   - CORS configuration

3. **Database Security**
   - Password hashing (bcrypt)
   - Encrypted sensitive fields
   - Database access logs
   - Regular backups

4. **Authorization**
   - Role-based access control
   - Resource-level permissions
   - Audit trails

---

## Performance Optimization

1. **Database Optimization**
   - Strategic indexing
   - Query optimization
   - Connection pooling
   - Pagination

2. **API Optimization**
   - Response compression (gzip)
   - Caching strategies
   - Lazy loading
   - API response time < 200ms

3. **Frontend Optimization**
   - Code splitting
   - Image optimization
   - CSS/JS minification
   - Lazy loading components

---

This architecture ensures:
- ✅ Scalability
- ✅ Maintainability
- ✅ Security
- ✅ Performance
- ✅ Easy testing
- ✅ Clear separation of concerns
