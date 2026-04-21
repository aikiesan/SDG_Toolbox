"""
User model for authentication and authorization.
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from itsdangerous import URLSafeTimedSerializer

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))

    # UIA integration fields (nullable — filled when UIA SSO is connected)
    uia_user_id = db.Column(db.String(64), nullable=True, unique=True, index=True)
    organization  = db.Column(db.String(256), nullable=True)
    uia_role      = db.Column(db.String(64), nullable=True)

    projects = db.relationship('Project', back_populates='user', cascade='all, delete-orphan')

    def check_password(self, password_hash, password):
        """Verify a password against its hash."""
        return check_password_hash(password_hash, password)

    @staticmethod
    def generate_confirmation_token(email, secret_key, salt):
        """Generate token for email confirmation."""
        serializer = URLSafeTimedSerializer(secret_key)
        return serializer.dumps(email, salt=salt)

    @staticmethod
    def verify_confirmation_token(token, secret_key, salt, expiration=3600):
        """Verify an email confirmation token."""
        serializer = URLSafeTimedSerializer(secret_key)
        try:
            email = serializer.loads(
                token,
                salt=salt,
                max_age=expiration
            )
            return email
        except Exception:
            return None

    @staticmethod
    def generate_reset_token(email, secret_key, salt):
        """Generate token for password reset."""
        serializer = URLSafeTimedSerializer(secret_key)
        return serializer.dumps(email, salt=salt + 'reset')

    @staticmethod
    def verify_reset_token(token, secret_key, salt, expiration=3600):
        """Verify a password reset token."""
        serializer = URLSafeTimedSerializer(secret_key)
        try:
            email = serializer.loads(
                token,
                salt=salt + 'reset',
                max_age=expiration
            )
            return email
        except Exception:
            return None
