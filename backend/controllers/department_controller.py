"""
Department Controller — HTTP request handlers
"""
from flask import request
from utils.response import success_response, error_response
from services import department_service


def get_departments():
    try:
        active_only = request.args.get('activeOnly', 'true').lower() == 'true'
        departments = department_service.get_all_departments(active_only)
        return success_response(departments, "Departments retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def get_department(dept_id):
    try:
        dept = department_service.get_department_by_id(dept_id)
        if not dept:
            return error_response("Department not found", 404)
        return success_response(dept, "Department retrieved successfully")
    except Exception as e:
        return error_response(str(e), 500)


def create_department():
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return error_response("Department name is required", 400)
        dept_id = department_service.create_department(data)
        return success_response({'departmentId': dept_id}, "Department created successfully", 201)
    except ValueError as e:
        return error_response(str(e), 409 if 'already exists' in str(e) else 400)
    except Exception as e:
        return error_response(str(e), 500)


def update_department(dept_id):
    try:
        data = request.get_json()
        dept = department_service.update_department(dept_id, data)
        return success_response(dept, "Department updated successfully")
    except ValueError as e:
        return error_response(str(e), 404 if 'not found' in str(e) else 400)
    except Exception as e:
        return error_response(str(e), 500)


def delete_department(dept_id):
    try:
        department_service.delete_department(dept_id)
        return success_response({}, "Department deleted successfully")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(str(e), 500)


def get_department_doctors(dept_id):
    try:
        doctors = department_service.get_department_doctors(dept_id)
        return success_response(doctors, "Department doctors retrieved")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(str(e), 500)
