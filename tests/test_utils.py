# tests/test_utils.py
import pytest
from app.utils.filters import format_datetime, format_date_filter # Example: testing a filter
from datetime import datetime
from app.utils.validation import (
    sanitize_input,
    validate_email,
    validate_password,
    validate_project_data,
    validate_assessment_response,
    validate_request_form,
    validate_sdg_data,
    validate_question_data
)
from flask import request
import json

def test_format_datetime_filter():
    dt = datetime(2024, 5, 1, 14, 30, 0)
    # Test medium format
    assert format_datetime(dt, format='medium') == 'May 01, 2024, 02:30 PM'
    # Test short_date format (should be MM/DD/YY)
    assert format_datetime(dt, format='short_date') == '05/01/24'
    assert format_datetime(None) == ""
    assert format_datetime("invalid string") == "invalid string"

# Add tests for other utils like validation, db helpers etc.

# Test sanitize_input
@pytest.mark.parametrize("input_value,expected", [
    ("normal text", "normal text"),
    ("<script>alert('xss')</script>", ""),  # Script tags and their contents should be removed
    ("<p>HTML</p>", "HTML"),  # HTML tags should be removed, content preserved
    ("  multiple   spaces  ", "multiple spaces"),  # Whitespace should be normalized
    ("\x00control\x1Fchars", "controlchars"),  # Control characters should be removed
    (None, None),  # None should remain None
    (123, "123"),  # Numbers should be converted to strings
])
def test_sanitize_input(input_value, expected):
    """Test input sanitization function."""
    assert sanitize_input(input_value) == expected

# Test validate_email
@pytest.mark.parametrize("email,is_valid", [
    ("user@example.com", True),
    ("invalid.email", False),
    ("no@domain", False),
    ("@nodomain.com", False),
    ("user@.com", False),
    ("", False),
    (None, False),
])
def test_validate_email(email, is_valid):
    """Test email validation function."""
    assert validate_email(email) == is_valid

# Test validate_password
@pytest.mark.parametrize("password,expected", [
    ("ValidPass123", (True, "")),
    ("short", (False, "Password must be at least 8 characters long")),
    ("no_numbers", (False, "Password must contain at least one digit")),
    ("no_uppercase123", (False, "Password must contain at least one uppercase letter")),
    ("NO_LOWERCASE123", (False, "Password must contain at least one lowercase letter")),
    ("", (False, "Password must be at least 8 characters long")),
    (None, (False, "Password must be at least 8 characters long")),
])
def test_validate_password(password, expected):
    """Test password validation function."""
    assert validate_password(password) == expected

# Test validate_project_data
@pytest.mark.parametrize("data,expected_errors", [
    (
        {
            'name': 'Valid Project',
            'description': 'Valid description',
            'size_sqm': '1000'
        },
        []
    ),
    (
        {
            'description': 'Missing name',
            'size_sqm': '1000'
        },
        ['Project name is required']
    ),
    (
        {
            'name': 'a' * 101,  # Too long
            'description': 'Valid description',
            'size_sqm': '1000'
        },
        ['Project name must be less than 100 characters']
    ),
    (
        {
            'name': 'Valid Project',
            'description': 'a' * 501,  # Too long
            'size_sqm': '1000'
        },
        ['Description must be less than 500 characters']
    ),
    (
        {
            'name': 'Valid Project',
            'size_sqm': 'not_a_number'
        },
        ['Size must be a valid number']
    ),
    (
        {
            'name': 'Valid Project',
            'size_sqm': '-100'
        },
        ['Size must be a positive number less than 1,000,000 sq meters']
    ),
])
def test_validate_project_data(data, expected_errors):
    """Test project data validation function."""
    assert validate_project_data(data) == expected_errors

