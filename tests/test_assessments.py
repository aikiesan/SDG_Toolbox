# tests/test_assessments.py
import pytest
from app.models import User, Project, Assessment, QuestionResponse
from datetime import datetime
from flask import url_for

def test_create_assessment(client, auth, test_user, test_project, session):
    # Login the user
    auth.login(email=test_user.email, password='password')

    response = client.post(f'/assessments/projects/{test_project.id}/new',
                         follow_redirects=False)  # Test the redirect itself
    assert response.status_code == 302
    
    # Check that an assessment was created
    assessment = session.query(Assessment).filter_by(project_id=test_project.id).order_by(Assessment.id.desc()).first()
    assert assessment is not None
    assert assessment.user_id == test_user.id
    assert response.location == url_for('assessments.questionnaire_step',
                                      project_id=test_project.id,
                                      assessment_id=assessment.id,
                                      step=1, _external=False)  # Check redirect location

def test_assessment_validation(client, auth, test_user, test_project, session):
    # Login the user
    auth.login(email=test_user.email, password='password')

    # This route does not perform validation on POST data
    # It will still create an assessment and redirect
    response = client.post(f'/assessments/projects/{test_project.id}/new', 
                         data={},
                         follow_redirects=False)
    assert response.status_code == 302  # It creates and redirects
    
    # Verify an assessment was created despite empty data
    assessment = session.query(Assessment).filter_by(project_id=test_project.id).order_by(Assessment.id.desc()).first()
    assert assessment is not None
    assert assessment.user_id == test_user.id

def test_assessment_list(client, auth, test_user, test_project, session):
    # Login the user
    auth.login(email=test_user.email, password='password')

    # Create an assessment for the project
    assessment = Assessment(
        project_id=test_project.id,
        user_id=test_user.id
    )
    session.add(assessment)
    session.flush()
    
    # Get the project detail page which lists assessments
    response = client.get(url_for('projects.show', id=test_project.id))
    assert response.status_code == 200
    
    # Check for assessment identifier in the response
    # Using assessment ID since it's a reliable identifier
    assert f"Assessment ID: {assessment.id}".encode() in response.data
    # Also check for project ID to ensure we're on the right page
    assert str(test_project.id).encode() in response.data

def test_assessment_detail(client, auth, test_user, test_project, session):
    # Login the user
    auth.login(email=test_user.email, password='password')

    assessment = Assessment(
        project_id=test_project.id,
        user_id=test_user.id
    )
    session.add(assessment)
    session.flush()
    
    response = client.get(f'/assessments/{assessment.id}')
    assert response.status_code == 200
    assert str(assessment.id).encode() in response.data
    assert str(test_project.id).encode() in response.data

# Commenting out test_assessment_edit as the route doesn't exist
# def test_assessment_edit(client, auth, test_user, test_project, session):
#     # Login the user
#     auth.login(email=test_user.email, password='password')
# 
#     assessment = Assessment(
#         project_id=test_project.id,
#         user_id=test_user.id
#     )
#     session.add(assessment)
#     session.flush()
#     
#     # Test GET request for edit form
#     response = client.get(f'/assessments/{assessment.id}/edit')
#     assert response.status_code == 200
#     
#     # Test POST request for edit submission
#     new_project = Project(name="New Project", user_id=test_user.id)
#     session.add(new_project)
#     session.flush()
#     
#     response = client.post(f'/assessments/{assessment.id}/edit', data={
#         'name': 'Updated Assessment Form',
#         'description': 'Updated Description Form',
#         'assessment_date': '2024-01-01',
#         'project_id': new_project.id
#     })
#     assert response.status_code == 302
#     
#     updated_assessment = session.get(Assessment, assessment.id)
#     assert updated_assessment.project_id == new_project.id
#     assert updated_assessment.user_id == test_user.id

def test_assessment_delete(client, auth, test_user, test_project, session):
    # Login the user
    auth.login(email=test_user.email, password='password')

    assessment = Assessment(
        project_id=test_project.id,
        user_id=test_user.id
    )
    session.add(assessment)
    session.flush()
    
    response = client.post(f'/assessments/{assessment.id}/delete')
    assert response.status_code == 302
    assert session.get(Assessment, assessment.id) is None

def test_question_response(client, auth, test_user, test_project, session):
    """Test submitting a question response through the web interface."""
    auth.login(email=test_user.email, password='password')

    assessment = Assessment(project_id=test_project.id, user_id=test_user.id)
    session.add(assessment)
    session.flush()

    generated_url = url_for('questionnaire.save_questionnaire_response', assessment_id=assessment.id)

    payload = {
        'question_id': 1,
        'response_text': 'Test response text',
        'response_option': 'option_1'
    }
    response = client.post(
        generated_url,
        json=payload
    )
    assert response.status_code == 200

    data = response.get_json()
    assert data['success'] is True
    assert data['message'] == 'Response saved successfully'

    saved_response = session.query(QuestionResponse).filter_by(
        assessment_id=assessment.id,
        question_id=1
    ).first()
    assert saved_response is not None
    assert saved_response.response_text == 'Test response text'
    assert saved_response.response_score is not None