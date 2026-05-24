# tests/test_assessment_service.py
import pytest
from datetime import datetime

from app.models.assessment import Assessment
from app.models.project import Project
from app.services.assessment_service import (
    get_assessment,
    get_project_for_assessment,
    create_assessment,
    update_assessment,
)


# ---------------------------------------------------------------------------
# get_assessment
# ---------------------------------------------------------------------------

def test_get_assessment_found(session, test_project):
    a = Assessment(
        project_id=test_project.id,
        user_id=test_project.user_id,
        status='draft',
    )
    session.add(a)
    session.flush()

    result = get_assessment(a.id)
    assert result is not None
    assert result.id == a.id


def test_get_assessment_not_found(session):
    result = get_assessment(999999)
    assert result is None


# ---------------------------------------------------------------------------
# get_project_for_assessment
# ---------------------------------------------------------------------------

def test_get_project_for_assessment(session, test_project):
    a = Assessment(
        project_id=test_project.id,
        user_id=test_project.user_id,
        status='draft',
    )
    session.add(a)
    session.flush()

    project = get_project_for_assessment(a.id)
    assert project is not None
    assert project.id == test_project.id


def test_get_project_for_assessment_not_found(session):
    result = get_project_for_assessment(999999)
    assert result is None


# ---------------------------------------------------------------------------
# create_assessment
# ---------------------------------------------------------------------------

def test_create_assessment(session, test_project):
    a = create_assessment(test_project.id, test_project.user_id)
    assert a is not None
    assert a.status == 'draft'
    assert a.project_id == test_project.id
    assert a.user_id == test_project.user_id


def test_create_assessment_persisted(session, test_project):
    a = create_assessment(test_project.id, test_project.user_id)
    fetched = get_assessment(a.id)
    assert fetched is not None
    assert fetched.id == a.id


# ---------------------------------------------------------------------------
# update_assessment
# ---------------------------------------------------------------------------

def test_update_assessment_status(session, test_project):
    a = Assessment(
        project_id=test_project.id,
        user_id=test_project.user_id,
        status='draft',
    )
    session.add(a)
    session.flush()

    updated = update_assessment(a.id, {'status': 'completed'})
    assert updated is not None
    assert updated.status == 'completed'


def test_update_assessment_not_found(session):
    result = update_assessment(999999, {'status': 'completed'})
    assert result is None


def test_update_assessment_ignores_unknown_fields(session, test_project):
    a = Assessment(
        project_id=test_project.id,
        user_id=test_project.user_id,
        status='draft',
    )
    session.add(a)
    session.flush()

    # Should not raise even if key doesn't exist on the model
    updated = update_assessment(a.id, {'nonexistent_field': 'value', 'status': 'completed'})
    assert updated.status == 'completed'
