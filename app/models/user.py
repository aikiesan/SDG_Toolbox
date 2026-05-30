"""
User model for authentication and authorization.
"""

from app import db
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from itsdangerous import URLSafeTimedSerializer

# Salts namespace the two token types so a confirmation token can never be
# replayed as a password-reset token (and vice versa).
_CONFIRM_SALT = 'email-confirm'
_RESET_SALT = 'password-reset'

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
    def _serializer():
        return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    def generate_confirmation_token(self):
        """Generate a signed email-confirmation token for this user."""
        return self._serializer().dumps(self.email, salt=_CONFIRM_SALT)

    @staticmethod
    def verify_confirmation_token(token, expiration=3600):
        """Return the email encoded in a valid confirmation token, else None."""
        try:
            return User._serializer().loads(token, salt=_CONFIRM_SALT, max_age=expiration)
        except Exception:
            return None

    def generate_reset_token(self):
        """Generate a signed password-reset token for this user."""
        return self._serializer().dumps(self.email, salt=_RESET_SALT)

    @staticmethod
    def verify_reset_token(token, expiration=3600):
        """Return the email encoded in a valid reset token, else None."""
        try:
            return User._serializer().loads(token, salt=_RESET_SALT, max_age=expiration)
        except Exception:
            return None
