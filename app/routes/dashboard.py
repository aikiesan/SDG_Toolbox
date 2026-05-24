"""
Dashboard routes for the application.
Provides analytics, user management, and admin functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db, cache
from app.models.user import User
from app.models.project import Project
from app.models.assessment import Assessment, SdgScore
from app.models.sdg import SdgGoal, SdgQuestion
from app.models.sdg_relationship import SdgRelationship
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            return f(*args, **kwargs)
        if session.get('is_admin'):
            return f(*args, **kwargs)
        flash('Administrator access required', 'danger')
        return redirect(url_for('main.index'))
    return decorated_function


def _project_to_dict(project, user_name=None):
    return {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'project_type': project.project_type,
        'location': project.location,
        'size_sqm': project.size_sqm,
        'user_id': project.user_id,
        'user_name': user_name or (project.user.name if project.user else ''),
        'created_at': project.created_at,
        'updated_at': project.updated_at,
        'start_date': project.start_date,
        'end_date': project.end_date,
        'budget': project.budget,
        'sector': project.sector,
        'status': project.status,
        'assessment_count': project.assessment_count,
    }


def _assessment_to_dict(assessment, project_name=None, user_name=None):
    return {
        'id': assessment.id,
        'project_id': assessment.project_id,
        'project_name': project_name or (assessment.project.name if assessment.project else ''),
        'user_id': assessment.user_id,
        'user_name': user_name or '',
        'status': assessment.status,
        'overall_score': assessment.overall_score,
        'assessment_type': assessment.assessment_type,
        'created_at': assessment.created_at,
        'updated_at': assessment.updated_at,
        'completed_at': assessment.completed_at,
    }


@dashboard_bp.route('/')
@login_required
@admin_required
@cache.cached(timeout=60, key_prefix='dashboard_index')
def index():
    """Dashboard home page with overall statistics."""
    user_count = User.query.count()
    project_count = Project.query.count()
    assessment_count = Assessment.query.count()
    completed_assessment_count = Assessment.query.filter_by(status='completed').count()
    avg_score = db.session.query(func.avg(Assessment.overall_score)).filter(
        Assessment.overall_score.isnot(None)
    ).scalar()

    sdg_scores_rows = db.session.query(
        SdgGoal.number,
        SdgGoal.name,
        func.avg(SdgScore.total_score).label('avg_score'),
        SdgGoal.color_code
    ).join(SdgScore, SdgScore.sdg_id == SdgGoal.id).group_by(SdgGoal.id).order_by(SdgGoal.number).all()
    sdg_scores = [{'number': r[0], 'name': r[1], 'avg_score': r[2], 'color_code': r[3]}
                  for r in sdg_scores_rows]

    recent_projects_q = db.session.query(Project, User.name).join(
        User, User.id == Project.user_id
    ).order_by(Project.created_at.desc()).limit(5).all()
    recent_projects = [_project_to_dict(p, user_name=uname) for p, uname in recent_projects_q]

    recent_assessments_q = db.session.query(Assessment, Project.name, User.name).join(
        Project, Project.id == Assessment.project_id
    ).join(User, User.id == Project.user_id).order_by(Assessment.created_at.desc()).limit(5).all()
    recent_assessments = [_assessment_to_dict(a, project_name=pname, user_name=uname)
                          for a, pname, uname in recent_assessments_q]

    completion_rate = (completed_assessment_count / assessment_count * 100) if assessment_count else 0

    def _step_pct(col):
        if not assessment_count:
            return 0
        count = Assessment.query.filter(col == True).count()
        return count / assessment_count * 100

    progress_stats = {
        'step1': _step_pct(Assessment.step1_completed),
        'step2': _step_pct(Assessment.step2_completed),
        'step3': _step_pct(Assessment.step3_completed),
        'step4': _step_pct(Assessment.step4_completed),
        'step5': _step_pct(Assessment.step5_completed),
    }

    # Chart data
    sdg_labels = [r['number'] for r in sdg_scores]
    sdg_score_values = [round(r['avg_score'], 1) if r['avg_score'] else 0 for r in sdg_scores]
    sdg_colors = [r['color_code'] for r in sdg_scores]

    project_types_rows = db.session.query(
        Project.project_type, func.count().label('count')
    ).group_by(Project.project_type).order_by(func.count().desc()).all()
    project_type_labels = [r[0] or 'Unknown' for r in project_types_rows]
    project_type_counts = [r[1] for r in project_types_rows]

    monthly_rows = db.session.query(
        func.strftime('%Y-%m', Assessment.created_at).label('month'),
        func.count().label('count')
    ).group_by('month').order_by('month').all()
    month_labels = [r[0] for r in monthly_rows]
    month_data = [r[1] for r in monthly_rows]

    return render_template(
        'dashboard/index.html',
        user_count=user_count,
        project_count=project_count,
        assessment_count=assessment_count,
        completed_assessment_count=completed_assessment_count,
        avg_score=avg_score or 0,
        completion_rate=completion_rate,
        progress_stats=progress_stats,
        sdg_scores=sdg_score_values,
        sdg_labels=sdg_labels,
        sdg_colors=sdg_colors,
        project_type_labels=project_type_labels,
        project_type_counts=project_type_counts,
        month_labels=month_labels,
        month_data=month_data,
        recent_projects=recent_projects,
        recent_assessments=recent_assessments,
    )


@dashboard_bp.route('/users')
@login_required
@admin_required
def users():
    """User management dashboard."""
    users_q = db.session.query(
        User,
        func.count(func.distinct(Project.id)).label('project_count'),
        func.count(func.distinct(Assessment.id)).label('assessment_count'),
    ).outerjoin(Project, Project.user_id == User.id).outerjoin(
        Assessment, Assessment.project_id == Project.id
    ).group_by(User.id).order_by(User.name).all()

    users_data = [{
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'is_admin': u.is_admin,
        'project_count': pc,
        'assessment_count': ac,
    } for u, pc, ac in users_q]

    return render_template('dashboard/users.html', users=users_data)


@dashboard_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View user details."""
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard.users'))

    projects_q = db.session.query(
        Project,
        func.count(Assessment.id).label('assessment_count'),
    ).outerjoin(Assessment, Assessment.project_id == Project.id).filter(
        Project.user_id == user_id
    ).group_by(Project.id).order_by(Project.created_at.desc()).all()
    projects = [_project_to_dict(p, user_name=user.name) | {'assessment_count': ac}
                for p, ac in projects_q]

    assessments_q = db.session.query(Assessment, Project.name).join(
        Project, Project.id == Assessment.project_id
    ).filter(Project.user_id == user_id).order_by(Assessment.created_at.desc()).all()
    assessments = [_assessment_to_dict(a, project_name=pname, user_name=user.name)
                   for a, pname in assessments_q]

    return render_template(
        'dashboard/user_detail.html',
        user={'id': user.id, 'name': user.name, 'email': user.email, 'is_admin': user.is_admin},
        projects=projects,
        assessments=assessments,
    )


