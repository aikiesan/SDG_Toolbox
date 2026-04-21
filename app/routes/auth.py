"""
Authentication routes.
Handles user login, registration, and password management.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from urllib.parse import urlparse as url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User
from app import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.email_confirmed_required import email_confirmed_required
from functools import wraps

# Import email utilities if they exist
from app.utils.email_utils import send_confirmation_email, send_password_reset_email

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Use SQLAlchemy ORM to find user by email
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if not email or not password or not name:
            flash('Please provide email, name, and password.', 'danger')
            return render_template('auth/register.html')
        
        existing = User.query.filter_by(email=email).first()
        
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        
        # Create new user with SQLAlchemy ORM
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    """Confirm email with token."""
    if current_user.is_authenticated and getattr(current_user, 'email_confirmed', False):
        return redirect(url_for('main.index'))
    
    email = User.verify_confirmation_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    user_row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if not user_row:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    if user_row.get('email_confirmed'):
        flash('Account already confirmed. Please login.', 'info')
    else:
        conn.execute('UPDATE users SET email_confirmed = 1 WHERE email = ?', (email,))
        conn.commit()
        flash('Your email has been confirmed. You can now log in.', 'success')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/unconfirmed')
@login_required
def unconfirmed():
    """Show unconfirmed email page."""
    if getattr(current_user, 'email_confirmed', False):
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth_bp.route('/resend-confirmation')
@login_required
def resend_confirmation():
    """Resend email confirmation."""
    if getattr(current_user, 'email_confirmed', False):
        flash('Your email is already confirmed.', 'info')
        return redirect(url_for('main.index'))
    
    send_confirmation_email(current_user)
    flash('A new confirmation email has been sent.', 'info')
    return redirect(url_for('auth.unconfirmed'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset requests."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        conn = get_db()
        user_row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user_row:
            user_obj = User(id=user_row['id'], name=user_row['name'], email=user_row['email'])
            send_password_reset_email(user_obj)
        
        # Always show success to prevent email enumeration
        flash('If your email is registered, you will receive a password reset link shortly.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    email = User.verify_reset_token(token)
    if not email:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    conn = get_db()
    user_row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if not user_row:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        conn.execute(
            'UPDATE users SET password_hash = ? WHERE email = ?',
            (generate_password_hash(password), email)
        )
        conn.commit()
        
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard page."""
    conn = get_db()
    users = conn.execute('SELECT * FROM users').fetchall()
    user_objs = [User(id=row['id'], name=row['name'], email=row['email'], 
                      is_admin=row.get('is_admin', 0)) for row in users]
    
    return render_template('auth/admin/dashboard.html', users=user_objs)

@auth_bp.route('/profile')
@login_required
@email_confirmed_required
def profile():
    """Display user profile."""
    conn = get_db()
    user_row = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    
    if not user_row:
        flash('User not found', 'danger')
        return redirect(url_for('main.index'))
    
    user_obj = User(id=user_row['id'], name=user_row['name'], email=user_row['email'], 
                    is_admin=user_row.get('is_admin', 0))
    
    try:
        projects_count = conn.execute('SELECT COUNT(*) FROM projects WHERE user_id = ?', 
                                     (current_user.id,)).fetchone()[0]
        assessments_count = conn.execute(
            'SELECT COUNT(*) FROM assessments WHERE user_id = ?', 
            (current_user.id,)).fetchone()[0]
    except Exception as e:
        flash(f'Error fetching user data: {str(e)}', 'warning')
        projects_count = 0
        assessments_count = 0
    
    return render_template(
        'profile.html',
        user=user_obj,
        projects_count=projects_count,
        assessments_count=assessments_count
    )
