import pytest
from flask import Flask
from app.forms.project_forms import ProjectForm, DateAfterValidator
from app import db
from wtforms import Form, DateField, StringField
from wtforms.validators import ValidationError
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-key'
    return app

def test_project_form_valid(app):
    """Test project form validation with valid data."""
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '1000'
    }):
        form = ProjectForm()
        assert form.validate() is True
        assert len(form.errors) == 0

def test_project_form_missing_required_fields(app):
    """Test project form validation with missing required fields."""
    # Test missing name
    with app.test_request_context('/fake', method='POST', data={
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '1000'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'name' in form.errors
        assert 'Project name is required' in form.errors['name']

    # Test missing project_type
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'location': 'Test Location',
        'size_sqm': '1000'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'project_type' in form.errors
        assert 'Project type is required' in form.errors['project_type']

def test_project_form_name_length(app):
    """Test project form validation for name length."""
    with app.test_request_context('/fake', method='POST', data={
        'name': 'a' * 101,  # 101 characters
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '1000'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'name' in form.errors
        assert 'Project name must be less than 100 characters' in form.errors['name']

def test_project_form_description_length(app):
    """Test project form validation for description length."""
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'a' * 501,  # 501 characters
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '1000'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'description' in form.errors
        assert 'Description must be less than 500 characters' in form.errors['description']

def test_project_form_size_validation(app):
    """Test size field validation in ProjectForm."""

    # Test valid size
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '1000'
    }):
        form = ProjectForm()
        assert form.validate() is True
        assert 'size_sqm' not in form.errors

    # Test non-numeric value
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': 'not_a_number'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'size_sqm' in form.errors
        assert 'Not a valid float value' in form.errors['size_sqm'][0]

    # Test negative value
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '-100'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'size_sqm' in form.errors
        assert 'Size must be a positive number' in str(form.errors['size_sqm'])

    # Test zero value
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '0'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'size_sqm' in form.errors
        assert 'Size must be a positive number' in str(form.errors['size_sqm'])

    # Test value exceeding maximum
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '2000000'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'size_sqm' in form.errors
        assert 'Size must be less than 1,000,000 sq meters' in str(form.errors['size_sqm'])

    # Test empty value (size_sqm is now required)
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': ''
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'size_sqm' in form.errors
        assert 'Size is required' in str(form.errors['size_sqm'])

def test_project_form_project_type_validation(app):
    """Test project form validation for project type field."""
    valid_types = [
        'residential', 'commercial', 'mixed_use', 'public', 'educational',
        'healthcare', 'industrial', 'infrastructure', 'landscape',
        'urban_planning', 'other'
    ]
    
    # Test each valid project type
    for project_type in valid_types:
        with app.test_request_context('/fake', method='POST', data={
            'name': 'Test Project',
            'description': 'A test project description',
            'project_type': project_type,
            'location': 'Test Location',
            'size_sqm': '1000'
        }):
            form = ProjectForm()
            assert form.validate() is True
            assert 'project_type' not in form.errors
    
    # Test invalid project type
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'invalid_type',
        'location': 'Test Location',
        'size_sqm': '1000'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'project_type' in form.errors
        # Print actual error message for debugging
        print(repr(form.errors['project_type']))
        # Use equality assertion to match the exact error message
        assert form.errors['project_type'] == ['Not a valid choice.']

def test_project_form_location_validation(app):
    """Test project form validation for location field."""
    # Test location with special characters
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'Test Location, 12345!@#$%^&*()',
        'size_sqm': '1000'
    }):
        form = ProjectForm()
        assert form.validate() is True
        assert 'location' not in form.errors

    # Test location too long
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'A test project description',
        'project_type': 'residential',
        'location': 'a' * 256,  # 256 characters
        'size_sqm': '1000'
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'location' in form.errors
        assert 'Location must be less than 255 characters' in form.errors['location']

def test_project_form_empty_values(app):
    """Test project form validation with empty values."""
    with app.test_request_context('/fake', method='POST', data={
        'name': '',
        'description': '',
        'project_type': '',
        'location': '',
        'size_sqm': ''
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'name' in form.errors
        assert 'Project name is required' in form.errors['name']
        assert 'project_type' in form.errors
        assert 'Project type is required' in form.errors['project_type']
        assert 'size_sqm' in form.errors
        assert 'Size is required' in str(form.errors['size_sqm'])

# Test for DateAfterValidator
def test_date_after_validator():
    """Test the DateAfterValidator works correctly."""
    # Create a test form with start_date and end_date fields
    class TestForm(Form):
        start_date = DateField('Start Date')
        end_date = DateField('End Date', validators=[DateAfterValidator('start_date')])
    
    # Test when end_date is after start_date (valid)
    form = TestForm()
    form.start_date.data = datetime.now().date()
    form.end_date.data = (datetime.now() + timedelta(days=10)).date()
    assert form.validate() is True
    
    # Test when end_date is the same as start_date (invalid)
    form = TestForm()
    today = datetime.now().date()
    form.start_date.data = today
    form.end_date.data = today
    assert form.validate() is False
    assert "End date must be after start date" in form.end_date.errors
    
    # Test when end_date is before start_date (invalid)
    form = TestForm()
    form.start_date.data = datetime.now().date()
    form.end_date.data = (datetime.now() - timedelta(days=10)).date()
    assert form.validate() is False
    assert "End date must be after start date" in form.end_date.errors
    
    # Test with custom message
    class TestFormCustomMessage(Form):
        start_date = DateField('Start Date')
        end_date = DateField('End Date', validators=[DateAfterValidator('start_date', message="Custom message")])
    
    form = TestFormCustomMessage()
    form.start_date.data = datetime.now().date()
    form.end_date.data = (datetime.now() - timedelta(days=10)).date()
    assert form.validate() is False
    assert "Custom message" in form.end_date.errors
    
    # Test with missing referenced field — validator flags it as an error
    class TestFormBadField(Form):
        end_date = DateField('End Date', validators=[DateAfterValidator('non_existent_field')])

    form = TestFormBadField()
    form.end_date.data = datetime.now().date()
    result = form.validate()
    assert result is False
    assert "non_existent_field" in form.end_date.errors[0]

# Test ProjectForm validation
def test_project_form_validation(app):
    """Test that ProjectForm validates data correctly."""
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'description': 'Description',
        'project_type': 'residential',
        'location': 'Test location',
        'size_sqm': '1000',
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'budget': '50000',
        'sector': 'technology',
    }):
        form = ProjectForm()
        assert form.validate() is True

    # Name too long
    with app.test_request_context('/fake', method='POST', data={
        'name': 'T' * 101,
        'project_type': 'residential',
        'location': 'Test location',
        'size_sqm': '1000',
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'Project name must be less than 100 characters' in form.name.errors

    # Negative size
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'project_type': 'residential',
        'location': 'Test location',
        'size_sqm': '-1',
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'Size must be a positive number' in str(form.size_sqm.errors)

    # End date before start date
    with app.test_request_context('/fake', method='POST', data={
        'name': 'Test Project',
        'project_type': 'residential',
        'location': 'Test location',
        'size_sqm': '1000',
        'start_date': '2023-06-01',
        'end_date': '2023-01-01',
    }):
        form = ProjectForm()
        assert form.validate() is False
        assert 'End date must be after start date' in form.end_date.errors 