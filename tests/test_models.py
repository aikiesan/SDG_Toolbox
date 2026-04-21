import pytest
from datetime import datetime, timedelta
from app.models import User, Project, Assessment
from werkzeug.security import generate_password_hash, check_password_hash

def test_user_creation(test_user, session):
    """Test basic user creation and attributes."""
    assert test_user.id is not None
    assert test_user.name == 'Test User'
    assert test_user.email.startswith('test_')
    assert test_user.email.endswith('@example.com')
    assert test_user.is_admin is False
    assert test_user.password_hash is not None

def test_user_password_hashing(session):
    """Test password hashing and verification."""
    user = User(
        name='Hash Test',
        email='hash@test.com',
        password_hash=generate_password_hash('testpass123')
    )
    session.add(user)
    session.flush()
    
    assert user.password_hash is not None
    assert user.password_hash != 'testpass123'
    assert user.check_password(user.password_hash, 'testpass123')
    assert not user.check_password(user.password_hash, 'wrongpass')

def test_user_projects_relationship(test_user, session):
    """Test user-projects relationship."""
    # Create a project for the user
    project = Project(
        name='Test Project',
        description='A test project',
        project_type='residential',
        user_id=test_user.id
    )
    session.add(project)
    session.flush()
    
    # Test relationship from user side
    assert project in test_user.projects
    assert len(test_user.projects) == 1
    
    # Test relationship from project side
    assert project.user == test_user
    assert project.user_id == test_user.id

def test_project_creation(test_user, session):
    """Test basic project creation and attributes."""
    project = Project(
        name='Test Project',
        description='A test project description',
        project_type='residential',
        location='Test Location',
        size_sqm=1000.0,
        user_id=test_user.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=365)
    )
    session.add(project)
    session.flush()
    
    assert project.id is not None
    assert project.name == 'Test Project'
    assert project.description == 'A test project description'
    assert project.project_type == 'residential'
    assert project.location == 'Test Location'
    assert project.size_sqm == 1000.0
    assert project.user_id == test_user.id
    assert project.created_at is not None
    assert project.updated_at is not None
    assert project.start_date is not None
    assert project.end_date is not None

def test_project_assessments_relationship(test_user, session):
    """Test project-assessments relationship."""
    # Create a project
    project = Project(
        name='Test Project',
        project_type='residential',
        user_id=test_user.id
    )
    session.add(project)
    session.flush()
    
    # Create an assessment for the project
    assessment = Assessment(
        project_id=project.id,
        user_id=test_user.id,
        status='draft'
    )
    session.add(assessment)
    session.flush()
    
    # Test relationship from project side
    assert assessment in project.assessments
    assert len(project.assessments) == 1
    
    # Test relationship from assessment side
    assert assessment.project == project
    assert assessment.project_id == project.id

def test_project_cascade_delete(test_user, session):
    """Test that deleting a project cascades to its assessments."""
    # Create a project with an assessment
    project = Project(
        name='Test Project',
        project_type='residential',
        user_id=test_user.id
    )
    session.add(project)
    session.flush()
    
    assessment = Assessment(
        project_id=project.id,
        user_id=test_user.id,
        status='draft'
    )
    session.add(assessment)
    session.flush()
    
    # Delete the project
    session.delete(project)
    session.flush()
    
    # Check that both project and assessment are deleted
    assert session.query(Project).get(project.id) is None
    assert session.query(Assessment).get(assessment.id) is None

def test_project_updated_at_timestamp(test_user, session):
    """Test that project's updated_at timestamp is updated on changes."""
    project = Project(
        name='Test Project',
        project_type='residential',
        user_id=test_user.id
    )
    session.add(project)
    session.flush()
    
    original_updated_at = project.updated_at
    
    # Wait a moment to ensure timestamp difference
    import time
    time.sleep(1)
    
    # Update the project
    project.name = 'Updated Project Name'
    session.flush()
    
    assert project.updated_at > original_updated_at

