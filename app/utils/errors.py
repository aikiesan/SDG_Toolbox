"""
Error handlers for the application.
Handles various HTTP error codes.
"""

from flask import render_template, redirect, url_for, flash

def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    @app.errorhandler(401)
    def unauthorized(e):
        """Handle 401 Unauthorized errors."""
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden(e):
        """Handle 403 Forbidden errors."""
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 Not Found errors."""
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 Internal Server Error errors."""
        return render_template('500.html'), 500
