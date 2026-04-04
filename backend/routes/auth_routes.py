"""
Authentication Routes for Hospital Patient Records Management System
Handles user login, logout, registration, and token management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models.User import User
from utils.validators import validate_email, validate_password
from utils.response import success_response, error_response

auth_bp = Blueprint('auth', __name__)
user_model = User()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        # Validate email format
        if not validate_email(data['email']):
            return error_response("Invalid email format", 400)
        
        # Validate password
        if not validate_password(data['password']):
            return error_response("Password must be at least 8 characters long", 400)
        
        # Check if user already exists
        existing_user = user_model.find_by_email(data['email'])
        if existing_user:
            return error_response("Email already exists", 409)
        
        # Create user
        user_data = {
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'email': data['email'],
            'password': data['password'],
            'role': data['role'],
            'phone': data.get('phone', ''),
            'department': data.get('department', None),
            'permissions': data.get('permissions', [])
        }
        
        user_id = user_model.create_user(user_data)
        
        return success_response(
            {"userId": user_id, "message": "User registered successfully"},
            "User created successfully",
            201
        )
        
    except Exception as e:
        return error_response(str(e), 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return error_response("Email and password are required", 400)
        
        # Find user
        user = user_model.find_by_email(data['email'])
        if not user:
            return error_response("Invalid email or password", 401)
        
        # Check if account is locked
        if user_model.is_account_locked(user):
            return error_response("Account is temporarily locked", 423)
        
        # Check if account is active
        if not user.get('isActive', True):
            return error_response("Account is inactive", 401)
        
        # Verify password
        if not user_model.verify_password(user, data['password']):
            user_model.increment_login_attempts(str(user['_id']))
            return error_response("Invalid email or password", 401)
        
        # Reset login attempts on successful login
        user_model.reset_login_attempts(str(user['_id']))
        
        # Update last login
        user_model.update_last_login(str(user['_id']))
        
        # Log activity
        user_model.log_activity(
            str(user['_id']),
            'LOGIN',
            request.remote_addr,
            request.headers.get('User-Agent', '')
        )
        
        # Create tokens
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={'role': user['role']}
        )
        refresh_token = create_refresh_token(identity=str(user['_id']))
        
        # Prepare user data for response
        user_response = {
            'id': str(user['_id']),
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'email': user['email'],
            'role': user['role'],
            'permissions': user.get('permissions', []),
            'department': user.get('department')
        }
        
        return success_response({
            'user': user_response,
            'accessToken': access_token,
            'refreshToken': refresh_token
        }, "Login successful")
        
    except Exception as e:
        return error_response(str(e), 500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = user_model.find_by_id(current_user_id)
        
        if not user or not user.get('isActive', True):
            return error_response("User not found or inactive", 401)
        
        new_access_token = create_access_token(
            identity=current_user_id,
            additional_claims={'role': user['role']}
        )
        
        return success_response({
            'accessToken': new_access_token
        }, "Token refreshed successfully")
        
    except Exception as e:
        return error_response(str(e), 500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout"""
    try:
        current_user_id = get_jwt_identity()
        
        # Log activity
        user_model.log_activity(
            current_user_id,
            'LOGOUT',
            request.remote_addr,
            request.headers.get('User-Agent', '')
        )
        
        return success_response({}, "Logout successful")
        
    except Exception as e:
        return error_response(str(e), 500)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = user_model.find_by_id(current_user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        user_response = {
            'id': str(user['_id']),
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'email': user['email'],
            'phone': user.get('phone', ''),
            'role': user['role'],
            'permissions': user.get('permissions', []),
            'department': user.get('department'),
            'isActive': user.get('isActive', True),
            'lastLogin': user.get('lastLogin'),
            'createdAt': user.get('createdAt')
        }
        
        return success_response(user_response, "Profile retrieved successfully")
        
    except Exception as e:
        return error_response(str(e), 500)

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('currentPassword') or not data.get('newPassword'):
            return error_response("Current password and new password are required", 400)
        
        user = user_model.find_by_id(current_user_id)
        if not user:
            return error_response("User not found", 404)
        
        # Verify current password
        if not user_model.verify_password(user, data['currentPassword']):
            return error_response("Current password is incorrect", 401)
        
        # Update password
        user_model.update_password(current_user_id, data['newPassword'])
        
        # Log activity
        user_model.log_activity(
            current_user_id,
            'PASSWORD_CHANGED',
            request.remote_addr,
            request.headers.get('User-Agent', '')
        )
        
        return success_response({}, "Password changed successfully")
        
    except Exception as e:
        return error_response(str(e), 500)
