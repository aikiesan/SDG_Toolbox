"""CSRF regression tests.

The main suite disables CSRF (TestingConfig.WTF_CSRF_ENABLED = False), which is
why a broken `{{ csrf_token }}` (rendered bare instead of called) went unnoticed
and produced "The CSRF session token is missing" on real form submissions.
These tests run with CSRF enabled.
"""
import re
import pytest

from app import create_app, db as _db
from config import TestingConfig


class CSRFConfig(TestingConfig):
    WTF_CSRF_ENABLED = True


@pytest.fixture
def csrf_app():
    app = create_app(CSRFConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


def _make_user(app, email='csrf@example.com', password='password'):
    from app.models.user import User
    from werkzeug.security import generate_password_hash
    with app.app_context():
        user = User(name='CSRF User', email=email,
                    password_hash=generate_password_hash(password),
                    email_confirmed=True)
        _db.session.add(user)
        _db.session.commit()
        return user.id


def test_bare_and_called_csrf_token_match(csrf_app):
    """{{ csrf_token }} and {{ csrf_token() }} render the same valid token."""
    from flask import render_template_string
    with csrf_app.test_request_context('/'):
        bare = render_template_string('{{ csrf_token }}')
        called = render_template_string('{{ csrf_token() }}')
    assert bare and len(bare) > 20
    assert '<function' not in bare        # the original bug rendered the function repr
    assert bare == called


def test_login_form_csrf_roundtrip(csrf_app):
    """login.html uses bare {{ csrf_token }}; the round-trip must validate."""
    _make_user(csrf_app)
    client = csrf_app.test_client()
    page = client.get('/auth/login')
    token = re.search(rb'name="csrf_token" value="([^"]+)"', page.data)
    assert token, "csrf_token hidden field not rendered"
    token = token.group(1).decode()
    assert '<function' not in token
    resp = client.post('/auth/login',
                       data={'email': 'csrf@example.com', 'password': 'password',
                             'csrf_token': token})
    assert resp.status_code in (302, 303)  # success redirect, not a 400 CSRF error


def test_new_project_form_csrf_roundtrip(csrf_app):
    """new.html (the reported page) submits a project with a valid CSRF token."""
    from app.models.project import Project
    _make_user(csrf_app)
    client = csrf_app.test_client()

    # Log in first.
    page = client.get('/auth/login')
    token = re.search(rb'name="csrf_token" value="([^"]+)"', page.data).group(1).decode()
    client.post('/auth/login',
               data={'email': 'csrf@example.com', 'password': 'password', 'csrf_token': token})

    # GET the new-project form and extract its token.
    form_page = client.get('/projects/new')
    assert form_page.status_code == 200
    ptoken = re.search(rb'name="csrf_token" value="([^"]+)"', form_page.data)
    assert ptoken, "csrf_token hidden field not rendered on new project form"
    ptoken = ptoken.group(1).decode()
    assert '<function' not in ptoken

    resp = client.post('/projects/new',
                       data={'name': 'CSRF Test Project', 'project_type': 'residential',
                             'location': 'Test City', 'size_sqm': '120',
                             'csrf_token': ptoken})
    assert resp.status_code in (302, 303)  # created -> redirect, not 400
    with csrf_app.app_context():
        assert Project.query.filter_by(name='CSRF Test Project').count() == 1


def test_missing_token_is_rejected(csrf_app):
    """Sanity check: a POST with no token still fails (CSRF really is on)."""
    _make_user(csrf_app)
    client = csrf_app.test_client()
    resp = client.post('/auth/login',
                       data={'email': 'csrf@example.com', 'password': 'password'})
    assert resp.status_code == 400
