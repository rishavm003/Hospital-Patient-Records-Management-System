"""
Medical Record Routes for Hospital Patient Records Management System
Handles medical record CRUD operations and patient medical history
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models.MedicalRecord import MedicalRecord
from models.User import User
from models.Patient import Patient
from utils.validators import validate_required_fields, sanitize_string
from utils.response import success_response, error_response, validation_error_response, paginated_response

medical_record_bp = Blueprint('medical_records', __name__)
medical_record_model = MedicalRecord()
user_model = User()
patient_model = Patient()


def check_user_permission(user_id, required_permission):
    """Check if user has required permission"""
    user = user_model.find_by_id(user_id)
    if not user:
        return False
    return user.get('role') in ['Admin', 'Doctor']


@medical_record_bp.route('', methods=['GET'])
@jwt_required()
def get_medical_records():
    """Get all medical records with optional filters and pagination"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        patient_id = request.args.get('patientId')
        doctor_id = request.args.get('doctorId')
        status = request.args.get('status')
        diagnosis = request.args.get('diagnosis')
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        
        # Build filters
        filters = {}
        if patient_id:
            filters['patientId'] = patient_id
        if doctor_id:
            filters['doctorId'] = doctor_id
        if status:
            filters['status'] = status
        if diagnosis:
            filters['diagnosis'] = diagnosis
        if date_from:
            filters['dateFrom'] = datetime.fromisoformat(date_from)
        if date_to:
            filters['dateTo'] = datetime.fromisoformat(date_to)
        
        result = medical_record_model.get_medical_records(filters, page, page_size)
        return success_response(data=result['data'], message="Medical records retrieved successfully")
    
    except Exception as e:
        return error_response(message=f"Error fetching medical records: {str(e)}", status_code=500)


@medical_record_bp.route('/<record_id>', methods=['GET'])
@jwt_required()
def get_medical_record(record_id):
    """Get a specific medical record by ID"""
    try:
        current_user_id = get_jwt_identity()
        
        result = medical_record_model.get_medical_record_by_id(record_id)
        if not result['success']:
            return error_response(message=result['message'], status_code=404)
        
        # Check if user has permission to view this record
        record = result['data']
        if not check_user_permission(current_user_id, 'view_all_medical_records'):
            # Users can only view their own records unless they have permission
            if (record.get('patientId') != current_user_id and 
                record.get('doctorId') != current_user_id):
                return error_response(message="Access denied", status_code=403)
        
        return success_response(data=result['data'], message="Medical record retrieved successfully")
    
    except Exception as e:
        return error_response(message=f"Error fetching medical record: {str(e)}", status_code=500)


@medical_record_bp.route('', methods=['POST'])
@jwt_required()
def create_medical_record():
    """Create a new medical record"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user has permission to create medical records
        if not check_user_permission(current_user_id, 'create_medical_records'):
            return error_response(message="Access denied", status_code=403)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patientId', 'doctorId', 'diagnosis', 'treatment']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return validation_error_response(errors=missing_fields)
        
        # Sanitize input data
        sanitized_data = {}
        for key, value in data.items():
            sanitized_data[key] = sanitize_string(str(value))
        
        # Set doctor ID to current user if not provided
        if 'doctorId' not in sanitized_data:
            sanitized_data['doctorId'] = current_user_id
        
        result = medical_record_model.create_medical_record(sanitized_data)
        if result['success']:
            return success_response(data={"recordId": result['data']}, message="Medical record created successfully")
        else:
            return error_response(message=result['message'], status_code=400)
    
    except Exception as e:
        return error_response(message=f"Error creating medical record: {str(e)}", status_code=500)


@medical_record_bp.route('/<record_id>', methods=['PUT'])
@jwt_required()
def update_medical_record(record_id):
    """Update an existing medical record"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get medical record first to check permissions
        record_result = medical_record_model.get_medical_record_by_id(record_id)
        if not record_result['success']:
            return error_response(message="Medical record not found", status_code=404)
        
        record = record_result['data']
        
        # Check if user has permission to update this record
        if not check_user_permission(current_user_id, 'edit_all_medical_records'):
            # Users can only edit their own records unless they have permission
            if (record.get('patientId') != current_user_id and 
                record.get('doctorId') != current_user_id):
                return error_response(message="Access denied", status_code=403)
        
        data = request.get_json()
        
        # Validate that we're not trying to change certain fields
        restricted_fields = ['createdAt', 'createdBy']
        for field in restricted_fields:
            data.pop(field, None)
        
        result = medical_record_model.update_medical_record(record_id, data)
        if result['success']:
            return success_response(message="Medical record updated successfully")
        else:
            return error_response(message=result['message'], status_code=400)
    
    except Exception as e:
        return error_response(message=f"Error updating medical record: {str(e)}", status_code=500)


