"""
Patient Routes for Hospital Patient Records Management System
Handles patient CRUD operations and related functionality
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.Patient import Patient
from models.User import User
from utils.validators import validate_email, validate_phone, validate_required_fields, sanitize_string
from utils.response import success_response, error_response, validation_error_response, paginated_response

patient_bp = Blueprint('patients', __name__)
patient_model = Patient()
user_model = User()

def check_user_permission(user_id, required_permission):
    """Check if user has required permission"""
    user = user_model.find_by_id(user_id)
    if not user:
        return False
    
    user_role = user.get('role', '')
    permissions = user.get('permissions', [])
    
    # Admin has all permissions
    if user_role == 'Admin':
        return True
    
    # Check specific permission
    return required_permission in permissions

@patient_bp.route('', methods=['POST'])
@jwt_required()
def create_patient():
    """Create a new patient"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        if not check_user_permission(current_user_id, 'create_patient'):
            return error_response("Insufficient permissions", 403)
        
        data = request.get_json()
        
        # Validate data
        validation_errors = validate_patient_data(data)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Check for duplicate email
        existing_patient = patient_model.find_by_email(data['email'])
        if existing_patient:
            return error_response("Email already exists", 409)
        
        # Add created by
        data['createdBy'] = current_user_id
        data['updatedBy'] = current_user_id
        
        # Create patient
        patient_id = patient_model.create_patient(data)
        
        return success_response(
            {"patientId": patient_id},
            "Patient created successfully",
            201
        )
        
    except Exception as e:
        return error_response(str(e), 500)

@patient_bp.route('', methods=['GET'])
@jwt_required()
def get_patients():
    """Get all patients with pagination and search"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        if not check_user_permission(current_user_id, 'view_all_patients'):
            return error_response("Insufficient permissions", 403)
        
        # Get query parameters
        page = request.args.get('page', 1)
        page_size = request.args.get('pageSize', 10)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        # Validate pagination
        page, page_size = paginate_query(page, page_size)
        
        # Search patients
        if search:
            result = patient_model.search_patients(search, page, page_size)
        elif status:
            result = patient_model.get_patients_by_status(status, page, page_size)
        else:
            result = patient_model.get_all_patients(page, page_size)
        
        return paginated_response(
            result['patients'],
            result['total'],
            result['page'],
            result['page_size']
        )
        
    except Exception as e:
        return error_response(str(e), 500)

@patient_bp.route('/<patient_id>', methods=['GET'])
@jwt_required()
def get_patient(patient_id):
    """Get a specific patient"""
    try:
        current_user_id = get_jwt_identity()
        user = user_model.find_by_id(current_user_id)
        
        # Check permissions
        if not check_user_permission(current_user_id, 'view_all_patients'):
            # Patients can only view their own records
            if user.get('role') != 'Patient' or current_user_id != patient_id:
                return error_response("Insufficient permissions", 403)
        
        patient = patient_model.find_by_id(patient_id)
        if not patient:
            return error_response("Patient not found", 404)
        
        # Convert ObjectId to string for JSON serialization
        patient['_id'] = str(patient['_id'])
        
        return success_response(patient, "Patient retrieved successfully")
        
    except Exception as e:
        return error_response(str(e), 500)

@patient_bp.route('/<patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    """Update patient information"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        if not check_user_permission(current_user_id, 'edit_patient'):
            return error_response("Insufficient permissions", 403)
        
        data = request.get_json()
        
        # Validate data (partial validation for updates)
        validation_errors = validate_patient_data(data)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Check if patient exists
        existing_patient = patient_model.find_by_id(patient_id)
        if not existing_patient:
            return error_response("Patient not found", 404)
        
        # Check for duplicate email (if email is being updated)
        if 'email' in data and data['email'] != existing_patient.get('email'):
            duplicate_patient = patient_model.find_by_email(data['email'])
            if duplicate_patient:
                return error_response("Email already exists", 409)
        
        # Add updated by
        data['updatedBy'] = current_user_id
        
        # Update patient
        patient_model.update_patient(patient_id, data)
        
        return success_response({}, "Patient updated successfully")
        
    except Exception as e:
        return error_response(str(e), 500)

@patient_bp.route('/<patient_id>/medical-history', methods=['POST'])
@jwt_required()
def add_medical_history(patient_id):
    """Add medical history entry"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        if not check_user_permission(current_user_id, 'create_medical_record'):
            return error_response("Insufficient permissions", 403)
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('condition'):
            return error_response("Condition is required", 400)
        
        # Check if patient exists
        patient = patient_model.find_by_id(patient_id)
        if not patient:
            return error_response("Patient not found", 404)
        
        # Add medical history
        patient_model.add_medical_history(patient_id, data)
        
        return success_response({}, "Medical history added successfully", 201)
        
    except Exception as e:
        return error_response(str(e), 500)

@patient_bp.route('/<patient_id>/allergies', methods=['POST'])
@jwt_required()
def add_allergy(patient_id):
    """Add allergy information"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        if not check_user_permission(current_user_id, 'edit_patient'):
            return error_response("Insufficient permissions", 403)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['allergen', 'severity']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        # Check if patient exists
        patient = patient_model.find_by_id(patient_id)
        if not patient:
            return error_response("Patient not found", 404)
        
        # Add allergy
        patient_model.add_allergy(patient_id, data)
        
        return success_response({}, "Allergy added successfully", 201)
        
    except Exception as e:
        return error_response(str(e), 500)

@patient_bp.route('/<patient_id>/medications', methods=['POST'])
@jwt_required()
def add_medication(patient_id):
    """Add current medication"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        if not check_user_permission(current_user_id, 'edit_patient'):
            return error_response("Insufficient permissions", 403)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['medicineName', 'dosage', 'frequency']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        # Check if patient exists
        patient = patient_model.find_by_id(patient_id)
        if not patient:
            return error_response("Patient not found", 404)
        
        # Add medication
        patient_model.add_medication(patient_id, data)
        
        return success_response({}, "Medication added successfully", 201)
        
    except Exception as e:
        return error_response(str(e), 500)

@patient_bp.route('/<patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    """Delete patient (soft delete)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        if not check_user_permission(current_user_id, 'delete_patient'):
            return error_response("Insufficient permissions", 403)
        
        # Check if patient exists
        patient = patient_model.find_by_id(patient_id)
        if not patient:
            return error_response("Patient not found", 404)
        
        # Soft delete patient
        patient_model.delete_patient(patient_id)
        
        return success_response({}, "Patient deleted successfully")
        
    except Exception as e:
        return error_response(str(e), 500)
