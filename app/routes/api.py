"""
API routes for the application.
Provides JSON endpoints for AJAX requests and external integrations.
"""

import jwt as pyjwt
print("PYJWT MODULE PATH:", pyjwt.__file__)
import datetime
from flask import Blueprint, jsonify, request, session, current_app
from flask import g
from functools import wraps
from werkzeug.security import check_password_hash
from app import db as orm_db
from app.models.user import User
from app.models.project import Project
from app.models.assessment import Assessment, SdgScore
from app.models.sdg import SdgGoal, SdgQuestion
from app.models.response import QuestionResponse
from app.services.scoring_service import get_assessment_summary
import json
from sqlalchemy import text, func, select

api_bp = Blueprint('api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            data = pyjwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user_id = data['user_id']
        except:
            return jsonify({'error': 'Token is invalid'}), 401
            
        return f(*args, **kwargs)
    return decorated

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password'}), 400

    email = data.get('email')
    password_candidate = data.get('password')

    # Use SQLAlchemy to find the user
    user = orm_db.session.execute(
        select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if user and check_password_hash(user.password_hash, password_candidate):
        token = pyjwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({'token': token, 'user_id': user.id}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@api_bp.route('/projects', methods=['GET', 'POST'])
@token_required
def projects_handler():
    """GET: List all projects for the user. POST: Create a project."""
    user_id = g.user_id
    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Project name is required'}), 400
        
        new_project = Project(
            name=name,
            description=data.get('description'),
            project_type=data.get('project_type'),
            location=data.get('location'),
            size_sqm=float(data.get('size_sqm')) if data.get('size_sqm') else None,
            user_id=user_id,
            start_date=datetime.datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None,
            budget=float(data.get('budget')) if data.get('budget') else None,
            sector=data.get('sector')
        )
        orm_db.session.add(new_project)
        orm_db.session.commit()
        project_dict = {c.name: getattr(new_project, c.name) for c in new_project.__table__.columns}
        return jsonify(project_dict), 201

    # GET
    projects_orm = orm_db.session.query(
        Project, func.count(Assessment.id).label('assessment_count')
    ).outerjoin(Assessment, Project.id == Assessment.project_id)\
     .filter(Project.user_id == user_id)\
     .group_by(Project.id)\
     .order_by(Project.updated_at.desc())\
     .all()

    projects_list = []
    for project_obj, count in projects_orm:
        project_dict = {c.name: getattr(project_obj, c.name) for c in project_obj.__table__.columns}
        project_dict['assessment_count'] = count
        projects_list.append(project_dict)
    return jsonify(projects_list)

@api_bp.route('/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def project_detail_handler(project_id):
    """GET: Get project. PUT: Update project. DELETE: Delete project."""
    user_id = g.user_id
    project = orm_db.session.execute(
        select(Project).filter_by(id=project_id, user_id=user_id)
    ).scalar_one_or_none()

    if not project:
        return jsonify({'error': 'Project not found or access denied'}), 404

    if request.method == 'PUT':
        data = request.get_json() or {}
        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)
        project.project_type = data.get('project_type', project.project_type)
        project.location = data.get('location', project.location)
        project.size_sqm = float(data.get('size_sqm')) if data.get('size_sqm') is not None else project.size_sqm
        project.start_date = datetime.datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() if data.get('start_date') else project.start_date
        project.end_date = datetime.datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else project.end_date
        project.budget = float(data.get('budget')) if data.get('budget') is not None else project.budget
        project.sector = data.get('sector', project.sector)
        project.updated_at = datetime.datetime.utcnow()
        orm_db.session.commit()
        project_dict = {c.name: getattr(project, c.name) for c in project.__table__.columns}
        return jsonify(project_dict), 200

    elif request.method == 'DELETE':
        orm_db.session.delete(project)
        orm_db.session.commit()
        return '', 204

    # GET
    project_dict = {c.name: getattr(project, c.name) for c in project.__table__.columns}
    assessments_list = []
    for assess_obj in project.assessments:
        assess_dict = {c.name: getattr(assess_obj, c.name) for c in assess_obj.__table__.columns}
        assessments_list.append(assess_dict)
    project_dict['assessments'] = assessments_list
    return jsonify(project_dict)

@api_bp.route('/projects/<int:project_id>/assessments', methods=['POST'])
@token_required
def create_project_assessment(project_id):
    user_id = g.user_id
    project = orm_db.session.execute(
        select(Project).filter_by(id=project_id, user_id=user_id)
    ).scalar_one_or_none()
    
    if not project:
        return jsonify({'error': 'Project not found or access denied'}), 404

    data = request.get_json() or {}
    new_assessment = Assessment(
        project_id=project_id,
        user_id=user_id
    )
    orm_db.session.add(new_assessment)
    orm_db.session.commit()
    assessment_dict = {c.name: getattr(new_assessment, c.name) for c in new_assessment.__table__.columns}
    return jsonify(assessment_dict), 201

@api_bp.route('/assessments/<int:assessment_id>/finalize', methods=['POST'])
@token_required
def finalize_assessment_api(assessment_id):
    user_id = g.user_id
    assessment = orm_db.session.execute(
        select(Assessment).join(Project).filter(
            Assessment.id == assessment_id,
            Project.user_id == user_id
        )
    ).scalar_one_or_none()
    
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404
        
    assessment.status = 'completed'
    assessment.completed_at = datetime.datetime.utcnow()
    assessment.updated_at = datetime.datetime.utcnow()
    orm_db.session.commit()
    
    overall_score = 100  # Placeholder
    return jsonify({
        'message': 'Assessment finalized successfully',
        'overall_score': overall_score,
        'status': 'completed'
    }), 200

@api_bp.route('/assessments/<int:assessment_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def assessment_detail_api_handler(assessment_id):
    """Get, update, or delete a specific assessment."""
    user_id = g.user_id
    
    assessment = orm_db.session.execute(
        select(Assessment).join(Project).filter(
            Assessment.id == assessment_id,
            Project.user_id == user_id
        )
    ).scalar_one_or_none()
    
    if not assessment:
        return jsonify({'error': 'Assessment not found or access denied'}), 404
    
    if request.method == 'PUT':
        data = request.get_json() or {}
        
        if 'status' in data:
            assessment.status = data['status']
        if 'draft_data' in data:
            assessment.draft_data = json.dumps(data['draft_data'])  # Serialize dict to JSON string
        
        assessment.updated_at = datetime.datetime.utcnow()
        orm_db.session.commit()
        
        return jsonify({
            'id': assessment.id,
            'status': assessment.status,
            'draft_data': assessment.draft_data,
            'updated_at': assessment.updated_at.isoformat() if assessment.updated_at else None
        }), 200
    
    elif request.method == 'DELETE':
        orm_db.session.query(QuestionResponse).filter_by(assessment_id=assessment_id).delete()
        orm_db.session.query(SdgScore).filter_by(assessment_id=assessment_id).delete()
        orm_db.session.delete(assessment)
        orm_db.session.commit()
        return '', 204
    
    # GET request
    assessment_dict = {
        'id': assessment.id,
        'project_id': assessment.project_id,
        'user_id': assessment.user_id,
        'status': assessment.status,
        'draft_data': assessment.draft_data,
        'created_at': assessment.created_at.isoformat() if assessment.created_at else None,
        'updated_at': assessment.updated_at.isoformat() if assessment.updated_at else None,
        'project_name': assessment.project.name
    }
    
    # Include SDG scores if they exist
    scores = orm_db.session.query(SdgScore).filter_by(assessment_id=assessment_id).all()
    assessment_dict['scores'] = [{
        'id': score.id,
        'sdg_id': score.sdg_id,
        'total_score': score.total_score
    } for score in scores]
    
    return jsonify(assessment_dict)

@api_bp.route('/assessments/<int:assessment_id>/summary', methods=['GET'])
@token_required
def get_assessment_summary_route(assessment_id):
    """Get a summary of assessment results."""
    user_id = g.user_id
    
    # Verify ownership using ORM
    assessment = orm_db.session.execute(
        select(Assessment).join(Project).filter(
            Assessment.id == assessment_id,
            Project.user_id == user_id
        )
    ).scalar_one_or_none()
    
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404
    
    # Get assessment summary
    summary = get_assessment_summary(orm_db.session, assessment_id)
    
    return jsonify(summary)

@api_bp.route('/assessments/<int:assessment_id>/responses', methods=['POST'])
@token_required
def get_assessment_responses(assessment_id):
    """Get a summary of assessment results."""
    user_id = g.user_id
    
    # Verify ownership using ORM
    assessment = orm_db.session.execute(
        select(Assessment).join(Project).filter(
            Assessment.id == assessment_id,
            Project.user_id == user_id
        )
    ).scalar_one_or_none()
    
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404
    
    # Get assessment summary
    summary = get_assessment_summary(orm_db.session, assessment_id)
    return jsonify(summary)

@api_bp.route('/sdg/goals', methods=['GET'])
def get_sdg_goals():
    """Get all SDG goals."""
    goals = orm_db.session.query(SdgGoal).order_by(SdgGoal.number).all()
    goals_list = [{
        'id': goal.id,
        'number': goal.number,
        'title': goal.title,
        'description': goal.description
    } for goal in goals]
    return jsonify(goals_list)

@api_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_metrics_api():
    """Get dashboard metrics."""
    user_id = g.user_id
    
    # Get total projects
    total_projects = orm_db.session.query(func.count(Project.id))\
        .filter(Project.user_id == user_id).scalar()
    
    # Get total assessments
    total_assessments = orm_db.session.query(func.count(Assessment.id))\
        .join(Project).filter(Project.user_id == user_id).scalar()
    
    # Get completed assessments
    completed_assessments = orm_db.session.query(func.count(Assessment.id))\
        .join(Project).filter(
            Project.user_id == user_id,
            Assessment.status == 'completed'
        ).scalar()
    
    return jsonify({
        'total_projects': total_projects,
        'total_assessments': total_assessments,
        'completed_assessments': completed_assessments
    })

@api_bp.route('/sdg/relationships', methods=['GET'])
def get_sdg_relationships():
    """Get SDG relationships."""
    relationships = orm_db.session.execute(text('''
        SELECT r.*, g1.number as goal1_number, g2.number as goal2_number
        FROM sdg_relationships r
        JOIN sdg_goals g1 ON r.goal1_id = g1.id
        JOIN sdg_goals g2 ON r.goal2_id = g2.id
        ORDER BY g1.number, g2.number
    ''')).fetchall()
    
    relationships_list = [dict(rel) for rel in relationships]
    return jsonify(relationships_list)

@api_bp.route('/questionnaire/<int:assessment_id>/save', methods=['POST'])
@token_required
def save_questionnaire_response(assessment_id):
    """Save questionnaire responses."""
    user_id = g.user_id
    
    # Verify ownership using ORM
    assessment = orm_db.session.execute(
        select(Assessment).join(Project).filter(
            Assessment.id == assessment_id,
            Project.user_id == user_id
        )
    ).scalar_one_or_none()
    
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404
    
    data = request.get_json()
    if not data or 'responses' not in data:
        return jsonify({'error': 'No responses provided'}), 400
    
    responses = data['responses']
    if not isinstance(responses, list):
        return jsonify({'error': 'Responses must be a list'}), 400
    
    # Process each response
    for response in responses:
        question_id = response.get('question_id')
        response_text = response.get('response_text')
        score = response.get('score')
        
        if not question_id or not response_text or score is None:
            continue
        
        # Check if response already exists
        existing = orm_db.session.query(QuestionResponse).filter_by(
            assessment_id=assessment_id,
            question_id=question_id
        ).first()
        
        if existing:
            # Update existing response
            existing.response_text = response_text
            existing.score = score
            existing.updated_at = datetime.datetime.utcnow()
        else:
            # Insert new response
            new_response = QuestionResponse(
                assessment_id=assessment_id,
                question_id=question_id,
                response_text=response_text,
                score=score
            )
            orm_db.session.add(new_response)
    
    orm_db.session.commit()
    return jsonify({'message': 'Responses saved successfully'}), 200

@api_bp.route('/save-progress', methods=['POST'])
@token_required
def save_progress():
    """Save assessment progress."""
    user_id = g.user_id
    
    data = request.get_json()
    if not data or 'assessment_id' not in data:
        return jsonify({'error': 'No assessment ID provided'}), 400
    
    assessment_id = data['assessment_id']
    
    # Verify ownership using ORM
    assessment = orm_db.session.execute(
        select(Assessment).join(Project).filter(
            Assessment.id == assessment_id,
            Project.user_id == user_id
        )
    ).scalar_one_or_none()
    
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404
    
    # Save draft data
    draft_data = data.get('draft_data')
    if draft_data:
        assessment.draft_data = draft_data
        assessment.updated_at = datetime.datetime.utcnow()
        orm_db.session.commit()
    
    return jsonify({'message': 'Progress saved successfully'}), 200
