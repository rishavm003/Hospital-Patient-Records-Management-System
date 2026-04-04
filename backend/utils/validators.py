"""
Input validation utilities
"""
import re
from datetime import datetime


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> bool:
    return len(password) >= 8


def validate_phone(phone: str) -> bool:
    pattern = r'^\+?[1-9]\d{6,14}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))


def validate_required_fields(data: dict, fields: list) -> list:
    """Return list of missing required fields"""
    missing = []
    for field in fields:
        if not data.get(field):
            missing.append(field)
    return missing


def validate_blood_group(blood_group: str) -> bool:
    valid = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return blood_group in valid


def validate_date(date_str: str) -> bool:
    try:
        datetime.fromisoformat(date_str)
        return True
    except (ValueError, TypeError):
        return False


def sanitize_string(value: str) -> str:
    """Basic XSS sanitization"""
    if not isinstance(value, str):
        return value
    replacements = {'<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;', '/': '&#x2F;'}
    for char, replacement in replacements.items():
        value = value.replace(char, replacement)
    return value.strip()
