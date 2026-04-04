"""
Constants for Hospital Patient Records Management System
Application-wide constants and configurations
"""

# User Roles
USER_ROLES = {
    'ADMIN': 'Admin',
    'DOCTOR': 'Doctor', 
    'NURSE': 'Nurse',
    'RECEPTIONIST': 'Receptionist',
    'PATIENT': 'Patient'
}

# User Permissions
PERMISSIONS = {
    'VIEW_ALL_PATIENTS': 'view_all_patients',
    'CREATE_PATIENT': 'create_patient',
    'EDIT_PATIENT': 'edit_patient',
    'DELETE_PATIENT': 'delete_patient',
    'CREATE_MEDICAL_RECORD': 'create_medical_record',
    'VIEW_MEDICAL_RECORD': 'view_medical_record',
    'CREATE_LAB_TEST': 'create_lab_test',
    'VIEW_LAB_RESULTS': 'view_lab_results',
    'SCHEDULE_APPOINTMENT': 'schedule_appointment',
    'VIEW_APPOINTMENTS': 'view_appointments',
    'RECORD_VITAL_SIGNS': 'record_vital_signs',
    'GENERATE_REPORTS': 'generate_reports',
    'MANAGE_USERS': 'manage_users',
    'MANAGE_DEPARTMENTS': 'manage_departments',
    'SYSTEM_SETTINGS': 'system_settings'
}

# Appointment Status
APPOINTMENT_STATUS = {
    'SCHEDULED': 'Scheduled',
    'COMPLETED': 'Completed', 
    'CANCELLED': 'Cancelled',
    'NO_SHOW': 'No-show'
}

# Appointment Types
APPOINTMENT_TYPES = {
    'CONSULTATION': 'Consultation',
    'FOLLOW_UP': 'Follow-up',
    'SURGERY': 'Surgery',
    'LAB_TEST': 'Lab Test'
}

# Lab Test Status
LAB_TEST_STATUS = {
    'PENDING': 'Pending',
    'IN_PROGRESS': 'In Progress',
    'COMPLETED': 'Completed'
}

# Lab Test Urgency
LAB_TEST_URGENCY = {
    'ROUTINE': 'Routine',
    'URGENT': 'Urgent'
}

# Patient Status
PATIENT_STATUS = {
    'ACTIVE': 'Active',
    'DISCHARGED': 'Discharged',
    'TRANSFERRED': 'Transferred'
}

# Medical Record Status
MEDICAL_RECORD_STATUS = {
    'ACTIVE': 'Active',
    'COMPLETED': 'Completed'
}

# Blood Groups
BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

# Genders
GENDERS = ['Male', 'Female', 'Other']

# Allergy Severity
ALLERGY_SEVERITY = ['Mild', 'Moderate', 'Severe']

# File Categories
FILE_CATEGORIES = ['X-Ray', 'Lab Report', 'Prescription', 'Insurance', 'Other']

# API Response Messages
RESPONSE_MESSAGES = {
    'PATIENT_CREATED': 'Patient created successfully',
    'PATIENT_UPDATED': 'Patient updated successfully', 
    'PATIENT_DELETED': 'Patient deleted successfully',
    'APPOINTMENT_SCHEDULED': 'Appointment scheduled successfully',
    'APPOINTMENT_CANCELLED': 'Appointment cancelled successfully',
    'MEDICAL_RECORD_CREATED': 'Medical record created successfully',
    'LAB_TEST_CREATED': 'Lab test created successfully',
    'USER_CREATED': 'User created successfully',
    'LOGIN_SUCCESS': 'Login successful',
    'LOGOUT_SUCCESS': 'Logout successful'
}

# Error Messages
ERROR_MESSAGES = {
    'INVALID_CREDENTIALS': 'Invalid email or password',
    'UNAUTHORIZED': 'Unauthorized access',
    'FORBIDDEN': 'Access forbidden',
    'NOT_FOUND': 'Resource not found',
    'VALIDATION_ERROR': 'Validation error',
    'DUPLICATE_EMAIL': 'Email already exists',
    'SERVER_ERROR': 'Internal server error'
}

# Pagination Defaults
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour in seconds
JWT_REFRESH_TOKEN_EXPIRES = 86400 * 7  # 7 days in seconds

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']

# Email Configuration
EMAIL_SUBJECTS = {
    'APPOINTMENT_REMINDER': 'Appointment Reminder',
    'LAB_TEST_READY': 'Lab Test Results Ready',
    'PASSWORD_RESET': 'Password Reset Request'
}
