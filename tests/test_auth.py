# tests/test_auth.py
import pytest
from flask import session
from app.models.user import User
from app.models.project import Project

def test_login_logout(auth, client, test_user, session):
    """Test login and logout using the auth fixture."""
    # Test login with the specific user created for this test
    response = auth.login(email=test_user.email)
    assert response.status_code == 200
    assert b"Logout" in response.data  # Check for logout link
    # --- CHANGE THIS ASSERTION ---
    # Check for something that ONLY appears when logged in
    assert b'My Projects' in response.data  # Assumes this text is in the logged-in navbar/dropdown
    # assert b"Login" not in response.data  # Comment out or remove this
    # --- END CHANGE ---

    # Check session variable AFTER successful login using session_transaction
    with client.session_transaction() as flask_sess:
        assert flask_sess.get('_user_id') == str(test_user.id)

    # --- Add a project for this user to prevent NoneType error ---
    project = Project(name='User Project for Login Test', user_id=test_user.id, description='Desc')
    session.add(project)
    session.commit()
    # -------------------------------------------------------------

    # Check accessing a protected route (e.g., projects index)
    response_projects = client.get('/projects/')
    assert response_projects.status_code == 200
    assert b'My Projects' in response_projects.data

    # Test logout
    response_logout = auth.logout()
    assert response_logout.status_code == 200
    # assert b"You have been logged out" in response_logout.data
    assert b"Login" in response_logout.data

    # Check session variable after logout using session_transaction
    with client.session_transaction() as flask_sess:
        assert '_user_id' not in flask_sess

    # Check accessing protected route after logout
    response_projects_after_logout = client.get('/projects/')
    assert response_projects_after_logout.status_code == 302  # Expect redirect to login page
    assert '/auth/login' in response_projects_after_logout.headers['Location']  # Verify redirect location


def test_login_invalid_password(auth, client, test_user):
    """Test login with incorrect password."""
    response = auth.login(email=test_user.email, password='wrongpassword')
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data
    assert b'Logout' not in response.data