@dashboard_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details."""
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard.users'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        is_admin = request.form.get('is_admin') == 'on'

        if not name or not email:
            flash('Name and email are required', 'danger')
            return render_template('dashboard/edit_user.html',
                                   user={'id': user.id, 'name': user.name, 'email': user.email,
                                         'is_admin': user.is_admin})

        existing = User.query.filter(User.email == email, User.id != user_id).first()
        if existing:
            flash('Email is already in use by another user', 'danger')
            return render_template('dashboard/edit_user.html',
                                   user={'id': user.id, 'name': user.name, 'email': user.email,
                                         'is_admin': user.is_admin})

        user.name = name
        user.email = email
        user.is_admin = is_admin
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('dashboard.user_detail', user_id=user_id))

    return render_template('dashboard/edit_user.html',
                           user={'id': user.id, 'name': user.name, 'email': user.email,
                                 'is_admin': user.is_admin})


@dashboard_bp.route('/projects')
@login_required
@admin_required
def projects():
    """Project management dashboard."""
    projects_q = db.session.query(
        Project,
        User.name,
        func.count(Assessment.id).label('assessment_count'),
    ).join(User, User.id == Project.user_id).outerjoin(
        Assessment, Assessment.project_id == Project.id
    ).group_by(Project.id).order_by(Project.created_at.desc()).all()

    projects_data = [_project_to_dict(p, user_name=uname) | {'assessment_count': ac}
                     for p, uname, ac in projects_q]

    return render_template('dashboard/projects.html', projects=projects_data)


@dashboard_bp.route('/assessments')
@login_required
@admin_required
def assessments():
    """Assessment management dashboard."""
    assessments_q = db.session.query(Assessment, Project.name, User.name).join(
        Project, Project.id == Assessment.project_id
    ).join(User, User.id == Project.user_id).order_by(Assessment.created_at.desc()).all()

    assessments_data = [_assessment_to_dict(a, project_name=pname, user_name=uname)
                        for a, pname, uname in assessments_q]

    return render_template('dashboard/assessments.html', assessments=assessments_data)


@dashboard_bp.route('/analytics')
@login_required
@admin_required
@cache.cached(timeout=300, key_prefix='dashboard_analytics')
def analytics():
    """Analytics dashboard with charts and statistics."""
    sdg_scores_rows = db.session.query(
        SdgGoal.number,
        SdgGoal.name,
        func.avg(SdgScore.total_score).label('avg_score'),
        SdgGoal.color_code
    ).join(SdgScore, SdgScore.sdg_id == SdgGoal.id).group_by(SdgGoal.id).order_by(SdgGoal.number).all()
    sdg_scores = [{'number': r[0], 'name': r[1], 'avg_score': r[2], 'color_code': r[3]}
                  for r in sdg_scores_rows]

    monthly_counts_rows = db.session.query(
        func.strftime('%Y-%m', Assessment.created_at).label('month'),
        func.count().label('count')
    ).group_by('month').order_by('month').all()
    monthly_counts = [{'month': r[0], 'count': r[1]} for r in monthly_counts_rows]

    project_types_rows = db.session.query(
        Project.project_type,
        func.count().label('count')
    ).group_by(Project.project_type).order_by(func.count().desc()).all()
    project_types = [{'project_type': r[0], 'count': r[1]} for r in project_types_rows]

    score_distribution = []

    return render_template(
        'dashboard/analytics.html',
        sdg_scores=sdg_scores,
        monthly_counts=monthly_counts,
        project_types=project_types,
        score_distribution=score_distribution,
    )


@dashboard_bp.route('/sdg-analysis')
@login_required
@admin_required
def sdg_analysis():
    """SDG analysis page (alias for analytics)."""
    return redirect(url_for('dashboard.analytics'))


@dashboard_bp.route('/project-comparison')
@login_required
@admin_required
def project_comparison():
    """Project comparison page."""
    return redirect(url_for('dashboard.projects'))


@dashboard_bp.route('/generate-report')
@login_required
@admin_required
def generate_report():
    """Report generation page."""
    return redirect(url_for('dashboard.analytics'))


@dashboard_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Application settings."""
    return render_template('dashboard/settings.html')


