"""
User Routes for Hospital Patient Records Management System
Handles user management and administrative functions
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.User import User
from utils.validators import validate_email, validate_required_fields, sanitize_string
from utils.response import success_response, error_response, validation_error_response, paginated_response

user_bp = Blueprint('users', __name__)
user_model = User()

def check_admin_permission(user_id):
    """Check if user has admin permissions"""
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'Admin'

@user_bp.route('', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check admin permissions
        if not check_admin_permission(current_user_id):
            return error_response("Admin access required", 403)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'role']
        validation_errors = []
        
        for field in required_fields:
            if not data.get(field):
                validation_errors.append(f"{field} is required")
        
        # Validate email
        if data.get('email') and not validate_email(data['email']):
            validation_errors.append("Invalid email format")
        
        # Validate names
        if data.get('firstName') and not validate_name(data['firstName']):
            validation_errors.append("Invalid first name")
        
        if data.get('lastName') and not validate_name(data['lastName']):
            validation_errors.append("Invalid last name")
        
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Check for duplicate email
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
            'permissions': data.get('permissions', []),
            'createdBy': current_user_id
        }
        
        user_id = user_model.create_user(user_data)
        
        return success_response(
            {"userId": user_id},
            "User created successfully",
            201
        )
        
    except Exception as e:
        return error_response(str(e), 500)

@user_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with pagination (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check admin permissions
        if not check_admin_permission(current_user_id):
            return error_response("Admin access required", 403)
        
        # Get query parameters
        page = request.args.get('page', 1)
        page_size = request.args.get('pageSize', 10)
        role = request.args.get('role', '')
        
        # Validate pagination
        page, page_size = paginate_query(page, page_size)
        
        # Get users
        if role:
            users = user_model.get_users_by_role(role)
            total = len(users)
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            paginated_users = users[start:end]
        else:
            # Get all users from collection
            collection = user_model.collection
            skip = (page - 1) * page_size
            paginated_users = list(collection.find({})
                                   .skip(skip)
                                   .limit(page_size)
                                   .sort('createdAt', -1))
            total = collection.count_documents({})
        
        # Convert ObjectIds to strings
        for user in paginated_users:
            user['_id'] = str(user['_id'])
            if 'createdBy' in user and user['createdBy']:
                user['createdBy'] = str(user['createdBy'])
        
        return paginated_response(
            paginated_users,
            total,
            page,
            page_size
        )
        
    except Exception as e:
        return error_response(str(e), 500)

@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Users can view their own profile, admins can view any
        if current_user_id != user_id and not check_admin_permission(current_user_id):
            return error_response("Insufficient permissions", 403)
        
        user = user_model.find_by_id(user_id)
        if not user:
            return error_response("User not found", 404)
        
        # Convert ObjectId to string
        user['_id'] = str(user['_id'])
        if 'createdBy' in user and user['createdBy']:
            user['createdBy'] = str(user['createdBy'])
        
        # Remove sensitive data
        user.pop('password', None)
        user.pop('passwordResetToken', None)
        user.pop('passwordResetExpires', None)
        
        return success_response(user, "User retrieved successfully")
        
    except Exception as e:
        return error_response(str(e), 500)

@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user information"""
    try:
        current_user_id = get_jwt_identity()
        
        # Users can update their own profile, admins can update any
        if current_user_id != user_id and not check_admin_permission(current_user_id):
            return error_response("Insufficient permissions", 403)
        
        data = request.get_json()
        
        # Validate data
        validation_errors = []
        
        if 'email' in data:
            if not validate_email(data['email']):
                validation_errors.append("Invalid email format")
        
        if 'firstName' in data and not validate_name(data['firstName']):
            validation_errors.append("Invalid first name")
        
        if 'lastName' in data and not validate_name(data['lastName']):
            validation_errors.append("Invalid last name")
        
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Check if user exists
        existing_user = user_model.find_by_id(user_id)
        if not existing_user:
            return error_response("User not found", 404)
        
        # Check for duplicate email (if email is being updated)
        if 'email' in data and data['email'] != existing_user.get('email'):
            duplicate_user = user_model.find_by_email(data['email'])
            if duplicate_user:
                return error_response("Email already exists", 409)
        
        # Non-admins cannot change certain fields
        if not check_admin_permission(current_user_id):
            restricted_fields = ['role', 'permissions', 'isActive', 'department']
            for field in restricted_fields:
                if field in data:
                    del data[field]
        
        # Update user
        user_model.update_user(user_id, data)
        
        return success_response({}, "User updated successfully")
        
    except Exception as e:
        return error_response(str(e), 500)

@user_bp.route('/<user_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_user(user_id):
    """Deactivate user account (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check admin permissions
        if not check_admin_permission(current_user_id):
            return error_response("Admin access required", 403)
        
        # Cannot deactivate yourself
        if current_user_id == user_id:
            return error_response("Cannot deactivate your own account", 400)
        
        # Check if user exists
        user = user_model.find_by_id(user_id)
        if not user:
            return error_response("User not found", 404)
        
        # Deactivate user
        user_model.deactivate_user(user_id)
        
        return success_response({}, "User deactivated successfully")
        
    except Exception as e:
        return error_response(str(e), 500)

@user_bp.route('/<user_id>/activate', methods=['POST'])
@jwt_required()
def activate_user(user_id):
    """Activate user account (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check admin permissions
        if not check_admin_permission(current_user_id):
            return error_response("Admin access required", 403)
        
        # Check if user exists
        user = user_model.find_by_id(user_id)
        if not user:
            return error_response("User not found", 404)
        
        # Activate user
        user_model.activate_user(user_id)
        
        return success_response({}, "User activated successfully")
        
    except Exception as e:
        return error_response(str(e), 500)

@user_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_user_roles():
    """Get available user roles"""
    try:
        from config.constants import USER_ROLES
        
        return success_response(USER_ROLES, "User roles retrieved successfully")
        
    except Exception as e:
        return error_response(str(e), 500)

@user_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_user_permissions():
    """Get available user permissions"""
    try:
        from config.constants import PERMISSIONS
        
        return success_response(PERMISSIONS, "User permissions retrieved successfully")
        
    except Exception as e:
        return error_response(str(e), 500)
