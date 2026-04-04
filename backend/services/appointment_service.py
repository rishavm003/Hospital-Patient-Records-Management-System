"""
Appointment Service — Business logic for appointment scheduling
"""
from models.Appointment import Appointment
from models.Doctor import Doctor
from models.Patient import Patient

appointment_model = Appointment()
doctor_model = Doctor()
patient_model = Patient()


def get_all_appointments(filters=None, page=1, page_size=10):
    query = {}
    if filters:
        if filters.get('status'):
            query['status'] = filters['status']
        if filters.get('date'):
            query['date'] = filters['date']
        if filters.get('doctorId'):
            from bson import ObjectId
            query['doctor'] = ObjectId(filters['doctorId'])
        if filters.get('patientId'):
            from bson import ObjectId
            query['patient'] = ObjectId(filters['patientId'])
    appointments, total = appointment_model.find_all(query, page, page_size)
    pagination = {
        'currentPage': page,
        'pageSize': page_size,
        'totalItems': total,
        'totalPages': -(-total // page_size),
        'hasNext': page * page_size < total,
        'hasPrev': page > 1
    }
    return appointments, pagination


def get_appointment_by_id(appointment_id: str):
    return appointment_model.find_by_id(appointment_id)


def create_appointment(data: dict):
    patient = patient_model.find_by_id(data.get('patient', ''))
    if not patient:
        raise ValueError("Patient not found")
    doctor = doctor_model.find_by_id(data.get('doctor', ''))
    if not doctor:
        raise ValueError("Doctor not found")
    return appointment_model.create_appointment(data)


def update_appointment(appointment_id: str, data: dict):
    existing = appointment_model.find_by_id(appointment_id)
    if not existing:
        raise ValueError("Appointment not found")
    if existing['status'] in ['Cancelled', 'Completed']:
        raise ValueError(f"Cannot update a {existing['status']} appointment")
    appointment_model.update_appointment(appointment_id, data)
    return appointment_model.find_by_id(appointment_id)


def cancel_appointment(appointment_id: str, reason: str, cancelled_by: str):
    existing = appointment_model.find_by_id(appointment_id)
    if not existing:
        raise ValueError("Appointment not found")
    if existing['status'] == 'Cancelled':
        raise ValueError("Appointment is already cancelled")
    appointment_model.cancel_appointment(appointment_id, reason, cancelled_by)


def complete_appointment(appointment_id: str, doctor_notes: str):
    existing = appointment_model.find_by_id(appointment_id)
    if not existing:
        raise ValueError("Appointment not found")
    appointment_model.complete_appointment(appointment_id, doctor_notes)


def get_patient_appointments(patient_id: str, page=1, page_size=10):
    appointments, total = appointment_model.find_by_patient(patient_id, page, page_size)
    pagination = {
        'currentPage': page,
        'pageSize': page_size,
        'totalItems': total,
        'totalPages': -(-total // page_size),
        'hasNext': page * page_size < total,
        'hasPrev': page > 1
    }
    return appointments, pagination


def get_doctor_appointments(doctor_id: str, date=None):
    return appointment_model.find_by_doctor(doctor_id, date)


def get_appointment_stats():
    return appointment_model.count_by_status()
