# tests/test_basic.py
import pytest

def test_index_page(client):
    """Test that the index page loads and contains the correct title."""
    response = client.get('/')
    assert response.status_code == 200
    # Check for the title in the HTML
    assert b'<title>SDG Assessment Tool' in response.data


def test_config(app):
    """Test that the testing config is loaded and relevant keys are set."""
    assert app.config.get('TESTING', False) is True
    assert app.config.get('SQLALCHEMY_DATABASE_URI') is not None
    assert app.config.get('MAIL_SUPPRESS_SEND', False) is True
    assert app.config.get('SERVER_NAME') == 'localhost.test'