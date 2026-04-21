from flask import abort
from app.utils.db import get_db
import logging

logger = logging.getLogger(__name__)

def get_projects(user_id, page=1, per_page=10, filters=None):
    """Get paginated projects for a user with optional filtering."""
    conn = get_db()
    sql = "SELECT * FROM projects WHERE user_id = ?"
    params = [user_id]
    if filters:
        if 'project_type' in filters and filters['project_type']:
            sql += " AND project_type = ?"
            params.append(filters['project_type'])
        if 'status' in filters and filters['status']:
            sql += " AND status = ?"
            params.append(filters['status'])
        if 'search' in filters and filters['search']:
            sql += " AND (name LIKE ? OR description LIKE ?)"
            search = f"%{filters['search']}%"
            params.extend([search, search])
    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    projects = conn.execute(sql, tuple(params)).fetchall()
    # conn.close() removed; teardown handles DB connection.
    return [dict(row) for row in projects]

def get_project(project_id, user_id=None):
    """Get a project by ID, optionally checking ownership."""
    conn = get_db()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project:
        # conn.close() removed; teardown handles DB connection.
        abort(404)
    if user_id is not None and project['user_id'] != user_id:
        logger.warning(f"User {user_id} attempted to access project {project_id} without permission")
        # conn.close() removed; teardown handles DB connection.
        abort(403)
    result = dict(project)
    # conn.close() removed; teardown handles DB connection.
    return result

def create_project(data, user_id):
    """Create a new project."""
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO projects (name, description, project_type, location, size_sqm, user_id) VALUES (?, ?, ?, ?, ?, ?)',
            (
                data['name'],
                data.get('description', ''),
                data.get('project_type'),
                data.get('location'),
                data.get('size_sqm'),
                user_id
            )
        )
        conn.commit()
        project = conn.execute('SELECT * FROM projects WHERE rowid = last_insert_rowid()').fetchone()
        logger.info(f"Project {project['id']} created by user {user_id}")
        result = dict(project)
        # conn.close() removed; teardown handles DB connection.
        return result
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating project: {str(e)}")
        # conn.close() removed; teardown handles DB connection.
        raise

def update_project(project_id, data, user_id):
    """Update an existing project."""
    conn = get_db()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project or project['user_id'] != user_id:
        # conn.close() removed; teardown handles DB connection.
        abort(403)
    try:
        fields = []
        params = []
        if 'name' in data:
            fields.append('name = ?')
            params.append(data['name'])
        if 'description' in data:
            fields.append('description = ?')
            params.append(data['description'])
        if 'project_type' in data:
            fields.append('project_type = ?')
            params.append(data['project_type'])
        if 'location' in data:
            fields.append('location = ?')
            params.append(data['location'])
        if 'size_sqm' in data:
            fields.append('size_sqm = ?')
            params.append(data['size_sqm'])
        if 'status' in data:
            fields.append('status = ?')
            params.append(data['status'])
        if not fields:
            # conn.close() removed; teardown handles DB connection.
            return dict(project)
        params.append(project_id)
        conn.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", tuple(params))
        conn.commit()
        logger.info(f"Project {project_id} updated by user {user_id}")
        updated_project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
        result = dict(updated_project)
        # conn.close() removed; teardown handles DB connection.
        return result
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating project {project_id}: {str(e)}")
        # conn.close() removed; teardown handles DB connection.
        raise

def delete_project(project_id, user_id):
    """Delete a project."""
    conn = get_db()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project or project['user_id'] != user_id:
        # conn.close() removed; teardown handles DB connection.
        abort(403)
    try:
        conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        conn.commit()
        logger.info(f"Project {project_id} deleted by user {user_id}")
        # conn.close() removed; teardown handles DB connection.
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        # conn.close() removed; teardown handles DB connection.
        raise