@dashboard_bp.route('/sdg-management')
@login_required
@admin_required
def sdg_management():
    """Manage SDG goals and relationships."""
    goals = SdgGoal.query.order_by(SdgGoal.number).all()
    goals_data = [{'id': g.id, 'number': g.number, 'name': g.name,
                   'color_code': g.color_code, 'description': g.description}
                  for g in goals]

    relationships_q = SdgRelationship.query.all()
    relationships_data = []
    for rel in relationships_q:
        relationships_data.append({
            'id': rel.id,
            'source_sdg_id': rel.source_sdg_id,
            'target_sdg_id': rel.target_sdg_id,
            'strength': rel.strength,
            'source_number': rel.source_goal.number if rel.source_goal else None,
            'source_name': rel.source_goal.name if rel.source_goal else None,
            'target_number': rel.target_goal.number if rel.target_goal else None,
            'target_name': rel.target_goal.name if rel.target_goal else None,
        })

    return render_template(
        'dashboard/sdg_management.html',
        goals=goals_data,
        relationships=relationships_data,
    )


@dashboard_bp.route('/question-management')
@login_required
@admin_required
def question_management():
    """Manage assessment questions."""
    questions_q = SdgQuestion.query.order_by(SdgQuestion.display_order).all()
    questions_data = [{
        'id': q.id,
        'text': q.text,
        'type': q.type,
        'sdg_id': q.sdg_id,
        'sdg_number': q.sdg.number if q.sdg else None,
        'sdg_name': q.sdg.name if q.sdg else None,
        'display_order': q.display_order,
        'max_score': q.max_score,
    } for q in questions_q]

    goals = SdgGoal.query.order_by(SdgGoal.number).all()
    goals_data = [{'id': g.id, 'number': g.number, 'name': g.name} for g in goals]

    return render_template(
        'dashboard/question_management.html',
        questions=questions_data,
        goals=goals_data,
    )
