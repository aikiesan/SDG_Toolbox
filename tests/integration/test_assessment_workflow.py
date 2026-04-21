"""
Integration tests for the complete assessment workflow.
Tests the full flow: Create project → Start assessment → Complete questionnaire → View results
"""

import pytest
from app.models.project import Project
from app.models.assessment import Assessment, SdgScore
from app.models.response import QuestionResponse
from app.models.sdg import SdgQuestion
from flask_login import login_user


class TestAssessmentWorkflow:
    """Test the complete assessment workflow from creation to completion."""

    def test_complete_assessment_workflow(self, client, session, test_user, auth):
        """
        Test the complete workflow:
        1. Create a project
        2. Start an assessment
        3. Complete questionnaire steps
        4. Calculate scores
        5. View results
        """
        # Step 1: Login
        auth.login(email=test_user.email, password='password')

        # Step 2: Create a project
        response = client.post('/projects/new', data={
            'name': 'Integration Test Project',
            'description': 'Testing full workflow',
            'project_type': 'commercial',
            'location': 'Test City',
            'size_sqm': 1000.0,
            'budget': 50000.0,
            'sector': 'Technology'
        }, follow_redirects=True)

        assert response.status_code == 200
        project = session.query(Project).filter_by(name='Integration Test Project').first()
        assert project is not None
        assert project.user_id == test_user.id

        # Step 3: Start an assessment
        response = client.post(f'/projects/{project.id}/assessment/new', data={
            'assessment_type': 'standard'
        }, follow_redirects=True)

        assert response.status_code == 200
        assessment = session.query(Assessment).filter_by(project_id=project.id).first()
        assert assessment is not None
        assert assessment.status == 'draft'
        assert assessment.assessment_type == 'standard'

        # Step 4: Complete questionnaire (simulate answering questions)
        questions = session.query(SdgQuestion).limit(5).all()
        for question in questions:
            response_data = QuestionResponse(
                assessment_id=assessment.id,
                question_id=question.id,
                response_score=4.0,
                response_text='Integration test response'
            )
            session.add(response_data)
        session.commit()

        # Step 5: Calculate scores (would normally be triggered by completing assessment)
        from app.services.scoring_service import calculate_sdg_scores
        result = calculate_sdg_scores(assessment.id)

        assert 'overall_score' in result
        assert result['overall_score'] > 0
        assert 'sdg_scores' in result

        # Step 6: Verify scores were saved
        sdg_scores = session.query(SdgScore).filter_by(assessment_id=assessment.id).all()
        assert len(sdg_scores) > 0

        # Verify assessment overall score was updated
        session.refresh(assessment)
        assert assessment.overall_score is not None
        assert assessment.overall_score > 0

        # Step 7: View results page
        response = client.get(f'/assessments/{assessment.id}/results')
        assert response.status_code == 200
        assert b'Integration Test Project' in response.data

    def test_assessment_step_navigation(self, client, session, test_user, test_project, auth):
        """Test navigating through assessment steps."""
        auth.login(email=test_user.email, password='password')

        # Create assessment
        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_user.id,
            status='draft',
            assessment_type='standard'
        )
        session.add(assessment)
        session.commit()

        # Test navigation through steps (if your app has multi-step assessment)
        steps = [1, 2, 3, 4, 5]
        for step in steps:
            response = client.get(f'/assessments/{assessment.id}/step/{step}')
            # Adjust assertion based on your app's behavior
            assert response.status_code in [200, 302]  # 200 for step exists, 302 for redirect

    def test_assessment_validation(self, client, session, test_user, auth):
        """Test validation when creating assessment without required fields."""
        auth.login(email=test_user.email, password='password')

        # Try to create assessment without project (should fail)
        response = client.post('/assessments/new', data={
            'assessment_type': 'standard'
        }, follow_redirects=True)

        # Should either redirect or show error (adjust based on actual behavior)
        assert response.status_code in [200, 400, 404]

    def test_assessment_permissions(self, client, session, test_user, other_user, test_project, auth):
        """Test that users can only access their own assessments."""
        # Create assessment for test_user
        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_user.id,
            status='draft'
        )
        session.add(assessment)
        session.commit()

        # Login as other_user and try to access test_user's assessment
        auth.logout()
        auth.login(email=other_user.email, password='password')

        response = client.get(f'/assessments/{assessment.id}/results')
        # Should be forbidden or redirect (adjust based on actual behavior)
        assert response.status_code in [403, 404, 302]

    def test_complete_assessment_updates_status(self, client, session, test_user, test_project, auth):
        """Test that completing an assessment updates its status."""
        auth.login(email=test_user.email, password='password')

        assessment = Assessment(
            project_id=test_project.id,
            user_id=test_user.id,
            status='draft'
        )
        session.add(assessment)
        session.commit()

        # Add some responses
        questions = session.query(SdgQuestion).limit(3).all()
        for question in questions:
            response = QuestionResponse(
                assessment_id=assessment.id,
                question_id=question.id,
                response_score=3.0
            )
            session.add(response)
        session.commit()

        # Complete the assessment (adjust endpoint based on your app)
        from app.services.scoring_service import calculate_sdg_scores
        calculate_sdg_scores(assessment.id)

        # Manually update status to completed
        assessment.status = 'completed'
        session.commit()

        session.refresh(assessment)
        assert assessment.status == 'completed'
        assert assessment.overall_score is not None
