"""
Routes package initialization.
"""

# Import routes for easier access and to ensure they're imported when the package is imported
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.projects import projects_bp
from app.routes.assessments import assessments_bp
from app.routes.questionnaire import questionnaire_bp
from app.routes.api import api_bp
from app.routes.dashboard import dashboard_bp
