# tests/test_projects.py
import pytest
from app.models.project import Project
from app.models.user import User
from app import db
import os
from werkzeug.security import generate_password_hash
from flask import url_for, session as flask_session
from datetime import datetime, timedelta

def test_projects_page_unauthenticated(client):
    """Accessing projects requires login and should redirect."""
    response = client.get('/projects/')
    assert response.status_code == 302  # Expect redirect
    assert '/auth/login' in response.headers['Location']  # Should redirect to login page

def test_projects_page_authenticated(client, auth, test_user):
    """Accessing projects works when logged in."""
    # Login using the specific user created for this test
    auth.login(email=test_user.email)
    response = client.get('/projects/')
    assert response.status_code == 200
    # Update this assertion to match your actual template content
    assert b'My Projects' in response.data

def test_create_project(client, auth, test_user, session):
    """Test creating a new project."""
    # Login using the specific user created for this test
    auth.login(email=test_user.email)
    response = client.post('/projects/new', data=dict(
        name='My Test Project',
        description='A project created during testing.',
        project_type='residential',
        location='Test Location',
        size_sqm='1000'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Project created successfully' in response.data
    assert b'My Test Project' in response.data

    # Check database
    project = Project.query.filter_by(name='My Test Project', user_id=test_user.id).first()
    assert project is not None
    assert project.location == 'Test Location'


@pytest.fixture(scope='function')
def other_user(session):
    print("     -> Creating other user object...")
    user = User(
        name='Other User',
        email=f'other_{os.urandom(4).hex()}@example.com',
        password_hash=generate_password_hash('password')
    )
    session.add(user)
    session.flush()
    print(f"     <- Other user object flushed (ID: {user.id}).")
    return user


from flask import url_for

def test_edit_project_unauthorized(client, auth, other_user, test_project):
    """Test that a user cannot edit another user's project."""
    auth.login(email=other_user.email)
    edit_url = f'/projects/{test_project.id}/edit'
    print(f"Attempting GET on: {edit_url} as other_user")

    response_get = client.get(edit_url, follow_redirects=False)
    print(f"GET response status: {response_get.status_code}")
    # --- RE-APPLY ASSERTION FIX ---
    assert response_get.status_code == 302 # Expect redirect
    # Check redirect location
    assert url_for('projects.index') in response_get.headers.get('Location', '') or \
           url_for('main.index') in response_get.headers.get('Location', '')
    # --- END FIX ---

    print(f"Attempting POST on: {edit_url} as other_user")
    response_post = client.post(edit_url, data={'name': 'Hacked Name'}, follow_redirects=False)
    print(f"POST response status: {response_post.status_code}")
    # --- RE-APPLY ASSERTION FIX ---
    assert response_post.status_code == 302 # Expect redirect
    # Check redirect location
    assert url_for('projects.index') in response_post.headers.get('Location', '') or \
           url_for('main.index') in response_post.headers.get('Location', '')
    # --- END FIX ---


def test_view_nonexistent_project(client, auth, test_user):
    """Test viewing a project that doesn't exist."""
    auth.login(email=test_user.email)
    response = client.get('/projects/99999') # Use an ID that won't exist
    assert response.status_code == 404 # Check for Not Found


@pytest.mark.parametrize("field_to_miss,expected_message", [
    ("name", b"Project name is required"),
    ("project_type", b"Project type is required"),
    ("location", b"Location is required"),
    ("size_sqm", b"Size is required"),
])
def test_create_project_missing_required_fields(client, auth, test_user, field_to_miss, expected_message):
    """Test creating a project with missing required fields."""
    auth.login(email=test_user.email)
    data = {
        'name': 'Valid Name',
        'description': 'Valid Description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '1000'
    }
    del data[field_to_miss]
    
    # Don't follow redirects to check the form re-render
    response = client.post('/projects/new', data=data, follow_redirects=False)
    assert response.status_code == 200  # Form re-rendered with errors
    
    # Check for form validation errors in the response
    assert expected_message in response.data
    
    # Verify no project was created
    project = Project.query.filter_by(name='Valid Name', user_id=test_user.id).first()
    assert project is None

@pytest.mark.parametrize("field,invalid_value,expected_message", [
    ("size_sqm", "not_a_number", b"Not a valid float value"),
    ("size_sqm", "-100", b"Size must be a positive number"),
    ("size_sqm", "0", b"Size must be a positive number"),
    ("size_sqm", "2000000", b"Size must be less than 1,000,000 sq meters"),
    ("name", "a" * 101, b"Project name must be less than 100 characters"),
    ("description", "a" * 501, b"Description must be less than 500 characters"),
    ("location", "a" * 256, b"Location must be less than 255 characters"),
    ("project_type", "invalid_type", b"Not a valid choice"),
    ("start_date", "invalid-date", b"Not a valid date value"),
    ("end_date", "invalid-date", b"Not a valid date value"),
    ("end_date", "2020-01-01", b"End date must be after start date"),
    ("budget", "not_a_number", b"Not a valid float value"),
    ("budget", "-5000", b"Budget must be a positive number"),
    ("sector", "invalid_sector", b"Not a valid choice"),
    ("budget", "1000000000", b"Budget must be less than 1,000,000,000"),
    ("start_date", "2030-01-01", b"Start date cannot be in the future"),
    ("end_date", "2029-01-02", b"End date cannot be more than 5 years from start date"),
])
def test_create_project_invalid_field_values(client, auth, test_user, field, invalid_value, expected_message):
    """Test creating a project with invalid field values."""
    auth.login(email=test_user.email)
    data = {
        'name': 'Valid Name',
        'description': 'Valid Description',
        'project_type': 'residential',
        'location': 'Test Location',
        'size_sqm': '1000',
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'budget': '50000',
        'sector': 'healthcare',
    }
    data[field] = invalid_value

    response = client.post('/projects/new', data=data, follow_redirects=False)
    assert response.status_code == 200
    assert expected_message in response.data

@pytest.mark.parametrize("status,expected_message", [
    ('planning', b'Project status updated to planning'),
    ('in_progress', b'Project status updated to in progress'),
    ('completed', b'Project status updated to completed'),
    ('on_hold', b'Project status updated to on hold'),
    ('cancelled', b'Project status updated to cancelled')
])
def test_project_status_transitions(client, auth, test_user, test_project, status, expected_message):
    """Test project status transitions."""
    auth.login(email=test_user.email)
    response = client.post(f'/projects/{test_project.id}/status', data={'status': status}, follow_redirects=True)
    assert response.status_code == 200
    assert expected_message in response.data


def test_project_pagination(client, auth, test_user, session):
    """Test project pagination."""
    auth.login(email=test_user.email)
    
    # Create 15 projects (more than default page size)
    for i in range(15):
        project = Project(
            name=f'Project {i}',
            user_id=test_user.id,
            project_type='residential'
        )
        session.add(project)
    session.commit()
    
    # Test first page
    response = client.get('/projects/')
    assert response.status_code == 200
    assert b'Project 0' in response.data
    assert b'Project 14' not in response.data
    
    # Test second page
    response = client.get('/projects/?page=2')
    assert response.status_code == 200
    assert b'Project 0' not in response.data
    assert b'Project 14' in response.data

def test_project_export_csv(client, auth, test_user, test_project):
    """Test project CSV export functionality."""
    auth.login(email=test_user.email)
    response = client.get(f'/projects/{test_project.id}/export?format=csv')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'Project Name,Description,Type,Location' in response.data


@pytest.mark.skip(reason="PDF export requires WeasyPrint system libraries not available in CI")
def test_project_export_pdf(client, auth, test_user, test_project):
    """Test project PDF export functionality."""
    auth.login(email=test_user.email)
    response = client.get(f'/projects/{test_project.id}/export?format=pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_project_duplicate(client, auth, test_user, test_project, session):
    """Test project duplication functionality."""
    auth.login(email=test_user.email)
    
    # Duplicate the project
    response = client.post(f'/projects/{test_project.id}/duplicate', follow_redirects=True)
    assert response.status_code == 200
    assert b'Project duplicated successfully' in response.data
    
    # Check that a new project was created with the same data
    duplicated_project = Project.query.filter(
        Project.name == f'Copy of {test_project.name}',
        Project.user_id == test_user.id
    ).first()
    assert duplicated_project is not None
    assert duplicated_project.description == test_project.description
    assert duplicated_project.project_type == test_project.project_type
    assert duplicated_project.location == test_project.location
    assert duplicated_project.size_sqm == test_project.size_sqm

def test_view_other_user_project(client, auth, other_user, test_project):
    """Test that a user cannot view another user's project."""
    auth.login(email=other_user.email)
    response = client.get(f'/projects/{test_project.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'You do not have permission to access this page.' in response.data


def test_edit_project_get(client, auth, test_user, test_project):
    """Test loading the edit project page."""
    auth.login(email=test_user.email)
    response = client.get(f'/projects/{test_project.id}/edit')
    assert response.status_code == 200
    # Check that the form is pre-filled with existing project data
    assert bytes(test_project.name, 'utf-8') in response.data
    if test_project.location:
        assert bytes(test_project.location, 'utf-8') in response.data


def test_edit_project_post(client, auth, test_user, test_project, session):
    """Test submitting changes to a project."""
    auth.login(email=test_user.email)
    edit_url = f'/projects/{test_project.id}/edit'
    new_data = {
        'name': 'Updated Project Name',
        'description': 'Updated description.',
        'project_type': 'commercial',
        'location': 'New Location',
        'size_sqm': '1500',
        'start_date': '2023-02-01',
        'end_date': '2023-12-15',
        'budget': '75000',
        'sector': 'healthcare'
    }
    response = client.post(edit_url, data=new_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Project updated successfully' in response.data
    assert b'Updated Project Name' in response.data

    # Check database
    updated_project = session.get(Project, test_project.id)
    assert updated_project.name == 'Updated Project Name'
    assert updated_project.location == 'New Location'
    assert updated_project.size_sqm == 1500.0
    assert updated_project.budget == 75000.0
    assert updated_project.sector == 'healthcare'


def test_delete_project(client, auth, test_user, test_project, session):
    """Test deleting a project."""
    auth.login(email=test_user.email)
    project_id_to_delete = test_project.id
    delete_url = f'/projects/{project_id_to_delete}/delete'

    response_post = client.post(delete_url) # No redirect follow needed if checking session

    # Check redirect
    assert response_post.status_code == 302
    assert url_for('projects.index') in response_post.headers['Location']

    # Check flash message in session
    with client.session_transaction() as flask_sess:
        assert '_flashes' in flask_sess
        flashed_messages = dict(flask_sess['_flashes'])
        print(f"Flashes after delete: {flashed_messages}")
        assert flashed_messages.get('success') == 'Project deleted successfully'

    # Check database
    deleted_project = session.get(Project, project_id_to_delete)
    assert deleted_project is None

def test_create_project_with_all_fields(client, auth, test_user, session):
    """Test creating a new project with all possible fields."""
    auth.login(email=test_user.email)
    response = client.post('/projects/new', data=dict(
        name='Comprehensive Project',
        description='A project with all fields filled in',
        project_type='commercial',
        location='Full Test Location',
        size_sqm='2500',
        start_date='2023-01-15',
        end_date='2024-06-30',
        budget='120000',
        sector='education'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Project created successfully' in response.data
    assert b'Comprehensive Project' in response.data

    # Check database
    project = Project.query.filter_by(name='Comprehensive Project', user_id=test_user.id).first()
    assert project is not None
    assert project.location == 'Full Test Location'
    assert project.size_sqm == 2500.0
    assert project.start_date is not None
    assert project.end_date is not None
    assert project.budget == 120000.0
    assert project.sector == 'education'

def test_project_validation_model_level(session, test_user):
    """Test that model-level validation works properly."""
    # Test size_sqm validation
    with pytest.raises(ValueError, match="Size must be a positive number"):
        project = Project(
            name='Test Validation',
            user_id=test_user.id,
            size_sqm=-100
        )
        session.add(project)
        session.flush()
    
    with pytest.raises(ValueError, match="Size must be less than 1,000,000 sq meters"):
        project = Project(
            name='Test Validation',
            user_id=test_user.id,
            size_sqm=2000000
        )
        session.add(project)
        session.flush()
    
    # Successful case
    project = Project(
        name='Valid Project',
        user_id=test_user.id,
        size_sqm=500
    )
    session.add(project)
    session.flush()
    assert project.id is not None

def test_project_filtering(client, auth, test_user, session):
    """Test project filtering functionality."""
    auth.login(email=test_user.email)
    
    # Create projects with different attributes
    projects = [
        Project(
            name='Project A',
            user_id=test_user.id,
            project_type='residential',
            status='planning',
            budget=100000
        ),
        Project(
            name='Project B',
            user_id=test_user.id,
            project_type='commercial',
            status='in_progress',
            budget=200000
        ),
        Project(
            name='Project C',
            user_id=test_user.id,
            project_type='mixed_use',
            status='completed',
            budget=300000
        )
    ]
    for project in projects:
        session.add(project)
    session.commit()
    
    # Test filtering by project type
    response = client.get('/projects/?type=residential')
    assert response.status_code == 200
    assert b'Project A' in response.data
    assert b'Project B' not in response.data
    assert b'Project C' not in response.data
    
    # Test filtering by status
    response = client.get('/projects/?status=in_progress')
    assert response.status_code == 200
    assert b'Project A' not in response.data
    assert b'Project B' in response.data
    assert b'Project C' not in response.data
    
    # Test filtering by budget range
    response = client.get('/projects/?min_budget=150000&max_budget=250000')
    assert response.status_code == 200
    assert b'Project A' not in response.data
    assert b'Project B' in response.data
    assert b'Project C' not in response.data

def test_project_sorting(client, auth, test_user, session):
    """Test project sorting functionality."""
    auth.login(email=test_user.email)
    
    # Create projects with different names and budgets
    projects = [
        Project(
            name='Zebra Project',
            user_id=test_user.id,
            budget=300000,
            created_at=datetime.utcnow() - timedelta(days=3)
        ),
        Project(
            name='Alpha Project',
            user_id=test_user.id,
            budget=100000,
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
        Project(
            name='Beta Project',
            user_id=test_user.id,
            budget=200000,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
    ]
    for project in projects:
        session.add(project)
    session.commit()
    
    # Test sorting by name (ascending)
    response = client.get('/projects/?sort=name&order=asc')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert data.find('Alpha Project') < data.find('Beta Project') < data.find('Zebra Project')
    
    # Test sorting by name (descending)
    response = client.get('/projects/?sort=name&order=desc')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert data.find('Zebra Project') < data.find('Beta Project') < data.find('Alpha Project')
    
    # Test sorting by budget (ascending)
    response = client.get('/projects/?sort=budget&order=asc')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert data.find('Alpha Project') < data.find('Beta Project') < data.find('Zebra Project')
    
    # Test sorting by creation date (newest first)
    response = client.get('/projects/?sort=created_at&order=desc')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert data.find('Alpha Project') < data.find('Beta Project') < data.find('Zebra Project')