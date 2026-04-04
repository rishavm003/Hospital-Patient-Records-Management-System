"""
User Model for Hospital Patient Records Management System
Handles authentication, authorization, and user management
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from config.database import db_config

class User:
    """User model class"""
    
    def __init__(self):
        self.collection = db_config.get_collection('users')
    
    def create_user(self, user_data):
        """Create a new user"""
        try:
            # Hash password
            user_data['password'] = generate_password_hash(user_data['password'])
            
            # Add timestamps
            user_data['createdAt'] = datetime.utcnow()
            user_data['updatedAt'] = datetime.utcnow()
            
            # Set default values
            user_data['isActive'] = True
            user_data['loginAttempts'] = 0
            user_data['twoFactorEnabled'] = False
            user_data['activityLog'] = []
            
            result = self.collection.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error creating user: {e}")
    
    def find_by_email(self, email):
        """Find user by email"""
        return self.collection.find_one({'email': email})
    
    def find_by_id(self, user_id):
        """Find user by ID"""
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def verify_password(self, user, password):
        """Verify user password"""
        return check_password_hash(user['password'], password)
    
    def update_last_login(self, user_id):
        """Update user's last login time"""
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'lastLogin': datetime.utcnow()}}
        )
    
    def increment_login_attempts(self, user_id):
        """Increment failed login attempts"""
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$inc': {'loginAttempts': 1}}
        )
    
    def reset_login_attempts(self, user_id):
        """Reset failed login attempts"""
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'loginAttempts': 0}}
        )
    
    def lock_account(self, user_id, lock_duration_minutes=30):
        """Lock user account temporarily"""
        lock_until = datetime.utcnow() + timedelta(minutes=lock_duration_minutes)
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'lockedUntil': lock_until}}
        )
    
    def is_account_locked(self, user):
        """Check if user account is locked"""
        if 'lockedUntil' in user:
            return datetime.utcnow() < user['lockedUntil']
        return False
    
    def update_password(self, user_id, new_password):
        """Update user password"""
        hashed_password = generate_password_hash(new_password)
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'password': hashed_password,
                'passwordChangedAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }}
        )
    
    def set_password_reset_token(self, user_id, token, expires_in_hours=1):
        """Set password reset token"""
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'passwordResetToken': token,
                'passwordResetExpires': expires_at
            }}
        )
    
    def clear_password_reset_token(self, user_id):
        """Clear password reset token"""
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$unset': {
                'passwordResetToken': '',
                'passwordResetExpires': ''
            }}
        )
    
    def log_activity(self, user_id, action, ip_address, user_agent):
        """Log user activity"""
        activity = {
            'action': action,
            'timestamp': datetime.utcnow(),
            'ipAddress': ip_address,
            'userAgent': user_agent
        }
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$push': {'activityLog': activity}}
        )
    
    def get_users_by_role(self, role):
        """Get all users by role"""
        return list(self.collection.find({'role': role}))
    
    def update_user(self, user_id, update_data):
        """Update user information"""
        update_data['updatedAt'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    
    def deactivate_user(self, user_id):
        """Deactivate user account"""
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'isActive': False,
                'updatedAt': datetime.utcnow()
            }}
        )
    
    def activate_user(self, user_id):
        """Activate user account"""
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'isActive': True,
                'updatedAt': datetime.utcnow()
            }}
        )
