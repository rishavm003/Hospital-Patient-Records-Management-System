"""
Medical Record Routes
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.medical_record_controller import (
    get_records, get_record, create_record, update_record, get_patient_records
)
from middleware.authorization import require_roles

medical_record_bp = Blueprint('medical_records', __name__)

medical_record_bp.route('/', methods=['GET'])(jwt_required()(get_records))
medical_record_bp.route('/<record_id>', methods=['GET'])(jwt_required()(get_record))
medical_record_bp.route('/', methods=['POST'])(
    require_roles('Admin', 'Doctor')(create_record)
)
medical_record_bp.route('/<record_id>', methods=['PUT'])(
    require_roles('Admin', 'Doctor')(update_record)
)
medical_record_bp.route('/patient/<patient_id>', methods=['GET'])(jwt_required()(get_patient_records))
