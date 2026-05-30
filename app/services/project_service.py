from flask import abort
from app import db
from app.models.project import Project
import logging

logger = logging.getLogger(__name__)


def _to_dict(project):
    """Serialize a Project ORM object to a plain dict."""
    return {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'project_type': project.project_type,
        'location': project.location,
        'size_sqm': project.size_sqm,
        'user_id': project.user_id,
        'created_at': project.created_at,
        'updated_at': project.updated_at,
        'start_date': project.start_date,
        'end_date': project.end_date,
        'budget': project.budget,
        'sector': project.sector,
        'status': project.status,
    }


def get_projects(user_id, page=1, per_page=10, filters=None):
    """Get paginated projects for a user with optional filtering."""
    query = Project.query.filter_by(user_id=user_id)
    if filters:
        if filters.get('project_type'):
            query = query.filter_by(project_type=filters['project_type'])
        if filters.get('status'):
            query = query.filter_by(status=filters['status'])
        if filters.get('search'):
            search = f"%{filters['search']}%"
            query = query.filter(
                db.or_(Project.name.ilike(search), Project.description.ilike(search))
            )
    query = query.order_by(Project.created_at.desc())
    projects = query.limit(per_page).offset((page - 1) * per_page).all()
    return [_to_dict(p) for p in projects]


def get_project(project_id, user_id=None):
    """Get a project by ID, optionally checking ownership."""
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)
    if user_id is not None and project.user_id != user_id:
        logger.warning(f"User {user_id} attempted to access project {project_id} without permission")
        abort(403)
    return _to_dict(project)


def create_project(data, user_id):
    """Create a new project."""
    try:
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            project_type=data.get('project_type'),
            location=data.get('location'),
            size_sqm=data.get('size_sqm'),
            user_id=user_id,
        )
        db.session.add(project)
        db.session.commit()
        logger.info(f"Project {project.id} created by user {user_id}")
        return _to_dict(project)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating project: {str(e)}")
        raise


def update_project(project_id, data, user_id):
    """Update an existing project."""
    project = db.session.get(Project, project_id)
    if not project or project.user_id != user_id:
        abort(403)
    try:
        for field in ('name', 'description', 'project_type', 'location', 'size_sqm', 'status'):
            if field in data:
                setattr(project, field, data[field])
        db.session.commit()
        logger.info(f"Project {project_id} updated by user {user_id}")
        return _to_dict(project)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating project {project_id}: {str(e)}")
        raise


def delete_project(project_id, user_id):
    """Delete a project."""
    project = db.session.get(Project, project_id)
    if not project or project.user_id != user_id:
        abort(403)
    try:
        db.session.delete(project)
        db.session.commit()
        logger.info(f"Project {project_id} deleted by user {user_id}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        raise
