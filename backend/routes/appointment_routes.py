"""
Appointment Routes for Hospital Patient Records Management System
Handles appointment scheduling, management, and calendar operations
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models.Appointment import Appointment
from models.User import User
from models.Patient import Patient
from utils.validators import validate_required_fields, sanitize_string
from utils.response import success_response, error_response, validation_error_response, paginated_response

appointment_bp = Blueprint('appointments', __name__)
appointment_model = Appointment()
user_model = User()
patient_model = Patient()


def check_user_permission(user_id, required_permission):
    """Check if user has required permission"""
    user = user_model.find_by_id(user_id)
    if not user:
        return False
    return user.get('role') == 'Admin' or user.get('role') == 'Doctor'


@appointment_bp.route('', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get all appointments with optional filters and pagination"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        status = request.args.get('status')
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        patient_id = request.args.get('patientId')
        doctor_id = request.args.get('doctorId')
        department = request.args.get('department')
        
        # Build filters
        filters = {}
        if status:
            filters['status'] = status
        if date_from:
            filters['dateFrom'] = datetime.fromisoformat(date_from)
        if date_to:
            filters['dateTo'] = datetime.fromisoformat(date_to)
        if patient_id:
            filters['patientId'] = patient_id
        if doctor_id:
            filters['doctorId'] = doctor_id
        if department:
            filters['department'] = department
        
        result = appointment_model.get_appointments(filters, page, page_size)
        return success_response(data=result['data'], message="Appointments retrieved successfully")
    
    except Exception as e:
        return error_response(message=f"Error fetching appointments: {str(e)}", status_code=500)


@appointment_bp.route('/<appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Get a specific appointment by ID"""
    try:
        current_user_id = get_jwt_identity()
        
        result = appointment_model.get_appointment_by_id(appointment_id)
        if not result['success']:
            return error_response(message=result['message'], status_code=404)
        
        # Check if user has permission to view this appointment
        appointment = result['data']
        if not check_user_permission(current_user_id, 'view_all_appointments'):
            # Users can only view their own appointments unless they have permission
            if (appointment.get('patientId') != current_user_id and 
                appointment.get('doctorId') != current_user_id):
                return error_response(message="Access denied", status_code=403)
        
        return success_response(data=result['data'], message="Appointment retrieved successfully")
    
    except Exception as e:
        return error_response(message=f"Error fetching appointment: {str(e)}", status_code=500)


@appointment_bp.route('', methods=['POST'])
@jwt_required()
def create_appointment():
    """Create a new appointment"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user has permission to create appointments
        if not check_user_permission(current_user_id, 'create_appointment'):
            return error_response(message="Access denied", status_code=403)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patientId', 'doctorId', 'dateTime', 'type', 'duration']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return validation_error_response(errors=missing_fields)
        
        # Sanitize input data
        sanitized_data = {}
        for key, value in data.items():
            sanitized_data[key] = sanitize_string(str(value))
        
        # Check for appointment conflicts
        if 'doctorId' in sanitized_data and 'dateTime' in sanitized_data:
            conflict_check = appointment_model.check_appointment_conflict(
                sanitized_data['doctorId'],
                sanitized_data['dateTime'],
                sanitized_data.get('duration', 30)
            )
            
            if conflict_check.get('hasConflict'):
                return error_response(
                    message="Appointment time conflicts with existing appointments",
                    status_code=409,
                    details={"conflicts": conflict_check.get('conflicts')}
                )
        
        result = appointment_model.create_appointment(sanitized_data)
        if result['success']:
            return success_response(data={"appointmentId": result['data']}, message="Appointment created successfully")
        else:
            return error_response(message=result['message'], status_code=400)
    
    except Exception as e:
        return error_response(message=f"Error creating appointment: {str(e)}", status_code=500)


@appointment_bp.route('/<appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update an existing appointment"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the appointment first to check permissions
        appointment_result = appointment_model.get_appointment_by_id(appointment_id)
        if not appointment_result['success']:
            return error_response(message="Appointment not found", status_code=404)
        
        appointment = appointment_result['data']
        
        # Check if user has permission to update this appointment
        if not check_user_permission(current_user_id, 'edit_all_appointments'):
            # Users can only edit their own appointments unless they have permission
            if (appointment.get('patientId') != current_user_id and 
                appointment.get('doctorId') != current_user_id):
                return error_response(message="Access denied", status_code=403)
        
        data = request.get_json()
        
        # Validate that we're not trying to change certain fields
        restricted_fields = ['createdAt', 'createdBy']
        for field in restricted_fields:
            data.pop(field, None)
        
        result = appointment_model.update_appointment(appointment_id, data)
        if result['success']:
            return success_response(message="Appointment updated successfully")
        else:
            return error_response(message=result['message'], status_code=400)
    
    except Exception as e:
        return error_response(message=f"Error updating appointment: {str(e)}", status_code=500)


@appointment_bp.route('/<appointment_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the appointment first to check permissions
        appointment_result = appointment_model.get_appointment_by_id(appointment_id)
        if not appointment_result['success']:
            return error_response(message="Appointment not found", status_code=404)
        
        appointment = appointment_result['data']
        
        # Check if user has permission to cancel this appointment
        if not check_user_permission(current_user_id, 'cancel_appointment'):
            # Users can only cancel their own appointments unless they have permission
            if (appointment.get('patientId') != current_user_id and 
                appointment.get('doctorId') != current_user_id):
                return error_response(message="Access denied", status_code=403)
        
        data = request.get_json()
        reason = data.get('reason') if data else None
        
        result = appointment_model.cancel_appointment(appointment_id, reason)
        if result['success']:
            return success_response(message="Appointment cancelled successfully")
        else:
            return error_response(message=result['message'], status_code=400)
    
    except Exception as e:
        return error_response(message=f"Error cancelling appointment: {str(e)}", status_code=500)


@appointment_bp.route('/<appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    """Delete an appointment"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the appointment first to check permissions
        appointment_result = appointment_model.get_appointment_by_id(appointment_id)
        if not appointment_result['success']:
            return error_response(message="Appointment not found", status_code=404)
        
        appointment = appointment_result['data']
        
        # Check if user has permission to delete this appointment
        if not check_user_permission(current_user_id, 'delete_appointment'):
            # Users can only delete their own appointments unless they have permission
            if (appointment.get('patientId') != current_user_id and 
                appointment.get('doctorId') != current_user_id):
                return error_response(message="Access denied", status_code=403)
        
        result = appointment_model.delete_appointment(appointment_id)
        if result['success']:
            return success_response(message="Appointment deleted successfully")
        else:
            return error_response(message=result['message'], status_code=400)
    
    except Exception as e:
        return error_response(message=f"Error deleting appointment: {str(e)}", status_code=500)


