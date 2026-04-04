"""
Lab Test Routes
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.lab_test_controller import (
    get_tests, get_test, create_test, update_results, update_status, get_patient_tests
)
from middleware.authorization import require_roles

lab_test_bp = Blueprint('lab_tests', __name__)

lab_test_bp.route('/', methods=['GET'])(jwt_required()(get_tests))
lab_test_bp.route('/<test_id>', methods=['GET'])(jwt_required()(get_test))
lab_test_bp.route('/', methods=['POST'])(
    require_roles('Admin', 'Doctor')(create_test)
)
lab_test_bp.route('/<test_id>/results', methods=['PUT'])(jwt_required()(update_results))
lab_test_bp.route('/<test_id>/status', methods=['PATCH'])(jwt_required()(update_status))
lab_test_bp.route('/patient/<patient_id>', methods=['GET'])(jwt_required()(get_patient_tests))
