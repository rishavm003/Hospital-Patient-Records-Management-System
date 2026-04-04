"""
Medical Record Service — Business logic
"""
from models.MedicalRecord import MedicalRecord
from models.Patient import Patient

record_model = MedicalRecord()
patient_model = Patient()


def get_all_records(filters=None, page=1, page_size=10):
    query = {}
    if filters:
        if filters.get('patientId'):
            from bson import ObjectId
            query['patient'] = ObjectId(filters['patientId'])
        if filters.get('doctorId'):
            from bson import ObjectId
            query['doctor'] = ObjectId(filters['doctorId'])
        if filters.get('status'):
            query['status'] = filters['status']
    records, total = record_model.find_all(query, page, page_size)
    pagination = {
        'currentPage': page,
        'pageSize': page_size,
        'totalItems': total,
        'totalPages': -(-total // page_size),
        'hasNext': page * page_size < total,
        'hasPrev': page > 1
    }
    return records, pagination


def get_record_by_id(record_id: str):
    return record_model.find_by_id(record_id)


def create_record(data: dict):
    patient = patient_model.find_by_id(data.get('patient', ''))
    if not patient:
        raise ValueError("Patient not found")
    return record_model.create_record(data)


def update_record(record_id: str, data: dict):
    existing = record_model.find_by_id(record_id)
    if not existing:
        raise ValueError("Medical record not found")
    record_model.update_record(record_id, data)
    return record_model.find_by_id(record_id)


def get_patient_records(patient_id: str, page=1, page_size=10):
    records, total = record_model.find_by_patient(patient_id, page, page_size)
    pagination = {
        'currentPage': page,
        'pageSize': page_size,
        'totalItems': total,
        'totalPages': -(-total // page_size),
        'hasNext': page * page_size < total,
        'hasPrev': page > 1
    }
    return records, pagination