@medical_record_bp.route('/<record_id>/vital-signs', methods=['POST'])
@jwt_required()
def add_vital_signs(record_id):
    """Add vital signs to a medical record"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get medical record first to check permissions
        record_result = medical_record_model.get_medical_record_by_id(record_id)
        if not record_result['success']:
            return error_response(message="Medical record not found", status_code=404)
        
        record = record_result['data']
        
        # Check if user has permission to update this record
        if not check_user_permission(current_user_id, 'edit_all_medical_records'):
            # Users can only edit their own records unless they have permission
            if (record.get('patientId') != current_user_id and 
                record.get('doctorId') != current_user_id):
                return error_response(message="Access denied", status_code=403)
        
        data = request.get_json()
        
        # Validate required fields for vital signs
        required_fields = ['bloodPressure', 'heartRate', 'temperature', 'recordedBy']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return validation_error_response(errors=missing_fields)
        
        # Sanitize and add recorded by
        sanitized_data = {}
        for key, value in data.items():
            sanitized_data[key] = sanitize_string(str(value))
        sanitized_data['recordedBy'] = current_user_id
        
        result = medical_record_model.add_vital_signs(record_id, sanitized_data)
        if result['success']:
            return success_response(message="Vital signs added successfully")
        else:
            return error_response(message=result['message'], status_code=400)
    
    except Exception as e:
        return error_response(message=f"Error adding vital signs: {str(e)}", status_code=500)


@medical_record_bp.route('/<record_id>/prescriptions', methods=['POST'])
@jwt_required()
def add_prescription(record_id):
    """Add prescription to a medical record"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get medical record first to check permissions
        record_result = medical_record_model.get_medical_record_by_id(record_id)
        if not record_result['success']:
            return error_response(message="Medical record not found", status_code=404)
        
        record = record_result['data']
        
        # Check if user has permission to update this record
        if not check_user_permission(current_user_id, 'edit_all_medical_records'):
            # Users can only edit their own records unless they have permission
            if (record.get('patientId') != current_user_id and 
                record.get('doctorId') != current_user_id):
                return error_response(message="Access denied", status_code=403)
        
        data = request.get_json()
        
        # Validate required fields for prescription
        required_fields = ['medication', 'dosage', 'frequency', 'duration']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return validation_error_response(errors=missing_fields)
        
        # Sanitize and add prescribed by
        sanitized_data = {}
        for key, value in data.items():
            sanitized_data[key] = sanitize_string(str(value))
        sanitized_data['prescribedBy'] = current_user_id
        
        result = medical_record_model.add_prescription(record_id, sanitized_data)
        if result['success']:
            return success_response(message="Prescription added successfully")
        else:
            return error_response(message=result['message'], status_code=400)
    
    except Exception as e:
        return error_response(message=f"Error adding prescription: {str(e)}", status_code=500)


@medical_record_bp.route('/patient/<patient_id>', methods=['GET'])
@jwt_required()
def get_patient_medical_records():
    """Get all medical records for a specific patient"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        
        # Check if user has permission to view patient records
        if not check_user_permission(current_user_id, 'view_all_medical_records'):
            # Users can only view their own records unless they have permission
            if patient_id != current_user_id:
                return error_response(message="Access denied", status_code=403)
        
        result = medical_record_model.get_patient_medical_records(patient_id, page, page_size)
        if result['success']:
            return success_response(data=result['data'], message="Patient medical records retrieved successfully")
        else:
            return error_response(message=result['message'], status_code=500)
    
    except Exception as e:
        return error_response(message=f"Error fetching patient medical records: {str(e)}", status_code=500)


@medical_record_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_medical_record_stats():
    """Get medical record statistics"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user has permission to view stats
        if not check_user_permission(current_user_id, 'view_medical_record_stats'):
            return error_response(message="Access denied", status_code=403)
        
        # Get query parameters
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        result = medical_record_model.get_medical_record_stats(start_date, end_date)
        if result['success']:
            return success_response(data=result['data'], message="Medical record statistics retrieved successfully")
        else:
            return error_response(message=result['message'], status_code=500)
    
    except Exception as e:
        return error_response(message=f"Error fetching medical record stats: {str(e)}", status_code=500)


@medical_record_bp.route('/<record_id>', methods=['DELETE'])
@jwt_required()
def delete_medical_record(record_id):
    """Delete a medical record"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get medical record first to check permissions
        record_result = medical_record_model.get_medical_record_by_id(record_id)
        if not record_result['success']:
            return error_response(message="Medical record not found", status_code=404)
        
        record = record_result['data']
        
        # Check if user has permission to delete this record
        if not check_user_permission(current_user_id, 'delete_medical_records'):
            # Users can only delete their own records unless they have permission
            if (record.get('patientId') != current_user_id and 
                record.get('doctorId') != current_user_id):
                return error_response(message="Access denied", status_code=403)
        
        result = medical_record_model.delete_medical_record(record_id)
        if result['success']:
            return success_response(message="Medical record deleted successfully")
        else:
            return error_response(message=result['message'], status_code=400)
    
    except Exception as e:
        return error_response(message=f"Error deleting medical record: {str(e)}", status_code=500)
