"""
Lab Test Service — Business logic
"""
from models.LabTest import LabTest
from models.Patient import Patient

lab_model = LabTest()
patient_model = Patient()


def get_all_tests(filters=None, page=1, page_size=10):
    query = {}
    if filters:
        if filters.get('patientId'):
            from bson import ObjectId
            query['patient'] = ObjectId(filters['patientId'])
        if filters.get('status'):
            query['status'] = filters['status']
        if filters.get('urgency'):
            query['urgency'] = filters['urgency']
    tests, total = lab_model.find_all(query, page, page_size)
    pagination = {
        'currentPage': page,
        'pageSize': page_size,
        'totalItems': total,
        'totalPages': -(-total // page_size),
        'hasNext': page * page_size < total,
        'hasPrev': page > 1
    }
    return tests, pagination


def get_test_by_id(test_id: str):
    return lab_model.find_by_id(test_id)


def create_test(data: dict):
    patient = patient_model.find_by_id(data.get('patient', ''))
    if not patient:
        raise ValueError("Patient not found")
    return lab_model.create_test(data)


def update_results(test_id: str, data: dict):
    existing = lab_model.find_by_id(test_id)
    if not existing:
        raise ValueError("Lab test not found")
    lab_model.update_results(test_id, data)
    return lab_model.find_by_id(test_id)


def update_status(test_id: str, status: str):
    valid_statuses = ['Pending', 'In Progress', 'Completed']
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    existing = lab_model.find_by_id(test_id)
    if not existing:
        raise ValueError("Lab test not found")
    lab_model.update_status(test_id, status)


def get_patient_tests(patient_id: str, page=1, page_size=10):
    tests, total = lab_model.find_by_patient(patient_id, page, page_size)
    pagination = {
        'currentPage': page,
        'pageSize': page_size,
        'totalItems': total,
        'totalPages': -(-total // page_size),
        'hasNext': page * page_size < total,
        'hasPrev': page > 1
    }
    return tests, pagination
