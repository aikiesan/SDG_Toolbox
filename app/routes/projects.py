"""
Project management routes.
Handles creating, viewing, editing, and deleting projects.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify, json, current_app, session
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.assessment import Assessment, SdgScore
from app.models.sdg import SdgGoal
from app import db
from datetime import datetime
from ..scoring_logic import calculate_scores_python  # Import the scoring function
from app.utils.sdg_data import SDG_INFO  # Import SDG_INFO for the results page
from app.forms.project_forms import ProjectForm

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/', strict_slashes=False)
@login_required
def index():
    """Show all projects for the current user."""
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    search_term = request.args.get('search', '')
    
    # Handle combined sort parameters from the frontend
    if sort in ['name_desc', 'budget_desc', 'budget_asc', 'date_desc', 'date_asc', 'assessment_count_desc', 'assessment_count_asc']:
        if sort.endswith('_desc'):
            order = 'desc'
            sort = sort.replace('_desc', '')
        elif sort.endswith('_asc'):
            order = 'asc'
            sort = sort.replace('_asc', '')
    project_type = request.args.get('type')
    status = request.args.get('status')
    min_budget = request.args.get('min_budget', type=float)
    max_budget = request.args.get('max_budget', type=float)
    
    query = Project.query.filter_by(user_id=current_user.id)
    
    # Apply search filter
    if search_term:
        query = query.filter(Project.name.ilike(f'%{search_term}%'))
    
    # Apply filters
    if project_type:
        query = query.filter_by(project_type=project_type)
    if status:
        query = query.filter_by(status=status)
    if min_budget is not None:
        query = query.filter(Project.budget >= min_budget)
    if max_budget is not None:
        query = query.filter(Project.budget <= max_budget)
    
    # Apply sorting
    if sort == 'name':
        if order == 'desc':
            current_sort = 'name_desc'
            query = query.order_by(Project.name.desc())
        else:
            current_sort = 'name'
            query = query.order_by(Project.name.asc())
    elif sort == 'budget':
        if order == 'desc':
            current_sort = 'budget_desc'
            query = query.order_by(Project.budget.desc())
        else:
            current_sort = 'budget_asc'
            query = query.order_by(Project.budget.asc())
    elif sort == 'assessment_count':
        # Join with assessments to get count for sorting
        from sqlalchemy import func
        query = query.outerjoin(Assessment).group_by(Project.id)
        if order == 'desc':
            current_sort = 'assessment_count_desc'
            query = query.order_by(func.count(Assessment.id).desc())
        else:
            current_sort = 'assessment_count_asc'
            query = query.order_by(func.count(Assessment.id).asc())
    else:  # default to created_at
        if order == 'desc':
            current_sort = 'date_desc'
            query = query.order_by(Project.created_at.desc())
        else:
            current_sort = 'date_asc'
            query = query.order_by(Project.created_at.asc())
    
    projects = query.paginate(page=page, per_page=10)
    return render_template('projects/index.html', 
                         projects=projects, 
                         search_term=search_term,
                         current_sort=current_sort)

@projects_bp.route('/<int:id>')
@login_required
def show(id):
    """Show a specific project."""
    project = db.session.get(Project, id)
    if project is None:
        abort(404)
    if project.user_id != current_user.id:
        abort(403)  # Forbidden
    
    # Get assessments for this project
    from app.models.assessment import Assessment
    assessments = Assessment.query.filter_by(project_id=project.id).order_by(Assessment.id.desc()).all()
    
    # Debug log to verify what is being fetched
    print(f"DEBUG: Found {len(assessments)} assessments for project {id}")
    for a in assessments:
        print(f"DEBUG: ID {a.id}, Type: {a.assessment_type}, Status: {a.status}")
    
    return render_template('projects/show.html', project=project, assessments=assessments)

@projects_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """Create a new project."""
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            project_type=form.project_type.data,
            location=form.location.data,
            size_sqm=form.size_sqm.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            sector=form.sector.data,
            user_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully', 'success')
        return redirect(url_for('projects.show', id=project.id))
    return render_template('projects/new.html', form=form)

@projects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a project."""
    project = db.session.get(Project, id)
    if project is None:
        abort(404)
    if project.user_id != current_user.id:
        abort(403)  # Forbidden
    
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        db.session.commit()
        flash('Project updated successfully', 'success')
        return redirect(url_for('projects.show', id=project.id))
    return render_template('projects/edit.html', form=form, project=project)

