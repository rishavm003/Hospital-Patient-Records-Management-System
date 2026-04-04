"""
Patient Service — Business logic for patient operations
"""
from models.Patient import Patient
from utils.validators import validate_email, validate_phone

patient_model = Patient()


def get_all_patients(filters=None, page=1, page_size=10):
    query = {}
    if filters:
        if filters.get('status'):
            query['status'] = filters['status']
        if filters.get('search'):
            s = filters['search']
            import re
            pattern = re.compile(s, re.IGNORECASE)
            query['$or'] = [
                {'firstName': pattern},
                {'lastName': pattern},
                {'email': pattern},
                {'phone': pattern}
            ]
        if filters.get('gender'):
            query['gender'] = filters['gender']
        if filters.get('bloodGroup'):
            query['bloodGroup'] = filters['bloodGroup']
    patients, total = patient_model.find_all(query, page, page_size)
    pagination = {
        'currentPage': page,
        'pageSize': page_size,
        'totalItems': total,
        'totalPages': -(-total // page_size),
        'hasNext': page * page_size < total,
        'hasPrev': page > 1
    }
    return patients, pagination


def get_patient_by_id(patient_id: str):
    return patient_model.find_by_id(patient_id)


def create_patient(data: dict, created_by: str):
    if not validate_email(data.get('email', '')):
        raise ValueError("Invalid email format")
    if data.get('phone') and not validate_phone(data['phone']):
        raise ValueError("Invalid phone number")
    existing = patient_model.find_by_email(data['email'])
    if existing:
        raise ValueError("A patient with this email already exists")
    data['createdBy'] = created_by
    return patient_model.create_patient(data)


def update_patient(patient_id: str, data: dict, updated_by: str):
    existing = patient_model.find_by_id(patient_id)
    if not existing:
        raise ValueError("Patient not found")
    if 'email' in data and not validate_email(data['email']):
        raise ValueError("Invalid email format")
    data['updatedBy'] = updated_by
    patient_model.update_patient(patient_id, data)
    return patient_model.find_by_id(patient_id)


def delete_patient(patient_id: str):
    existing = patient_model.find_by_id(patient_id)
    if not existing:
        raise ValueError("Patient not found")
    patient_model.delete_patient(patient_id)


def get_patient_stats():
    return patient_model.get_stats()
