"""
Role-Based Access Control (RBAC) Authorization Middleware
"""
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from utils.response import error_response

ROLE_HIERARCHY = {
    'Admin': 5,
    'Doctor': 4,
    'Nurse': 3,
    'Receptionist': 2,
    'Patient': 1
}


def require_roles(*allowed_roles):
    """Decorator: restrict endpoint to specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get('role', '')
                if user_role not in allowed_roles:
                    return error_response(
                        f"Access denied. Required roles: {', '.join(allowed_roles)}",
                        403,
                        "FORBIDDEN"
                    )
                return f(*args, **kwargs)
            except Exception:
                return error_response("Authentication required", 401)
        return decorated
    return decorator


def require_min_role(min_role: str):
    """Decorator: restrict endpoint to roles at or above minimum level"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get('role', '')
                user_level = ROLE_HIERARCHY.get(user_role, 0)
                required_level = ROLE_HIERARCHY.get(min_role, 99)
                if user_level < required_level:
                    return error_response("Insufficient permissions", 403, "FORBIDDEN")
                return f(*args, **kwargs)
            except Exception:
                return error_response("Authentication required", 401)
        return decorated
    return decorator