@appointment_bp.route('/calendar/<int:year>/<int:month>', methods=['GET'])
@jwt_required()
def get_calendar_appointments(year, month):
    """Get appointments for a specific month (for calendar view)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Calculate date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1, 1) - timedelta(days=1)
        
        # Get appointments for the date range
        result = appointment_model.get_appointments_by_date_range(start_date, end_date, current_user_id)
        if result['success']:
            return success_response(data=result['data'], message="Calendar appointments retrieved successfully")
        else:
            return error_response(message=result['message'], status_code=500)
    
    except Exception as e:
        return error_response(message=f"Error fetching calendar appointments: {str(e)}", status_code=500)


@appointment_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_appointment_stats():
    """Get appointment statistics"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user has permission to view stats
        if not check_user_permission(current_user_id, 'view_appointment_stats'):
            return error_response(message="Access denied", status_code=403)
        
        # Get query parameters
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        result = appointment_model.get_appointment_stats(start_date, end_date)
        if result['success']:
            return success_response(data=result['data'], message="Appointment statistics retrieved successfully")
        else:
            return error_response(message=result['message'], status_code=500)
    
    except Exception as e:
        return error_response(message=f"Error fetching appointment stats: {str(e)}", status_code=500)


@appointment_bp.route('/available-slots', methods=['GET'])
@jwt_required()
def get_available_slots():
    """Get available appointment slots for a specific date"""
    try:
        date_str = request.args.get('date')
        doctor_id = request.args.get('doctorId')
        
        if not date_str:
            return error_response(message="Date parameter is required", status_code=400)
        
        appointment_date = datetime.fromisoformat(date_str)
        
        # Get existing appointments for the date
        filters = {
            'dateFrom': appointment_date,
            'dateTo': appointment_date + timedelta(days=1),  # End of day
            'status': 'Scheduled'
        }
        
        if doctor_id:
            filters['doctorId'] = doctor_id
        
        result = appointment_model.get_appointments(filters)
        if result['success']:
            appointments = result['data']
            
            # Generate available time slots (9 AM to 5 PM, 30-minute intervals)
            all_slots = []
            for hour in range(9, 18):  # 9 AM to 5 PM
                for minute in [0, 30]:
                    slot_time = appointment_date.replace(hour=hour, minute=minute)
                    all_slots.append({
                        'time': slot_time.strftime('%H:%M'),
                        'available': True
                    })
            
            # Mark occupied slots
            for apt in appointments:
                apt_time = datetime.fromisoformat(apt['dateTime'])
                slot_hour = apt_time.hour
                slot_minute = apt_time.minute
                
                # Find and mark the slot as occupied
                for i, slot in enumerate(all_slots):
                    slot_time = datetime.fromisoformat(f"{appointment_date.strftime('%Y-%m-%d')} {slot['time']}")
                    if (slot_time.hour == slot_hour and 
                        abs(slot_time.minute - slot_minute) < 30):
                        all_slots[i]['available'] = False
                        break
            
            return success_response(data={'date': date_str, 'slots': all_slots}, message="Available slots retrieved successfully")
        else:
            return error_response(message="Error checking available slots", status_code=500)
    
    except Exception as e:
        return error_response(message=f"Error checking available slots: {str(e)}", status_code=500)
