# tests/test_project_service.py
"""Tests for the project service layer (SQLAlchemy ORM backed)."""
import pytest
from werkzeug.exceptions import NotFound, Forbidden

from app.models.project import Project
from app.services.project_service import (
    get_projects, get_project, create_project, update_project, delete_project,
)


def _make_project(session, user_id, name='Proj', **kwargs):
    project = Project(name=name, user_id=user_id, **kwargs)
    session.add(project)
    session.commit()
    return project


# ---------------------------------------------------------------------------
# get_projects
# ---------------------------------------------------------------------------

def test_get_projects_returns_list(session, test_user):
    _make_project(session, test_user.id, name='Proj', project_type='commercial')
    result = get_projects(user_id=test_user.id)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['name'] == 'Proj'


def test_get_projects_empty(session, test_user):
    result = get_projects(user_id=test_user.id)
    assert result == []


# ---------------------------------------------------------------------------
# get_project
# ---------------------------------------------------------------------------

def test_get_project_found(session, test_user):
    project = _make_project(session, test_user.id, name='My Proj',
                            project_type='residential', location='Paris', size_sqm=200.0)
    result = get_project(project_id=project.id, user_id=test_user.id)
    assert result['id'] == project.id
    assert result['name'] == 'My Proj'


def test_get_project_not_found_raises_404(session):
    with pytest.raises(NotFound):
        get_project(project_id=999999)


def test_get_project_wrong_user_raises_403(session, test_user):
    project = _make_project(session, test_user.id, name='Other Proj')
    with pytest.raises(Forbidden):
        get_project(project_id=project.id, user_id=test_user.id + 1)


# ---------------------------------------------------------------------------
# create / update
# ---------------------------------------------------------------------------

def test_create_project(session, test_user):
    result = create_project({'name': 'Created', 'project_type': 'commercial'}, test_user.id)
    assert result['name'] == 'Created'
    assert result['user_id'] == test_user.id
    assert Project.query.filter_by(name='Created').count() == 1


def test_update_project(session, test_user):
    project = _make_project(session, test_user.id, name='Before')
    result = update_project(project.id, {'name': 'After'}, test_user.id)
    assert result['name'] == 'After'


def test_update_project_wrong_user_raises_403(session, test_user):
    project = _make_project(session, test_user.id, name='X')
    with pytest.raises(Forbidden):
        update_project(project.id, {'name': 'Y'}, test_user.id + 1)


# ---------------------------------------------------------------------------
# delete_project
# ---------------------------------------------------------------------------

def test_delete_project_success(session, test_user):
    project = _make_project(session, test_user.id, name='Del Proj')
    result = delete_project(project_id=project.id, user_id=test_user.id)
    assert result is True
    assert get_project_silently(project.id) is None


def test_delete_project_wrong_user_raises_403(session, test_user):
    project = _make_project(session, test_user.id, name='Del Proj')
    with pytest.raises(Forbidden):
        delete_project(project_id=project.id, user_id=test_user.id + 1)


def get_project_silently(project_id):
    from app import db
    return db.session.get(Project, project_id)
