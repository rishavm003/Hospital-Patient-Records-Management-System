"""
JWT Authentication Middleware
"""
from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from utils.response import error_response


def jwt_required_custom(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return error_response("Authentication required", 401)
    return decorated


def get_current_user_id():
    return get_jwt_identity()


def get_current_user_role():
    claims = get_jwt()
    return claims.get('role', '')