# Test validate_assessment_response
@pytest.mark.parametrize("question_type,value,options,expected", [
    # Select type tests
    ('select', '3', None, (True, "")),
    ('select', '6', None, (False, "Score must be between 0 and 5")),
    ('select', 'not_a_number', None, (False, "Score must be a number")),
    
    # Checklist type tests
    ('checklist', json.dumps(['option1', 'option2']), 
     [{'key': 'option1'}, {'key': 'option2'}], 
     (True, "")),
    ('checklist', json.dumps(['invalid_option']), 
     [{'key': 'option1'}], 
     (False, "Invalid selection: invalid_option")),
    ('checklist', 'invalid_json', None, 
     (False, "Invalid JSON format for selected options")),
    
    # Other type tests
    ('text', 'any value', None, (True, "")),
])
def test_validate_assessment_response(question_type, value, options, expected):
    """Test assessment response validation function."""
    assert validate_assessment_response(question_type, value, options) == expected

# Test validate_sdg_data
@pytest.mark.parametrize("data,expected_errors", [
    (
        {
            'name': 'Valid SDG',
            'number': '1',
            'color_code': '#FF5733'
        },
        []
    ),
    (
        {
            'number': '1',
            'color_code': '#FF5733'
        },
        ['SDG name is required']
    ),
    (
        {
            'name': 'Valid SDG',
            'color_code': '#FF5733'
        },
        ['SDG number is required']
    ),
    (
        {
            'name': 'Valid SDG',
            'number': '18',
            'color_code': '#FF5733'
        },
        ['SDG number must be between 1 and 17']
    ),
    (
        {
            'name': 'Valid SDG',
            'number': '1',
            'color_code': 'invalid_color'
        },
        ['Color code must be a valid hex color (e.g., #FF5733)']
    ),
])
def test_validate_sdg_data(data, expected_errors):
    """Test SDG data validation function."""
    assert validate_sdg_data(data) == expected_errors

# Test validate_question_data
@pytest.mark.parametrize("data,expected_errors", [
    (
        {
            'question_text': 'Valid question?',
            'primary_sdg_id': '1',
            'question_type': 'select',
            'max_score': '5'
        },
        []
    ),
    (
        {
            'primary_sdg_id': '1',
            'question_type': 'select'
        },
        ['Question text is required']
    ),
    (
        {
            'question_text': 'Valid question?',
            'question_type': 'select'
        },
        ['Primary SDG is required']
    ),
    (
        {
            'question_text': 'Valid question?',
            'primary_sdg_id': '1',
            'question_type': 'invalid_type'
        },
        ['Invalid question type']
    ),
    (
        {
            'question_text': 'Valid question?',
            'primary_sdg_id': '1',
            'question_type': 'checklist',
            'options': 'invalid_json'
        },
        ['Options must be valid JSON']
    ),
    (
        {
            'question_text': 'Valid question?',
            'primary_sdg_id': '1',
            'question_type': 'checklist',
            'options': json.dumps([{'invalid': 'option'}])
        },
        ['Each option must be an object with at least a "text" property']
    ),
])
def test_validate_question_data(data, expected_errors):
    """Test question data validation function."""
    assert validate_question_data(data) == expected_errors

# Test datetime formatting functions
@pytest.mark.parametrize("value,format,expected", [
    # Test None value
    (None, 'medium', ""),
    
    # Test string inputs
    ("2024-03-15T14:30:00Z", 'medium', "Mar 15, 2024, 02:30 PM"),
    ("2024-03-15 14:30:00", 'medium', "Mar 15, 2024, 02:30 PM"),
    ("invalid_date", 'medium', "invalid_date"),
    
    # Test datetime object
    (datetime(2024, 3, 15, 14, 30), 'medium', "Mar 15, 2024, 02:30 PM"),
    
    # Test different formats
    (datetime(2024, 3, 15, 14, 30), 'full', "Friday, 15 March 2024 at 02:30:00 PM"),
    (datetime(2024, 3, 15, 14, 30), 'short_date', "03/15/24"),
    (datetime(2024, 3, 15, 14, 30), 'medium_date', "Mar 15, 2024"),
    
    # Test invalid format (should default to medium)
    (datetime(2024, 3, 15, 14, 30), 'invalid_format', "Mar 15, 2024, 02:30 PM"),
])
def test_format_datetime(value, format, expected):
    """Test datetime formatting function."""
    assert format_datetime(value, format) == expected

def test_format_date_filter():
    """Test the date filter function."""
    test_date = datetime(2024, 3, 15, 14, 30)
    assert format_date_filter(test_date) == "Mar 15, 2024"