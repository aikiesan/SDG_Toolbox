import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-sdg-assessment'
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
    ADMINS = [os.environ.get('ADMIN_EMAIL') or 'lucassnakamura@gmail.com']  # For error reporting
    # --- End Flask-Mail Config ---

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

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
