"""
Department Service — Business logic
"""
from models.Department import Department
from models.Doctor import Doctor

dept_model = Department()
doctor_model = Doctor()


def get_all_departments(active_only=True):
    return dept_model.find_all(active_only)


def get_department_by_id(dept_id: str):
    return dept_model.find_by_id(dept_id)


def create_department(data: dict):
    existing = dept_model.find_by_name(data.get('name', ''))
    if existing:
        raise ValueError("A department with this name already exists")
    return dept_model.create_department(data)


def update_department(dept_id: str, data: dict):
    existing = dept_model.find_by_id(dept_id)
    if not existing:
        raise ValueError("Department not found")
    dept_model.update_department(dept_id, data)
    return dept_model.find_by_id(dept_id)


def delete_department(dept_id: str):
    existing = dept_model.find_by_id(dept_id)
    if not existing:
        raise ValueError("Department not found")
    dept_model.delete_department(dept_id)


def get_department_doctors(dept_id: str):
    existing = dept_model.find_by_id(dept_id)
    if not existing:
        raise ValueError("Department not found")
    return doctor_model.find_by_department(dept_id)
