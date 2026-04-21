"""
Middleware functions for Flask application.
Includes request processors and global handlers.
"""

from flask import request, session
from app.utils.validation import validate_request_form

def validate_all_requests():
    """
    Global middleware to validate and sanitize all form submissions.
    This attaches sanitized form data to the request object.
    """
    if request.method == 'POST':
        # Validate and sanitize form data
        request.validated_form = validate_request_form()

def update_session_activity():
    """
    Update session activity timestamp on each request.
    This helps with session timeout management.
    """
    if session:
        from datetime import datetime
        session['last_activity'] = datetime.now()

def check_login_status():
    """
    Check if user is logged in and set global template variable.
    This makes login status available to all templates without having
    to pass it explicitly from each route.
    """
    from flask import g
    
    # Set default values
    g.user_id = None
    g.user_name = None
    g.is_admin = False
    
    # Check if user is logged in via session
    if 'user_id' in session:
        g.user_id = session['user_id']
        g.user_name = session.get('user_name', 'User')
        g.is_admin = session.get('is_admin', False)
    
    # For Flask-Login compatibility
    from flask_login import current_user
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        g.user_id = current_user.id
        g.user_name = getattr(current_user, 'name', 'User')
        g.is_admin = getattr(current_user, 'is_admin', False)

def register_middleware(app):
    """
    Register all middleware with the Flask application.
    This function is called from the application factory.
    """
    # Order matters - execute in sequence for each request
    app.before_request(validate_all_requests)
    app.before_request(update_session_activity)
    app.before_request(check_login_status)
