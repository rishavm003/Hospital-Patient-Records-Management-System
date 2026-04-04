"""
Medical Record Controller — HTTP request handlers
"""
from flask import request
from utils.response import success_response, error_response, paginated_response
from services import medical_record_service


def get_records():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        filters = {
            'patientId': request.args.get('patientId'),
            'doctorId': request.args.get('doctorId'),
            'status': request.args.get('status')
        }
        records, pagination = medical_record_service.get_all_records(filters, page, page_size)
        return paginated_response(records, pagination, "Records retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def get_record(record_id):
    try:
        record = medical_record_service.get_record_by_id(record_id)
        if not record:
            return error_response("Medical record not found", 404)
        return success_response(record, "Record retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def create_record():
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required", 400)
        required = ['patient', 'doctor']
        for field in required:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        record_id = medical_record_service.create_record(data)
        return success_response({'recordId': record_id}, "Medical record created successfully", 201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


def update_record(record_id):
    try:
        data = request.get_json()
        record = medical_record_service.update_record(record_id, data)
        return success_response(record, "Record updated successfully")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


def get_patient_records(patient_id):
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        records, pagination = medical_record_service.get_patient_records(patient_id, page, page_size)
        return paginated_response(records, pagination, "Patient records retrieved")
    except Exception as e:
        return error_response(str(e), 500)