@projects_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a project."""
    project = db.session.get(Project, id)
    if project is None:
        abort(404)
    if project.user_id != current_user.id:
        abort(403)  # Forbidden
    
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully', 'success')
    return redirect(url_for('projects.index'))

@projects_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    """Update project status."""
    project = db.session.get(Project, id)
    if project is None:
        abort(404)
    if project.user_id != current_user.id:
        abort(403)  # Forbidden
    
    status = request.form.get('status')
    if status not in ['planning', 'in_progress', 'completed', 'on_hold', 'cancelled']:
        flash('Invalid status', 'error')
        return redirect(url_for('projects.show', id=id))
    
    project.status = status
    db.session.commit()
    flash(f'Project status updated to {status.replace("_", " ")}', 'success')
    return redirect(url_for('projects.show', id=id))


@projects_bp.route('/<int:id>/export')
@login_required
def export(id):
    """Export project data."""
    project = db.session.get(Project, id)
    if project is None:
        abort(404)
    if project.user_id != current_user.id:
        abort(403)  # Forbidden
    
    format = request.args.get('format', 'csv')
    if format == 'csv':
        # Generate CSV
        import csv
        from io import StringIO
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['Project Name', 'Description', 'Type', 'Location', 'Size (sqm)', 'Budget'])
        cw.writerow([
            project.name,
            project.description or '',
            project.project_type,
            project.location,
            project.size_sqm,
            project.budget
        ])
        output = si.getvalue()
        return current_app.response_class(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=project_{id}.csv'}
        )
    elif format == 'pdf':
        # Generate PDF
        from weasyprint import HTML
        html = render_template('projects/export_pdf.html', project=project)
        pdf = HTML(string=html).write_pdf()
        return current_app.response_class(
            pdf,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=project_{id}.pdf'}
        )
    else:
        abort(400)  # Bad Request

@projects_bp.route('/<int:id>/duplicate', methods=['POST'])
@login_required
def duplicate(id):
    """Duplicate a project."""
    project = db.session.get(Project, id)
    if project is None:
        abort(404)
    if project.user_id != current_user.id:
        abort(403)  # Forbidden
    
    new_project = Project(
        name=f'Copy of {project.name}',
        description=project.description,
        project_type=project.project_type,
        location=project.location,
        size_sqm=project.size_sqm,
        start_date=project.start_date,
        end_date=project.end_date,
        budget=project.budget,
        sector=project.sector,
        user_id=current_user.id
    )
    db.session.add(new_project)
    db.session.commit()
    flash('Project duplicated successfully', 'success')
    return redirect(url_for('projects.show', id=new_project.id))

@projects_bp.route('/<int:id>/assessments/new', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def new_assessment(id):
    """Create a new assessment for a project. Handles GET (show form) and POST (create or show errors)."""
    from app.models.assessment import Assessment
    project = Project.query.filter_by(id=id, user_id=current_user.id).first()
    if not project:
        flash('Project not found or you don\'t have permission to access it', 'danger')
        return redirect(url_for('projects.index'))

    if request.method == 'POST':
        # Example: validate a required field (e.g., 'assessment_name')
        assessment_name = request.form.get('assessment_name')
        if not assessment_name:
            flash('Assessment name is required.', 'danger')
            # Render a template for the assessment creation form with error
            return render_template('projects/new.html', project=project), 200
        # You can add more validation here as needed
        assessment = Assessment(project_id=id, user_id=current_user.id, status='draft', name=assessment_name)
        db.session.add(assessment)
        db.session.commit()
        assessment_id = assessment.id
        return redirect(url_for('assessments.questionnaire_step', project_id=id, assessment_id=assessment_id, step=1))

    # GET: show the form for creating an assessment
    return render_template('projects/new.html', project=project)

@projects_bp.route('/api/test', methods=['GET'])
def test_api():
    """Test API endpoint."""
    return jsonify({"message": "API is working"})

@projects_bp.route('/save-progress', methods=['POST'])
@login_required
def save_progress():
    """Save expert assessment progress (session-based authentication)."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'error': 'No project ID provided'}), 400
    
    # Verify user owns the project
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'error': 'Project not found or access denied'}), 404
    
    # For expert assessments, we can store progress in session or temporary storage
    # Since these are typically completed in one session, we'll use session storage
    session_key = f'expert_assessment_progress_{project_id}'
    if 'expert_assessment_progress' not in session:
        session['expert_assessment_progress'] = {}
    
    session['expert_assessment_progress'][str(project_id)] = {
        'section_id': data.get('section_id'),
        'section_data': data.get('section_data'),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify({'message': 'Progress saved successfully'}), 200

@projects_bp.route('/project/<int:project_id>/expert_assessment/save', methods=['POST'])
@login_required
def save_expert_assessment(project_id):
    """Save an expert assessment for a project."""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        assessment_data_json = request.form.get('assessment-data')

        if not assessment_data_json:
            flash('Error: Missing assessment data.', 'danger')
            return redirect(url_for('projects.view_project', project_id=project.id))

        try:
            # Parse the raw answers from the hidden input
            raw_expert_answers = json.loads(assessment_data_json)
        except json.JSONDecodeError:
            flash('Error: Invalid assessment data format.', 'danger')
            return redirect(url_for('projects.start_expert_assessment', project_id=project.id))

        # Create Assessment Record
        new_assessment = Assessment(
            project_id=project.id,
            user_id=current_user.id,
            status='completed',
            assessment_type='expert',
            raw_expert_data=raw_expert_answers,
            completed_at=datetime.utcnow()
        )
        db.session.add(new_assessment)

        # Calculate Scores using the imported function
        try:
            calculated_scores = calculate_scores_python(raw_expert_answers)
            if not isinstance(calculated_scores, list):
                raise ValueError("Scoring function did not return a list of scores")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error calculating expert scores for project {project_id}: {e}")
            flash(f'Error calculating scores: {e}', 'danger')
            return redirect(url_for('projects.start_expert_assessment', project_id=project.id))

        # Create SdgScore Records
        total_sum = 0
        valid_scores_count = 0
        sdg_goals_map = {goal.number: goal.id for goal in SdgGoal.query.all()}

        for score_data in calculated_scores:
            sdg_number = score_data.get('number')
            sdg_goal_id = sdg_goals_map.get(sdg_number)

            if sdg_goal_id is None:
                current_app.logger.warning(f"Could not find SDG Goal ID for number {sdg_number}. Skipping score.")
                continue

            sdg_score_record = SdgScore(
                sdg_id=sdg_goal_id,
                total_score=score_data.get('total_score'),
                notes=raw_expert_answers.get(f'sdg{sdg_number}_notes', ''),  # Get notes from raw form data
                direct_score=score_data.get('direct_score'),  # Get these from the scoring function if available
                bonus_score=score_data.get('bonus_score')     # Get these from the scoring function if available
            )
            new_assessment.sdg_scores.append(sdg_score_record)

            # For calculating overall score
            if score_data.get('total_score') is not None:
                total_sum += score_data['total_score']
                valid_scores_count += 1

        # Calculate overall score
        new_assessment.overall_score = (total_sum / valid_scores_count) if valid_scores_count > 0 else 0

        # Final Save
        try:
            db.session.commit()
            flash('Expert Assessment saved successfully!', 'success')
            print(f"DEBUG: Redirecting to projects.show_expert_results with assessment_id={new_assessment.id}")
            return redirect(url_for('projects.show_expert_results', assessment_id=new_assessment.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving expert assessment to DB for project {project_id}: {e}")
            flash(f'Error saving assessment to database: {e}', 'danger')
            return redirect(url_for('projects.start_expert_assessment', project_id=project.id))

    return redirect(url_for('projects.view_project', project_id=project.id))

@projects_bp.route('/expert-assessment/<int:assessment_id>/results')
@login_required
def show_expert_results(assessment_id):
    """Display the results of an expert assessment."""
    # 1. Fetch the specific Assessment, ensuring it's an 'expert' type
    assessment = Assessment.query.filter_by(id=assessment_id, assessment_type='expert').first_or_404()
    project = assessment.project  # Access the related project via backref

    # Permission Check (User must own the project)
    if project.user_id != current_user.id:
        flash('You do not have permission to view this assessment.', 'danger')
        return redirect(url_for('projects.index'))

    # 2. Retrieve the calculated SDG scores with related SDG goal information
    sdg_scores_query = db.session.query(
        SdgScore.total_score,
        SdgScore.notes,
        SdgScore.direct_score,
        SdgScore.bonus_score,
        SdgGoal.number,
        SdgGoal.name,
        SdgGoal.color_code,
        SdgGoal.icon
    ).join(SdgGoal, SdgScore.sdg_id == SdgGoal.id)\
     .filter(SdgScore.assessment_id == assessment.id)\
     .order_by(SdgGoal.number)\
     .all()

    # Convert the query result into a list of dictionaries
    scores_data = []
    if sdg_scores_query:
        for score_row in sdg_scores_query:
            scores_data.append({
                'number': score_row.number,
                'name': score_row.name,
                'color_code': score_row.color_code or '#CCCCCC',  # Default color if none set
                'icon': score_row.icon,
                'total_score': round(score_row.total_score, 1) if score_row.total_score is not None else 0.0,
                'notes': score_row.notes or '',
                'direct_score': round(score_row.direct_score, 1) if score_row.direct_score is not None else None,
                'bonus_score': round(score_row.bonus_score, 1) if score_row.bonus_score is not None else None
            })
    else:
        flash('Could not retrieve SDG scores for this assessment.', 'warning')

    # 3. Render the results template with all necessary data
    return render_template('projects/expert_results.html',
                         assessment=assessment,
                         project=project,
                         scores_data=scores_data,
                         scores_json=json.dumps(scores_data),
                         SDG_INFO_json=json.dumps(SDG_INFO))  # Add SDG_INFO to the template context

@projects_bp.route('/project/<int:project_id>/expert-assessment')
@login_required
def expert_assessment(project_id):
    """Start a new expert assessment for a project."""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    return render_template('questionnaire/expert_assessment.html', project=project)
