import os
from datetime import timedelta


def _env_bool(name, default=False):
    """Parse a boolean environment variable."""
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ('true', 'on', '1', 'yes')


# Sentinel value used as the insecure development fallback. Production refuses
# to start while SECRET_KEY still equals this (enforced in create_app).
INSECURE_DEFAULT_SECRET_KEY = 'dev-key-for-sdg-assessment'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or INSECURE_DEFAULT_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'sdgassessmentdev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Flask-Mail Configuration ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'  # e.g., smtp.googlemail.com for Gmail
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Your email address
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Your email password or app password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or (MAIL_USERNAME if 'MAIL_USERNAME' in os.environ else None)
    ADMINS = [os.environ.get('ADMIN_EMAIL')] if os.environ.get('ADMIN_EMAIL') else []  # For error reporting
    # --- End Flask-Mail Config ---

    # --- Session / cookie hardening ---
    # Overridable via environment so deployments can tune them (see
    # .env.production.template). Defaults here are safe for development.
    SESSION_COOKIE_HTTPONLY = _env_bool('SESSION_COOKIE_HTTPONLY', True)
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', False)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', False)
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.environ.get('REMEMBER_COOKIE_DURATION') or 14))


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False
    SERVER_NAME = 'localhost.test'
    MAIL_SUPPRESS_SEND = True  # Disable actual email sending during tests


class ProductionConfig(Config):
    DEBUG = False
    PREFERRED_URL_SCHEME = 'https'
    # Secure cookies are required in production. They are sent only over HTTPS,
    # so HTTPS must be terminated at the proxy (see nginx.conf / DEPLOYMENT.md).
    # Set SESSION_COOKIE_SECURE=False explicitly only for an HTTP-only bootstrap.
    SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', True)
    REMEMBER_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', True)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
