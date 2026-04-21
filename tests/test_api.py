# tests/test_api.py (Example structure)
import pytest
from app.models import User, Project, Assessment, SdgScore, QuestionResponse
from datetime import datetime
import json
from werkzeug.security import generate_password_hash
import uuid  # Add uuid import

@pytest.fixture
def test_user_api(session):
    """Create a test user for API testing."""
    from app.models import User
    from werkzeug.security import generate_password_hash

    # Generate a unique email for each test run for this fixture
    unique_email = f"api_test_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash=generate_password_hash('password123'),
        name='API Test User'
    )
    session.add(user)
    session.flush()  # Get ID, will be rolled back by function-scoped session fixture
    # Store the plain password with the user object for the api_auth_token fixture to use
    user.plain_password = 'password123'
    return user

@pytest.fixture
def api_auth_token(client, test_user_api):
    """Get an authentication token for API testing."""
    login_payload = {
        'email': test_user_api.email,  # Use the unique email
        'password': test_user_api.plain_password  # Use the stored plain password
    }
    response = client.post('/api/auth/login', json=login_payload)  # This route uses ORM now
    if response.status_code != 200:
        pytest.fail(f"API Login failed: {response.status_code} - {response.text}")
    data = response.get_json()
    assert 'token' in data
    return data['token']

@pytest.fixture
def test_project_api(session, test_user_api):
    """Create a test project for API testing."""
    from app.models import Project  # Ensure Project is imported
    from datetime import datetime  # Ensure datetime is imported

    project = Project(
        name='Test Project',  # For test_update_project, this name is updated
        description='Test Description',
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        budget=100000.0,
        location='Test Location',
        sector='Technology',  # Initial sector for test_update_project
        project_type='commercial',  # If you have both
        user_id=test_user_api.id
    )
    session.add(project)
    session.flush()
    return project

