"""
Lab Test Controller — HTTP request handlers
"""
from flask import request
from utils.response import success_response, error_response, paginated_response
from services import lab_test_service


def get_tests():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        filters = {
            'patientId': request.args.get('patientId'),
            'status': request.args.get('status'),
            'urgency': request.args.get('urgency')
        }
        tests, pagination = lab_test_service.get_all_tests(filters, page, page_size)
        return paginated_response(tests, pagination, "Lab tests retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def get_test(test_id):
    try:
        test = lab_test_service.get_test_by_id(test_id)
        if not test:
            return error_response("Lab test not found", 404)
        return success_response(test, "Lab test retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def create_test():
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required", 400)
        required = ['patient', 'requestedBy', 'testType', 'testName']
        for field in required:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        test_id = lab_test_service.create_test(data)
        return success_response({'testId': test_id}, "Lab test created successfully", 201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


def update_results(test_id):
    try:
        data = request.get_json()
        test = lab_test_service.update_results(test_id, data)
        return success_response(test, "Lab test results updated successfully")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


def update_status(test_id):
    try:
        data = request.get_json() or {}
        status = data.get('status')
        if not status:
            return error_response("Status is required", 400)
        lab_test_service.update_status(test_id, status)
        return success_response({}, "Status updated successfully")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


def get_patient_tests(patient_id):
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        tests, pagination = lab_test_service.get_patient_tests(patient_id, page, page_size)
        return paginated_response(tests, pagination, "Patient lab tests retrieved")
    except Exception as e:
        return error_response(str(e), 500)
