"""
Appointment Controller — HTTP request handlers
"""
from flask import request
from flask_jwt_extended import get_jwt_identity
from utils.response import success_response, error_response, paginated_response
from services import appointment_service


def get_appointments():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        filters = {
            'status': request.args.get('status'),
            'date': request.args.get('date'),
            'doctorId': request.args.get('doctorId'),
            'patientId': request.args.get('patientId')
        }
        appointments, pagination = appointment_service.get_all_appointments(filters, page, page_size)
        return paginated_response(appointments, pagination, "Appointments retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def get_appointment(appointment_id):
    try:
        appointment = appointment_service.get_appointment_by_id(appointment_id)
        if not appointment:
            return error_response("Appointment not found", 404)
        return success_response(appointment, "Appointment retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def create_appointment():
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required", 400)
        required = ['patient', 'doctor', 'date', 'startTime']
        for field in required:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        appointment_id = appointment_service.create_appointment(data)
        return success_response({'appointmentId': appointment_id}, "Appointment created successfully", 201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


def update_appointment(appointment_id):
    try:
        data = request.get_json()
        appointment = appointment_service.update_appointment(appointment_id, data)
        return success_response(appointment, "Appointment updated successfully")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


def cancel_appointment(appointment_id):
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        current_user_id = get_jwt_identity()
        appointment_service.cancel_appointment(appointment_id, reason, current_user_id)
        return success_response({}, "Appointment cancelled successfully")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


def complete_appointment(appointment_id):
    try:
        data = request.get_json() or {}
        doctor_notes = data.get('doctorNotes', '')
        appointment_service.complete_appointment(appointment_id, doctor_notes)
        return success_response({}, "Appointment completed successfully")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


def get_appointment_stats():
    try:
        stats = appointment_service.get_appointment_stats()
        return success_response(stats, "Stats retrieved")
    except Exception as e:
        return error_response(str(e), 500)
