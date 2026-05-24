# tests/test_auth_routes.py
import pytest


def test_login_get(client):
    resp = client.get('/auth/login')
    assert resp.status_code == 200


def test_register_get(client):
    resp = client.get('/auth/register')
    assert resp.status_code == 200


def test_forgot_password_get(client):
    resp = client.get('/auth/forgot-password')
    assert resp.status_code == 200


def test_login_success(client, test_user):
    resp = client.post('/auth/login', data={
        'email': test_user.email,
        'password': 'password',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Login successful' in resp.data


def test_login_wrong_password(client, test_user):
    resp = client.post('/auth/login', data={
        'email': test_user.email,
        'password': 'wrongpass',
    }, follow_redirects=True)
    assert b'Invalid' in resp.data


def test_login_unknown_email(client, session):
    resp = client.post('/auth/login', data={
        'email': 'nobody@example.com',
        'password': 'password',
    }, follow_redirects=True)
    assert b'Invalid' in resp.data


def test_logout_redirects(client, test_user, auth):
    auth.login(email=test_user.email, password='password')
    resp = client.get('/auth/logout', follow_redirects=True)
    assert resp.status_code == 200
    assert b'logged out' in resp.data


def test_register_new_user(client, session):
    resp = client.post('/auth/register', data={
        'email': 'brandnew@example.com',
        'name': 'Brand New',
        'password': 'securepass123',
    }, follow_redirects=True)
    assert resp.status_code == 200
    # Successful registration redirects to login
    assert b'Registration successful' in resp.data or b'login' in resp.data.lower()


def test_register_duplicate_email(client, test_user):
    resp = client.post('/auth/register', data={
        'email': test_user.email,
        'name': 'Duplicate',
        'password': 'password',
    }, follow_redirects=True)
    assert b'already registered' in resp.data


def test_register_missing_fields(client, session):
    resp = client.post('/auth/register', data={
        'email': 'partial@example.com',
        # name and password missing
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_unconfirmed_requires_login(client, session):
    resp = client.get('/auth/unconfirmed', follow_redirects=True)
    assert resp.status_code == 200
    # Should redirect to login page
    assert b'login' in resp.data.lower() or b'Login' in resp.data


def test_unconfirmed_accessible_when_logged_in(client, test_user, auth):
    auth.login(email=test_user.email, password='password')
    resp = client.get('/auth/unconfirmed', follow_redirects=True)
    # Either shows unconfirmed page or redirects to index (if email already confirmed)
    assert resp.status_code == 200


def test_admin_route_requires_admin(client, test_user, auth):
    auth.login(email=test_user.email, password='password')
    resp = client.get('/auth/admin', follow_redirects=True)
    # Non-admin should be redirected away
    assert resp.status_code == 200
    assert b'admin privileges' in resp.data or b'login' in resp.data.lower()


def test_admin_route_requires_login(client, session):
    resp = client.get('/auth/admin', follow_redirects=True)
    assert resp.status_code == 200
    assert b'login' in resp.data.lower() or b'Login' in resp.data


def test_profile_unconfirmed_redirects_to_unconfirmed(client, test_user, auth):
    # test_user has email_confirmed=False (default) — decorator should redirect
    auth.login(email=test_user.email, password='password')
    resp = client.get('/auth/profile', follow_redirects=False)
    assert resp.status_code == 302
    assert 'unconfirmed' in resp.headers['Location']


def test_unconfirmed_confirmed_user_redirects_to_index(client, admin_user, auth):
    # admin_user has email_confirmed=True — should redirect away from unconfirmed page
    auth.login(email=admin_user.email, password='adminpass')
    resp = client.get('/auth/unconfirmed', follow_redirects=False)
    assert resp.status_code == 302