def test_user_email_uniqueness(session):
    """Test that user email addresses must be unique."""
    # Create first user
    user1 = User(
        name='User 1',
        email='test@example.com',
        password_hash=generate_password_hash('password')
    )
    session.add(user1)
    session.flush()
    
    # Try to create second user with same email
    user2 = User(
        name='User 2',
        email='test@example.com',
        password_hash=generate_password_hash('password')
    )
    session.add(user2)
    
    # Should raise an integrity error
    with pytest.raises(Exception):
        session.flush()

def test_project_required_fields(test_user, session):
    """Test that project required fields are enforced."""
    # Try to create project without required fields
    project = Project(user_id=test_user.id)
    session.add(project)
    
    # Should raise an integrity error
    with pytest.raises(Exception):
        session.flush()

def test_project_size_validation(test_user, session):
    """Test size field validation in Project model at both model and database levels."""
    # Test model-level validation (direct attribute assignment)
    project = Project(name="Test Project", project_type="residential", user_id=test_user.id)
    
    # Test valid size
    project.size_sqm = 1000
    assert project.size_sqm == 1000
    
    # Test non-numeric value
    with pytest.raises(ValueError, match="Size must be a number."):
        project.size_sqm = "not_a_number"
    
    # Test negative value
    with pytest.raises(ValueError, match="Size must be a positive number."):
        project.size_sqm = -100
    
    # Test zero value
    with pytest.raises(ValueError, match="Size must be a positive number."):
        project.size_sqm = 0
    
    # Test value exceeding maximum
    with pytest.raises(ValueError, match="Size must be less than 1,000,000 sq meters."):
        project.size_sqm = 2000000
    
    # Test None value (should be allowed)
    project.size_sqm = None
    assert project.size_sqm is None
    
    # Test database-level validation (saving to database)
    # Create a project with valid size
    valid_project = Project(
        name="Test Project",
        project_type="residential",
        user_id=test_user.id,
        size_sqm=1000
    )
    session.add(valid_project)
    session.flush()  # This should succeed
    
    # Test invalid size updates at database level
    # Create new project for each test to avoid previous error states
    
    # Test negative value
    project_negative = Project(name="Test Negative", project_type="residential", user_id=test_user.id, size_sqm=1000)
    session.add(project_negative)
    session.flush()
    with pytest.raises(ValueError, match="Size must be a positive number."):
        project_negative.size_sqm = -100
    session.rollback()  # Reset the session after error
    
    # Test exceeding maximum
    project_max = Project(name="Test Maximum", project_type="residential", user_id=test_user.id, size_sqm=1000)
    session.add(project_max)
    session.flush()
    with pytest.raises(ValueError, match="Size must be less than 1,000,000 sq meters."):
        project_max.size_sqm = 2000000
    session.rollback()  # Reset the session after error
    
    # Test non-numeric value
    project_nonnum = Project(name="Test Non-Numeric", project_type="residential", user_id=test_user.id, size_sqm=1000)
    session.add(project_nonnum)
    session.flush()
    with pytest.raises(ValueError, match="Size must be a number."):
        project_nonnum.size_sqm = "not_a_number"
    session.rollback()  # Reset the session after error
    
    # Test valid update
    project_valid = Project(name="Test Valid Update", project_type="residential", user_id=test_user.id, size_sqm=1000)
    session.add(project_valid)
    session.flush()
    project_valid.size_sqm = 2000
    session.flush()  # This should succeed
    assert project_valid.size_sqm == 2000

def test_project_type_validation(test_user, session):
    """Test project type validation."""
    valid_types = [
        'residential', 'commercial', 'mixed_use', 'public', 'educational',
        'healthcare', 'industrial', 'infrastructure', 'landscape',
        'urban_planning', 'other'
    ]
    
    for project_type in valid_types:
        project = Project(
            name=f'Test {project_type} Project',
            project_type=project_type,
            user_id=test_user.id
        )
        session.add(project)
        session.flush()
        assert project.project_type == project_type 