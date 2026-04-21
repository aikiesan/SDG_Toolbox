import pytest
from flask import url_for
from unittest.mock import patch
from flask_login import current_user

def test_404_error(client):
    """Test that 404 errors are handled correctly."""
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data
    assert b"The page you are looking for does not exist." in response.data
    assert b"Return to Home" in response.data

def test_401_error(client):
    """Test that 401 errors redirect to login."""
    # Try to access a protected route without logging in
    response = client.get(url_for('projects.new_project'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data

def test_403_error(client, test_user, auth):
    """Test that accessing admin-only routes as non-admin redirects with a message."""
    auth.login(email=test_user.email)
    response = client.get(url_for('dashboard.projects'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Administrator access required" in response.data

def test_500_error(client, app, test_user, auth):
    """Test that 500 errors are handled correctly."""
    auth.login(email=test_user.email, password='password')
    app.config['PROPAGATE_EXCEPTIONS'] = False
    try:
        with patch('app.routes.projects.Project.query') as mock_query:
            mock_query.filter_by.side_effect = Exception("Simulated server error")
            response = client.get(url_for('projects.index'))
            assert response.status_code == 500
            assert b"Internal Server Error" in response.data
    finally:
        app.config['PROPAGATE_EXCEPTIONS'] = True

def test_error_page_styles(client):
    """Test that error pages have proper styling and layout."""
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404
    
    # Check for Bootstrap classes and styling
    assert b'container' in response.data
    assert b'row' in response.data
    assert b'col-md-12' in response.data
    assert b'text-center' in response.data
    assert b'btn btn-primary' in response.data

def test_error_page_navigation(client):
    """Test that error pages have working navigation."""
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404

    # Check for navigation elements
    assert b'navbar' in response.data
    assert b'navbar-brand' in response.data
    assert b'SDG Assessment Tool' in response.data

    # Check for footer
    assert b'footer' in response.data