"""
Department Routes
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.department_controller import (
    get_departments, get_department, create_department,
    update_department, delete_department, get_department_doctors
)
from middleware.authorization import require_roles

department_bp = Blueprint('departments', __name__)

department_bp.route('/', methods=['GET'])(jwt_required()(get_departments))
department_bp.route('/<dept_id>', methods=['GET'])(jwt_required()(get_department))
department_bp.route('/', methods=['POST'])(
    require_roles('Admin')(create_department)
)
department_bp.route('/<dept_id>', methods=['PUT'])(
    require_roles('Admin')(update_department)
)
department_bp.route('/<dept_id>', methods=['DELETE'])(
    require_roles('Admin')(delete_department)
)
department_bp.route('/<dept_id>/doctors', methods=['GET'])(jwt_required()(get_department_doctors))
