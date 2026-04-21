"""
Validation utilities.
Input validation and sanitization functions.
"""

import re
import json
from flask import request

def sanitize_input(value):
    """
    Sanitize user input by removing potentially dangerous characters.
    """
    if value is None:
        return None
    
    # Convert to string if not already
    value = str(value)
    
    # Remove any script tags
    value = re.sub(r'<script.*?>.*?</script>', '', value, flags=re.DOTALL)
    
    # Replace any HTML tags with spaces
    value = re.sub(r'<[^>]*>', ' ', value)
    
    # Remove control characters
    value = re.sub(r'[\x00-\x1F\x7F]', '', value)
    
    # Replace multiple spaces with a single space
    value = re.sub(r'\s+', ' ', value)
    
    # Trim whitespace
    value = value.strip()
    
    return value

def validate_email(email):
    """
    Validate email format.
    """
    if not email:
        return False
    
    # Simple regex for basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validate password strength.
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    return True, ""

def validate_project_data(data):
    """
    Validate project form data.
    Returns a list of error messages, empty if valid.
    """
    errors = []
    
    # Required fields
    if not data.get('name'):
        errors.append('Project name is required')
    
    # Length validations
    if data.get('name') and len(data['name']) > 100:
        errors.append('Project name must be less than 100 characters')
    
    if data.get('description') and len(data['description']) > 500:
        errors.append('Description must be less than 500 characters')
    
    # Size validation
    if data.get('size_sqm'):
        try:
            size = float(data['size_sqm'])
            if size <= 0 or size > 1000000:  # 1 million sq meters as upper limit
                errors.append('Size must be a positive number less than 1,000,000 sq meters')
        except ValueError:
            errors.append('Size must be a valid number')
    
    return errors

def validate_assessment_response(question_type, value, options=None):
    """
    Validate an assessment question response.
    Returns (is_valid, error_message) tuple.
    """
    if question_type == 'select':
        # For select/radio questions, value should be a number 1-5
        try:
            score = int(value)
            if score < 0 or score > 5:
                return False, "Score must be between 0 and 5"
        except (ValueError, TypeError):
            return False, "Score must be a number"
    
    elif question_type == 'checklist':
        # For checklist questions, value should be a list of selected options
        try:
            selected = json.loads(value) if isinstance(value, str) else value
            if not isinstance(selected, list):
                return False, "Selected options must be a list"
            
            if options:
                # If options are provided, validate that selections are valid
                valid_keys = []
                for opt in options:
                    if isinstance(opt, dict):
                        valid_keys.append(opt.get('key', opt.get('text')))
                    elif isinstance(opt, str):
                        valid_keys.append(opt)
                
                for selection in selected:
                    if selection not in valid_keys:
                        return False, f"Invalid selection: {selection}"
        except json.JSONDecodeError:
            return False, "Invalid JSON format for selected options"
    
    # For other question types, no specific validation
    
    return True, ""

def validate_request_form():
    """
    Validate and sanitize all form fields in the current request.
    Returns a dictionary of sanitized form data.
    """
    if request.method != 'POST':
        return {}
    
    sanitized = {}
    for key, value in request.form.items():
        sanitized[key] = sanitize_input(value)
    
    return sanitized

def validate_sdg_data(data):
    """
    Validate SDG form data.
    Returns a list of error messages, empty if valid.
    """
    errors = []
    
    # Required fields
    if not data.get('name'):
        errors.append('SDG name is required')
    
    if not data.get('number'):
        errors.append('SDG number is required')
    else:
        try:
            number = int(data['number'])
            if number < 1 or number > 17:
                errors.append('SDG number must be between 1 and 17')
        except ValueError:
            errors.append('SDG number must be a valid integer')
    
    # Color code validation
    if data.get('color_code'):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', data['color_code']):
            errors.append('Color code must be a valid hex color (e.g., #FF5733)')
    
    return errors

def validate_question_data(data):
    """
    Validate question form data.
    Returns a list of error messages, empty if valid.
    """
    errors = []
    
    # Required fields
    if not data.get('question_text'):
        errors.append('Question text is required')
    
    if not data.get('primary_sdg_id'):
        errors.append('Primary SDG is required')
    
    if not data.get('question_type'):
        errors.append('Question type is required')
    elif data['question_type'] not in ['select', 'checklist', 'text']:
        errors.append('Invalid question type')
    
    # Options validation for checklists
    if data.get('question_type') == 'checklist' and data.get('options'):
        try:
            options = json.loads(data['options']) if isinstance(data['options'], str) else data['options']
            if not isinstance(options, list):
                errors.append('Options must be a list')
            else:
                for option in options:
                    if not isinstance(option, dict) or 'text' not in option:
                        errors.append('Each option must be an object with at least a "text" property')
        except json.JSONDecodeError:
            errors.append('Options must be valid JSON')
    
    # Max score validation
    if data.get('max_score'):
        try:
            max_score = float(data['max_score'])
            if max_score <= 0:
                errors.append('Max score must be a positive number')
        except ValueError:
            errors.append('Max score must be a valid number')
    
    return errors
