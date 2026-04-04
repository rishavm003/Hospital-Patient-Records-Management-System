"""
Patient Controller — HTTP request handlers
"""
from flask import request
from flask_jwt_extended import get_jwt_identity
from utils.response import success_response, error_response, paginated_response
from services import patient_service


def get_patients():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        filters = {
            'search': request.args.get('search'),
            'status': request.args.get('status'),
            'gender': request.args.get('gender'),
            'bloodGroup': request.args.get('bloodGroup')
        }
        patients, pagination = patient_service.get_all_patients(filters, page, page_size)
        return paginated_response(patients, pagination, "Patients retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def get_patient(patient_id):
    try:
        patient = patient_service.get_patient_by_id(patient_id)
        if not patient:
            return error_response("Patient not found", 404)
        return success_response(patient, "Patient retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def create_patient():
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required", 400)
        required = ['firstName', 'lastName', 'email', 'dateOfBirth', 'gender']
        for field in required:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        current_user_id = get_jwt_identity()
        patient_id = patient_service.create_patient(data, current_user_id)
        return success_response({'patientId': patient_id}, "Patient created successfully", 201)
    except ValueError as e:
        return error_response(str(e), 409 if 'already exists' in str(e) else 400)
    except Exception as e:
        return error_response(str(e), 500)


def update_patient(patient_id):
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required", 400)
        current_user_id = get_jwt_identity()
        patient = patient_service.update_patient(patient_id, data, current_user_id)
        return success_response(patient, "Patient updated successfully")
    except ValueError as e:
        return error_response(str(e), 404 if 'not found' in str(e) else 400)
    except Exception as e:
        return error_response(str(e), 500)


def delete_patient(patient_id):
    try:
        patient_service.delete_patient(patient_id)
        return success_response({}, "Patient deleted successfully")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(str(e), 500)


def get_patient_stats():
    try:
        stats = patient_service.get_patient_stats()
        return success_response(stats, "Stats retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)
