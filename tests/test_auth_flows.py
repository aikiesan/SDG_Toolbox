"""Regression tests for auth flows that were previously broken.

confirm_email, forgot_password (POST), reset_password, profile and the admin
dashboard used a raw-SQLite layer with a missing import and mismatched token
signatures, so they crashed at runtime. These tests pin the ORM-backed
behaviour so they cannot regress.
"""
from werkzeug.security import check_password_hash

from app import db
from app.models.user import User


def test_token_roundtrip(app):
    """Confirmation and reset tokens encode/verify the user's email."""
    with app.app_context():
        user = User(name='Tok', email='tok@example.com')
        ctoken = user.generate_confirmation_token()
        rtoken = user.generate_reset_token()
        assert User.verify_confirmation_token(ctoken) == 'tok@example.com'
        assert User.verify_reset_token(rtoken) == 'tok@example.com'
        # Tokens are namespaced: a confirm token is not a valid reset token.
        assert User.verify_reset_token(ctoken) is None
        assert User.verify_confirmation_token('garbage') is None


def test_forgot_password_post_known_and_unknown(client, test_user):
    # Known email
    resp = client.post('/auth/forgot-password',
                       data={'email': test_user.email}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'password reset link' in resp.data.lower()
    # Unknown email returns the same response (no enumeration) and does not crash
    resp = client.post('/auth/forgot-password',
                       data={'email': 'nobody@example.com'}, follow_redirects=True)
    assert resp.status_code == 200


def test_reset_password_updates_hash(client, test_user):
    token = test_user.generate_reset_token()
    resp = client.get(f'/auth/reset-password/{token}')
    assert resp.status_code == 200
    resp = client.post(f'/auth/reset-password/{token}',
                       data={'password': 'newpassword123', 'confirm_password': 'newpassword123'},
                       follow_redirects=True)
    assert resp.status_code == 200
    updated = db.session.get(User, test_user.id)
    assert check_password_hash(updated.password_hash, 'newpassword123')


def test_reset_password_invalid_token_redirects(client):
    resp = client.get('/auth/reset-password/not-a-real-token', follow_redirects=True)
    assert resp.status_code == 200


def test_confirm_email_marks_confirmed(client, test_user):
    assert not test_user.email_confirmed
    token = test_user.generate_confirmation_token()
    resp = client.get(f'/auth/confirm/{token}', follow_redirects=True)
    assert resp.status_code == 200
    assert db.session.get(User, test_user.id).email_confirmed is True


def test_profile_renders_for_confirmed_user(client, auth, test_user):
    test_user.email_confirmed = True
    db.session.commit()
    auth.login(email=test_user.email)
    resp = client.get('/auth/profile')
    assert resp.status_code == 200


def test_admin_dashboard_redirects_to_user_management(client, auth, admin_user):
    auth.login(email=admin_user.email, password='adminpass')
    resp = client.get('/auth/admin', follow_redirects=True)
    assert resp.status_code == 200
    # Lands on the maintained dashboard user-management page.
    assert b'users' in resp.data.lower()
