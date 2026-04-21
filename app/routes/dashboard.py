"""
Dashboard routes for the application.
Provides analytics, user management, and admin functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from app.utils.db import get_db
from app import cache
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)

# Admin check decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is admin via Flask-Login
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            return f(*args, **kwargs)
        
        # Check if user is admin via session
        if session.get('is_admin'):
            return f(*args, **kwargs)
        
        # Not an admin
        flash('Administrator access required', 'danger')
        return redirect(url_for('main.index'))
    
    return decorated_function

@dashboard_bp.route('/')
@login_required
@admin_required
@cache.cached(timeout=60, key_prefix='dashboard_index')  # 1-minute cache
def index():
    """Dashboard home page with overall statistics."""
    conn = get_db()

    # Consolidate all counts and average into a single query using CTEs
    stats_query = '''
        WITH stats AS (
            SELECT
                (SELECT COUNT(*) FROM users) as user_count,
                (SELECT COUNT(*) FROM projects) as project_count,
                (SELECT COUNT(*) FROM assessments) as assessment_count,
                (SELECT COUNT(*) FROM assessments WHERE status = 'completed') as completed_count,
                (SELECT AVG(overall_score) FROM assessments WHERE overall_score IS NOT NULL) as avg_score
        )
        SELECT * FROM stats
    '''
    stats = conn.execute(stats_query).fetchone()
    user_count = stats[0]
    project_count = stats[1]
    assessment_count = stats[2]
    completed_assessment_count = stats[3]
    avg_score = stats[4]

    # Get average scores per SDG
    sdg_scores = conn.execute('''
        SELECT g.number, g.name, AVG(s.total_score) as avg_score, g.color_code
        FROM sdg_scores s
        JOIN sdg_goals g ON s.sdg_id = g.id
        GROUP BY g.id
        ORDER BY g.number
    ''').fetchall()

    # Get recent activity in a single query with UNION ALL
    recent_data = conn.execute('''
        SELECT 'project' as type, p.id, p.name, p.created_at, u.name as user_name,
               NULL as project_name, p.description, p.project_type, p.location, p.size_sqm,
               p.user_id, p.updated_at, p.start_date, p.end_date, p.budget, p.sector, p.status
        FROM projects p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 5
    ''').fetchall()
    recent_projects = [dict(row) for row in recent_data]

    recent_assessments = conn.execute('''
        SELECT a.*, p.name as project_name, u.name as user_name
        FROM assessments a
        JOIN projects p ON a.project_id = p.id
        JOIN users u ON a.user_id = u.id
        ORDER BY a.created_at DESC
        LIMIT 5
    ''').fetchall()
    
    return render_template(
        'dashboard/index.html',
        user_count=user_count,
        project_count=project_count,
        assessment_count=assessment_count,
        completed_assessment_count=completed_assessment_count,
        avg_score=avg_score,
        sdg_scores=[dict(score) for score in sdg_scores],
        recent_projects=recent_projects,
        recent_assessments=[dict(assessment) for assessment in recent_assessments]
    )

@dashboard_bp.route('/users')
@login_required
@admin_required
def users():
    """User management dashboard."""
    conn = get_db()

    # Optimized query using LEFT JOINs instead of correlated subqueries
    users_data = conn.execute('''
        SELECT u.*,
               COALESCE(COUNT(DISTINCT p.id), 0) as project_count,
               COALESCE(COUNT(DISTINCT a.id), 0) as assessment_count
        FROM users u
        LEFT JOIN projects p ON p.user_id = u.id
        LEFT JOIN assessments a ON a.project_id = p.id
        GROUP BY u.id
        ORDER BY u.name
    ''').fetchall()

    return render_template(
        'dashboard/users.html',
        users=[dict(user) for user in users_data]
    )

@dashboard_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View user details."""
    conn = get_db()
    
    # Get user info
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard.users'))
    
    # Get user's projects with optimized query (LEFT JOIN instead of subquery)
    projects = conn.execute('''
        SELECT p.*,
               COALESCE(COUNT(a.id), 0) as assessment_count
        FROM projects p
        LEFT JOIN assessments a ON a.project_id = p.id
        WHERE p.user_id = ?
        GROUP BY p.id
        ORDER BY p.created_at DESC
    ''', (user_id,)).fetchall()
    
    # Get user's assessments
    assessments = conn.execute('''
        SELECT a.*, p.name as project_name
        FROM assessments a
        JOIN projects p ON a.project_id = p.id
        WHERE p.user_id = ?
        ORDER BY a.created_at DESC
    ''', (user_id,)).fetchall()
    
    return render_template(
        'dashboard/user_detail.html',
        user=dict(user),
        projects=[dict(project) for project in projects],
        assessments=[dict(assessment) for assessment in assessments]
    )

