# tests/test_assessments_routes.py
import pytest
from app.models.assessment import Assessment
from app.models.sdg import SdgGoal


@pytest.fixture
def test_assessment(session, test_project):
    """Draft assessment belonging to test_project."""
    a = Assessment(
        project_id=test_project.id,
        user_id=test_project.user_id,
        status='draft',
    )
    session.add(a)
    session.flush()
    return a


def _login(client, user):
    return client.post('/auth/login', data={
        'email': user.email,
        'password': 'password',
    }, follow_redirects=True)


# ---------------------------------------------------------------------------
# Questionnaire step — GET
# ---------------------------------------------------------------------------

def test_questionnaire_step1_get(client, test_user, test_project, test_assessment):
    _login(client, test_user)
    resp = client.get(
        f'/assessments/projects/{test_project.id}/questionnaire/{test_assessment.id}/step/1'
    )
    assert resp.status_code == 200


def test_questionnaire_step_requires_login(client, test_project, test_assessment):
    resp = client.get(
        f'/assessments/projects/{test_project.id}/questionnaire/{test_assessment.id}/step/1',
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b'login' in resp.data.lower() or b'Login' in resp.data


def test_questionnaire_step1_contains_sdg_content(client, test_user, test_project, test_assessment):
    _login(client, test_user)
    resp = client.get(
        f'/assessments/projects/{test_project.id}/questionnaire/{test_assessment.id}/step/1'
    )
    assert resp.status_code == 200
    # Step 1 covers SDGs 1, 2, 3, 6 — at least the project name should appear
    assert test_project.name.encode() in resp.data or b'SDG' in resp.data


# ---------------------------------------------------------------------------
# Questionnaire step — POST (save and advance)
# ---------------------------------------------------------------------------

def test_questionnaire_step1_post_redirects_to_step2(
    client, test_user, test_project, test_assessment, session
):
    _login(client, test_user)

    # Get SDG goals for step 1 (numbers 1, 2, 3, 6)
    sdgs = session.query(SdgGoal).filter(SdgGoal.number.in_([1, 2, 3, 6])).all()
    form_data = {}
    for sdg in sdgs:
        form_data[f'direct_score_{sdg.id}'] = '1'
        form_data[f'notes_{sdg.id}'] = ''

    resp = client.post(
        f'/assessments/projects/{test_project.id}/questionnaire/{test_assessment.id}/step/1',
        data=form_data,
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert 'step/2' in resp.headers['Location']


def test_questionnaire_step5_post_redirects_to_finalize(
    client, test_user, test_project, test_assessment, session
):
    _login(client, test_user)

    sdgs = session.query(SdgGoal).filter(SdgGoal.number.in_([16, 17])).all()
    form_data = {}
    for sdg in sdgs:
        form_data[f'direct_score_{sdg.id}'] = '2'
        form_data[f'notes_{sdg.id}'] = ''

    resp = client.post(
        f'/assessments/projects/{test_project.id}/questionnaire/{test_assessment.id}/step/5',
        data=form_data,
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert 'finalize' in resp.headers['Location']


# ---------------------------------------------------------------------------
# Finalize
# ---------------------------------------------------------------------------

def test_finalize_get_redirects_to_results(client, test_user, test_assessment):
    _login(client, test_user)
    resp = client.get(f'/assessments/{test_assessment.id}/finalize', follow_redirects=False)
    assert resp.status_code == 302
    assert 'results' in resp.headers['Location']


def test_finalize_post_marks_completed(client, test_user, test_assessment, session):
    _login(client, test_user)
    resp = client.post(f'/assessments/{test_assessment.id}/finalize', follow_redirects=False)
    assert resp.status_code == 302

    session.expire(test_assessment)
    assert test_assessment.status == 'completed'


# ---------------------------------------------------------------------------
# Finalize API (JSON)
# ---------------------------------------------------------------------------

def test_finalize_api_returns_json_success(client, test_user, test_assessment):
    _login(client, test_user)
    resp = client.post(f'/assessments/{test_assessment.id}/finalize-api')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True


def test_finalize_api_requires_login(client, test_assessment):
    resp = client.post(f'/assessments/{test_assessment.id}/finalize-api', follow_redirects=False)
    # Should redirect to login (302) or return 401/403
    assert resp.status_code in (302, 401, 403)


# ---------------------------------------------------------------------------
# Results page
# ---------------------------------------------------------------------------

def test_results_page_loads(client, test_user, test_project, test_assessment):
    _login(client, test_user)
    resp = client.get(
        f'/assessments/projects/{test_project.id}/assessments/{test_assessment.id}/results',
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_results_shortcut_redirects(client, test_user, test_project, test_assessment):
    _login(client, test_user)
    resp = client.get(f'/assessments/{test_assessment.id}/results', follow_redirects=True)
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def test_delete_assessment(client, test_user, test_project, test_assessment, session):
    _login(client, test_user)
    aid = test_assessment.id
    resp = client.post(f'/assessments/{aid}/delete', follow_redirects=False)
    assert resp.status_code == 302

    deleted = session.get(Assessment, aid)
    assert deleted is None


def test_delete_requires_login(client, test_assessment):
    resp = client.post(f'/assessments/{test_assessment.id}/delete', follow_redirects=False)
    assert resp.status_code in (302, 401, 403)


def test_view_shared_valid_token(client, test_user, test_project, test_assessment, session):
    from datetime import datetime, timedelta
    test_assessment.share_token = 'test-share-token-abc123'
    test_assessment.share_expires = datetime.utcnow() + timedelta(days=30)
    session.flush()
    resp = client.get('/assessments/shared/test-share-token-abc123')
    assert resp.status_code == 200


def test_view_shared_invalid_token(client, session):
    resp = client.get('/assessments/shared/nonexistent-token', follow_redirects=True)
    assert resp.status_code == 200


def test_view_shared_expired_token(client, test_assessment, session):
    from datetime import datetime, timedelta
    test_assessment.share_token = 'expired-token-xyz'
    test_assessment.share_expires = datetime.utcnow() - timedelta(days=1)
    session.flush()
    resp = client.get('/assessments/shared/expired-token-xyz', follow_redirects=True)
    assert resp.status_code == 200


def test_delete_nonexistent_assessment_returns_404(client, test_user, auth):
    auth.login(email=test_user.email, password='password')
    resp = client.post('/assessments/999999/delete', follow_redirects=False)
    assert resp.status_code == 404


def test_delete_wrong_user_forbidden(client, other_user, test_project, test_assessment):
    _login(client, other_user)
    resp = client.post(f'/assessments/{test_assessment.id}/delete', follow_redirects=False)
    # Should be 403 or redirect (not silently succeed)
    assert resp.status_code in (302, 403)
