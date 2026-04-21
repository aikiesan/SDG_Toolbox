from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def email_confirmed_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and not getattr(current_user, 'email_confirmed', False):
            flash('Please confirm your email first.', 'warning')
            return redirect(url_for('auth.unconfirmed'))
        return f(*args, **kwargs)
    return decorated_function
