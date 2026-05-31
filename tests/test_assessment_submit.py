"""End-to-end tests for the assessment submit route (core write path).

Exercises POST /assessments/projects/<pid>/assessments/<aid>/submit, which
saves responses, triggers scoring, and marks the assessment completed.
"""
from app import db
from app.models.assessment import Assessment, SdgScore
from app.models.project import Project
from app.models.response import QuestionResponse


def _draft_assessment(session, project):
    a = Assessment(project_id=project.id, user_id=project.user_id, status='draft')
    session.add(a)
    session.flush()
    return a


def _submit_url(project, assessment):
    return f'/assessments/projects/{project.id}/assessments/{assessment.id}/submit'


def test_submit_requires_login(client, test_project, session):
    a = _draft_assessment(session, test_project)
    resp = client.post(_submit_url(test_project, a), json={'q1': 'yes'})
    # Unauthenticated -> redirect to login (302) or 401
    assert resp.status_code in (302, 401)


def test_submit_completes_and_scores(client, auth, test_user, test_project, session):
    auth.login(email=test_user.email)
    a = _draft_assessment(session, test_project)

    resp = client.post(_submit_url(test_project, a),
                       json={'q1': 'yes', 'q2': ['recycling', 'reuse'], 'q3': 'neutral'})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['success'] is True

    refreshed = db.session.get(Assessment, a.id)
    assert refreshed.status == 'completed'
    assert refreshed.completed_at is not None
    # Responses persisted and scores computed.
    assert QuestionResponse.query.filter_by(assessment_id=a.id).count() == 3
    assert SdgScore.query.filter_by(assessment_id=a.id).count() == 17


def test_submit_rejects_non_owner(client, auth, other_user, test_project, session):
    # test_project belongs to test_user; log in as a different user.
    auth.login(email=other_user.email)
    a = _draft_assessment(session, test_project)
    resp = client.post(_submit_url(test_project, a), json={'q1': 'yes'})
    assert resp.status_code == 403
    assert db.session.get(Assessment, a.id).status == 'draft'


def test_submit_missing_project_404(client, auth, test_user):
    auth.login(email=test_user.email)
    resp = client.post('/assessments/projects/999999/assessments/1/submit', json={'q1': 'yes'})
    assert resp.status_code == 404


def test_submit_no_data_400(client, auth, test_user, test_project, session):
    auth.login(email=test_user.email)
    a = _draft_assessment(session, test_project)
    resp = client.post(_submit_url(test_project, a), json={})
    assert resp.status_code == 400