@dashboard_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details."""
    conn = get_db()
    
    # Get user info
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard.users'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Basic validation
        if not name or not email:
            flash('Name and email are required', 'danger')
            return render_template('dashboard/edit_user.html', user=dict(user))
        
        # Check if email is already used by another user
        existing = conn.execute('SELECT id FROM users WHERE email = ? AND id != ?', 
                              (email, user_id)).fetchone()
        if existing:
            flash('Email is already in use by another user', 'danger')
            return render_template('dashboard/edit_user.html', user=dict(user))
        
        # Update user
        conn.execute('''
            UPDATE users
            SET name = ?, email = ?, is_admin = ?
            WHERE id = ?
        ''', (name, email, is_admin, user_id))
        conn.commit()
        
        flash('User updated successfully', 'success')
        return redirect(url_for('dashboard.user_detail', user_id=user_id))
    
    return render_template('dashboard/edit_user.html', user=dict(user))

@dashboard_bp.route('/projects')
@login_required
@admin_required
def projects():
    """Project management dashboard."""
    conn = get_db()

    # Optimized query using LEFT JOIN instead of correlated subquery
    projects_data = conn.execute('''
        SELECT p.*, u.name as user_name,
               COALESCE(COUNT(a.id), 0) as assessment_count
        FROM projects p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN assessments a ON a.project_id = p.id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    ''').fetchall()

    return render_template(
        'dashboard/projects.html',
        projects=[dict(project) for project in projects_data]
    )

@dashboard_bp.route('/assessments')
@login_required
@admin_required
def assessments():
    """Assessment management dashboard."""
    conn = get_db()
    
    # Get all assessments with project and user info
    assessments_data = conn.execute('''
        SELECT a.*, p.name as project_name, u.name as user_name
        FROM assessments a
        JOIN projects p ON a.project_id = p.id
        JOIN users u ON p.user_id = u.id
        ORDER BY a.created_at DESC
    ''').fetchall()
    
    return render_template(
        'dashboard/assessments.html',
        assessments=[dict(assessment) for assessment in assessments_data]
    )

@dashboard_bp.route('/analytics')
@login_required
@admin_required
@cache.cached(timeout=300, key_prefix='dashboard_analytics')  # 5-minute cache
def analytics():
    """Analytics dashboard with charts and statistics."""
    conn = get_db()
    
    # Get SDG average scores
    sdg_scores = conn.execute('''
        SELECT g.number, g.name, AVG(s.total_score) as avg_score, g.color_code
        FROM sdg_scores s
        JOIN sdg_goals g ON s.sdg_id = g.id
        GROUP BY g.id
        ORDER BY g.number
    ''').fetchall()
    
    # Monthly assessment counts
    monthly_counts = conn.execute('''
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM assessments
        GROUP BY month
        ORDER BY month
    ''').fetchall()
    
    # Project type breakdown
    project_types = conn.execute('''
        SELECT project_type, COUNT(*) as count
        FROM projects
        GROUP BY project_type
        ORDER BY count DESC
    ''').fetchall()
    
    # Score distribution
    score_distribution = conn.execute('''
        SELECT 
            CASE
                WHEN overall_score < 2 THEN '0-2'
                WHEN overall_score < 4 THEN '2-4'
                WHEN overall_score < 6 THEN '4-6'
                WHEN overall_score < 8 THEN '6-8'
                ELSE '8-10'
            END as score_range,
            COUNT(*) as count
        FROM assessments
        WHERE overall_score IS NOT NULL
        GROUP BY score_range
        ORDER BY score_range
    ''').fetchall()
    
    return render_template(
        'dashboard/analytics.html',
        sdg_scores=[dict(score) for score in sdg_scores],
        monthly_counts=[dict(month) for month in monthly_counts],
        project_types=[dict(pt) for pt in project_types],
        score_distribution=[dict(score) for score in score_distribution]
    )

@dashboard_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Application settings."""
    # This could be expanded to include actual application settings
    # stored in a settings table
    return render_template('dashboard/settings.html')

@dashboard_bp.route('/sdg-management')
@login_required
@admin_required
def sdg_management():
    """Manage SDG goals and relationships."""
    conn = get_db()
    
    # Get all SDG goals
    goals = conn.execute('SELECT * FROM sdg_goals ORDER BY number').fetchall()
    
    # Get all SDG relationships
    relationships = conn.execute('''
        SELECT r.*, s.number as source_number, s.name as source_name,
               t.number as target_number, t.name as target_name
        FROM sdg_relationships r
        JOIN sdg_goals s ON r.source_sdg_id = s.id
        JOIN sdg_goals t ON r.target_sdg_id = t.id
        ORDER BY r.source_sdg_id, r.relationship_strength DESC
    ''').fetchall()
    
    return render_template(
        'dashboard/sdg_management.html',
        goals=[dict(goal) for goal in goals],
        relationships=[dict(rel) for rel in relationships]
    )

@dashboard_bp.route('/question-management')
@login_required
@admin_required
def question_management():
    """Manage assessment questions."""
    conn = get_db()
    
    # Get all SDG questions with SDG info
    questions = conn.execute('''
        SELECT q.*, g.number as sdg_number, g.name as sdg_name
        FROM sdg_questions_view
        ORDER BY display_order
    ''').fetchall()
    
    # Get all SDG goals for dropdown
    goals = conn.execute('SELECT * FROM sdg_goals ORDER BY number').fetchall()
    
    return render_template(
        'dashboard/question_management.html',
        questions=[dict(question) for question in questions],
        goals=[dict(goal) for goal in goals]
    )