def test_get_projects(client, api_auth_token, test_user_api, test_project_api):
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    response = client.get('/api/projects', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['name'] == 'Test Project'
    assert data[0]['location'] == 'Test Location'

def test_get_project(client, api_auth_token, test_user_api, test_project_api):
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    response = client.get(f'/api/projects/{test_project_api.id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Test Project'
    assert data['location'] == 'Test Location'

def test_create_project(client, api_auth_token, test_user_api, session):
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    project_data = {
        'name': 'New API Project',
        'description': 'New Description',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'budget': 200000.0,
        'location': 'New Location',
        'sector': 'New Sector'
        # user_id is derived from token by @token_required
    }
    response = client.post('/api/projects', json=project_data, headers=headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'New API Project'
    assert data['description'] == 'New Description'
    assert data['location'] == 'New Location'
    assert data['sector'] == 'New Sector'

def test_update_project(client, api_auth_token, test_user_api, test_project_api):
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    project_data = {
        'name': 'Updated API Project',
        'description': 'Updated Description',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'budget': 300000.0,
        'location': 'Updated Location',
        'sector': 'Updated Sector'
    }
    response = client.put(f'/api/projects/{test_project_api.id}', 
                         json=project_data,
                         headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Updated API Project'
    assert data['description'] == 'Updated Description'
    assert data['location'] == 'Updated Location'
    assert data['sector'] == 'Updated Sector'

def test_delete_project(client, api_auth_token, test_user_api, test_project_api, session):
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    response = client.delete(f'/api/projects/{test_project_api.id}', headers=headers)
    assert response.status_code == 204
    assert session.get(Project, test_project_api.id) is None

def test_get_assessments(client, api_auth_token, test_user_api, test_project_api, session):
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    # Create an assessment for the project
    assessment = Assessment(
        project_id=test_project_api.id,
        user_id=test_user_api.id
    )
    session.add(assessment)
    session.commit()  # Commit so API can see it via get_db()

    # This endpoint GETs the project and its assessments
    response = client.get(f'/api/projects/{test_project_api.id}', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify project details
    assert data['id'] == test_project_api.id
    assert data['name'] == 'Test Project'
    
    # Verify assessments list
    assert 'assessments' in data
    assert len(data['assessments']) == 1
    assert data['assessments'][0]['id'] == assessment.id
    assert data['assessments'][0]['project_id'] == test_project_api.id
    assert data['assessments'][0]['user_id'] == test_user_api.id

def test_get_assessment(client, api_auth_token, test_user_api, test_project_api, session):
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    assessment = Assessment(
        project_id=test_project_api.id,
        user_id=test_user_api.id
    )
    session.add(assessment)
    session.flush()
    
    response = client.get(f'/api/assessments/{assessment.id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == assessment.id

def test_create_assessment(client, api_auth_token, test_user_api, test_project_api):
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    assessment_data = {
        'project_id': test_project_api.id
        # user_id is derived from token by @token_required
    }
    response = client.post(f'/api/projects/{test_project_api.id}/assessments', 
                         json=assessment_data,
                         headers=headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['project_id'] == test_project_api.id
    assert data['user_id'] == test_user_api.id

def test_update_assessment(client, api_auth_token, test_user_api, test_project_api, session):
    """Test updating an assessment via PUT."""
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    
    # Create an assessment for testing
    assessment = Assessment(
        project_id=test_project_api.id,
        user_id=test_user_api.id,
        status='draft'
    )
    session.add(assessment)
    session.flush()
    
    # Test updating status
    update_data = {
        'status': 'in_progress',
        'draft_data': {
            'step': 2,
            'answers': {'q1': 'answer1'}
        }
    }
    
    response = client.put(
        f'/api/assessments/{assessment.id}',
        json=update_data,
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify the response
    assert data['id'] == assessment.id
    assert data['status'] == 'in_progress'
    
    # Parse the returned JSON string for draft_data
    if data.get('draft_data') is not None:
        returned_draft_data = json.loads(data['draft_data'])
        assert returned_draft_data == update_data['draft_data']
    else:
        assert update_data.get('draft_data') is None
    
    assert 'updated_at' in data
    
    # Verify the database was updated
    updated_assessment = session.get(Assessment, assessment.id)
    assert updated_assessment.status == 'in_progress'
    
    # Compare dictionaries after parsing both JSON strings from DB and expected
    db_draft_data_dict = json.loads(updated_assessment.draft_data)
    expected_draft_data_dict = update_data['draft_data']
    assert db_draft_data_dict == expected_draft_data_dict

def test_delete_assessment(client, api_auth_token, test_user_api, test_project_api, session):
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    # Create an assessment for the project
    assessment = Assessment(
        project_id=test_project_api.id,
        user_id=test_user_api.id
    )
    session.add(assessment)
    session.commit()
    
    # Create some related data that should be deleted
    # Add an SDG score
    score = SdgScore(
        assessment_id=assessment.id,
        sdg_id=1,  # Assuming SDG 1 exists
        total_score=5.0
    )
    session.add(score)
    
    # Add a question response
    qr = QuestionResponse(
        assessment_id=assessment.id,
        question_id=1,  # Assuming question 1 exists
        response_text='Test response'
    )
    session.add(qr)
    session.commit()
    
    # Delete the assessment
    delete_response = client.delete(f'/api/assessments/{assessment.id}', headers=headers)
    assert delete_response.status_code == 204
    
    # Verify the assessment and related data are deleted
    assert session.get(Assessment, assessment.id) is None
    assert SdgScore.query.filter_by(assessment_id=assessment.id).first() is None
    assert QuestionResponse.query.filter_by(assessment_id=assessment.id).first() is None

def test_assessment_not_found(client, api_auth_token, test_user_api):
    """Test that accessing a non-existent assessment returns 404."""
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    response = client.get('/api/assessments/99999', headers=headers)
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Assessment not found or access denied'

def test_assessment_access_denied(client, api_auth_token, test_user_api, session):
    """Test that accessing another user's assessment returns 404."""
    headers = {'Authorization': f'Bearer {api_auth_token}'}
    
    # Create another user with unique email
    other_user_email = f"other_user_api_{uuid.uuid4().hex[:8]}@example.com"
    other_user = User(
        email=other_user_email,
        password_hash=generate_password_hash('password123'),
        name='Other User API'
    )
    session.add(other_user)
    session.flush()  # Ensure user has an ID before creating project
    
    # Create a project for the other user
    other_project = Project(
        name='Other Project',
        user_id=other_user.id
    )
    session.add(other_project)
    session.flush()  # Ensure project has an ID before creating assessment
    
    # Create an assessment for the other user's project
    other_assessment = Assessment(
        project_id=other_project.id,
        user_id=other_user.id
    )
    session.add(other_assessment)
    session.commit()
    
    # Try to access the other user's assessment
    response = client.get(f'/api/assessments/{other_assessment.id}', headers=headers)
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Assessment not found or access denied'

def test_unauthorized_access(client, test_project_api):
    """Test that API endpoints require authentication."""
    # Try to access endpoints without auth headers
    response = client.get('/api/projects')
    assert response.status_code == 401
    
    response = client.get(f'/api/projects/{test_project_api.id}')
    assert response.status_code == 401
    
    response = client.post('/api/projects', json={})
    assert response.status_code == 401

def test_invalid_token(client, test_project_api):
    """Test that invalid tokens are rejected."""
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.get('/api/projects', headers=headers)
    assert response.status_code == 401

# Add tests for POST, PUT, DELETE API endpoints, invalid tokens, etc.