"""
Context processors for Jinja2 templates.
"""

from datetime import datetime
from flask import url_for
from flask_wtf.csrf import generate_csrf

def inject_now():
    """Inject current datetime into templates."""
    return {'now': datetime.now()}

def inject_csrf_token():
    """Make CSRF token available to all templates."""
    return {'csrf_token': generate_csrf()}

def url_for_project_routes(endpoint, **kwargs):
    """Handle both blueprint and non-blueprint routes for projects."""
    if endpoint.startswith('projects.'):
        # Convert blueprint route to simple route
        simple_endpoint = endpoint.replace('projects.', '')
        if simple_endpoint == 'index':
            return url_for('projects.index', **kwargs)
        elif simple_endpoint == 'new':
            return url_for('projects.new', **kwargs)
        elif simple_endpoint == 'show':
            return url_for('projects.show', **kwargs)
        elif simple_endpoint == 'edit':
            return url_for('projects.edit', **kwargs)
        elif simple_endpoint == 'delete':
            return url_for('projects.delete', **kwargs)
    elif endpoint.startswith('assessments.'):
        # Convert blueprint route to simple route
        simple_endpoint = endpoint.replace('assessments.', '')
        if simple_endpoint == 'new':
            return url_for('assessments.new', **kwargs)
        elif simple_endpoint == 'show':
            return url_for('assessments.show', **kwargs)
    
    # Fall back to standard url_for
    return url_for(endpoint, **kwargs)

def utility_processor():
    """Inject utility functions into templates."""
    return dict(url_for_project_routes=url_for_project_routes)

def register_context_processors(app):
    """Register all context processors with the app."""
    app.context_processor(inject_now)
    app.context_processor(inject_csrf_token)
    app.context_processor(utility_processor)
