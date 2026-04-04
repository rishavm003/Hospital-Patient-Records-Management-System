"""
Standard API response utilities
"""
from flask import jsonify
from datetime import datetime, timezone


def success_response(data=None, message="Success", status_code=200):
    """Return a standard success response"""
    response = {
        "success": True,
        "message": message,
        "statusCode": status_code,
        "data": data if data is not None else {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return jsonify(response), status_code


def error_response(message="An error occurred", status_code=400, error_code=None, details=None):
    """Return a standard error response"""
    response = {
        "success": False,
        "message": message,
        "statusCode": status_code,
        "error": {
            "code": error_code or _get_error_code(status_code),
            "details": details or []
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return jsonify(response), status_code


def paginated_response(items, pagination, message="Retrieved successfully"):
    """Return a paginated response"""
    response = {
        "success": True,
        "message": message,
        "statusCode": 200,
        "data": {
            "items": items,
            "pagination": pagination
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return jsonify(response), 200


def validation_error_response(errors, message="Validation failed"):
    """Return a validation error response"""
    return error_response(
        message=message,
        status_code=422,
        error_code="VALIDATION_ERROR",
        details=errors
    )


def _get_error_code(status_code):
    codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        423: "LOCKED",
        500: "INTERNAL_SERVER_ERROR"
    }
    return codes.get(status_code, "ERROR")
