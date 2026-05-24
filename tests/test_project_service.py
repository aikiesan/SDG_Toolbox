# tests/test_project_service.py
import pytest
from unittest.mock import patch, MagicMock
from werkzeug.exceptions import NotFound, Forbidden


class FakeRow(dict):
    """Minimal sqlite3.Row substitute — supports dict() conversion and key access."""

    def keys(self):
        return super().keys()


def make_conn(*rows):
    """Return a mock DB connection whose cursor returns the given FakeRow dicts."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    fake_rows = [FakeRow(r) for r in rows]
    mock_cursor.fetchall.return_value = fake_rows
    mock_cursor.fetchone.return_value = fake_rows[0] if fake_rows else None
    mock_conn.execute.return_value = mock_cursor
    return mock_conn


# ---------------------------------------------------------------------------
# get_projects
# ---------------------------------------------------------------------------

def test_get_projects_returns_list(app):
    row = {'id': 1, 'name': 'Proj', 'user_id': 1, 'project_type': 'commercial',
           'description': '', 'location': '', 'size_sqm': None, 'status': 'active',
           'created_at': None, 'budget': None, 'sector': None,
           'start_date': None, 'end_date': None}
    with app.app_context():
        with patch('app.services.project_service.get_db', return_value=make_conn(row)):
            from app.services.project_service import get_projects
            result = get_projects(user_id=1)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['name'] == 'Proj'


def test_get_projects_empty(app):
    with app.app_context():
        with patch('app.services.project_service.get_db', return_value=make_conn()):
            from app.services.project_service import get_projects
            result = get_projects(user_id=1)
    assert result == []


# ---------------------------------------------------------------------------
# get_project
# ---------------------------------------------------------------------------

def test_get_project_found(app):
    row = {'id': 5, 'name': 'My Proj', 'user_id': 7, 'project_type': 'residential',
           'description': '', 'location': 'Paris', 'size_sqm': 200.0, 'status': 'active',
           'created_at': None, 'budget': None, 'sector': None,
           'start_date': None, 'end_date': None}
    with app.app_context():
        with patch('app.services.project_service.get_db', return_value=make_conn(row)):
            from app.services.project_service import get_project
            result = get_project(project_id=5, user_id=7)
    assert result['id'] == 5
    assert result['name'] == 'My Proj'


def test_get_project_not_found_raises_404(app):
    with app.app_context():
        with patch('app.services.project_service.get_db', return_value=make_conn()):
            from app.services.project_service import get_project
            with pytest.raises(NotFound):
                get_project(project_id=999)


def test_get_project_wrong_user_raises_403(app):
    row = {'id': 5, 'name': 'Other Proj', 'user_id': 99, 'project_type': 'commercial',
           'description': '', 'location': '', 'size_sqm': None, 'status': 'active',
           'created_at': None, 'budget': None, 'sector': None,
           'start_date': None, 'end_date': None}
    with app.app_context():
        with patch('app.services.project_service.get_db', return_value=make_conn(row)):
            from app.services.project_service import get_project
            with pytest.raises(Forbidden):
                get_project(project_id=5, user_id=1)  # user_id=1 ≠ row['user_id']=99


# ---------------------------------------------------------------------------
# delete_project
# ---------------------------------------------------------------------------

def test_delete_project_success(app):
    row = {'id': 3, 'name': 'Del Proj', 'user_id': 2, 'project_type': 'commercial',
           'description': '', 'location': '', 'size_sqm': None, 'status': 'active',
           'created_at': None, 'budget': None, 'sector': None,
           'start_date': None, 'end_date': None}
    with app.app_context():
        with patch('app.services.project_service.get_db', return_value=make_conn(row)):
            from app.services.project_service import delete_project
            result = delete_project(project_id=3, user_id=2)
    assert result is True


def test_delete_project_wrong_user_raises_403(app):
    row = {'id': 3, 'name': 'Del Proj', 'user_id': 99, 'project_type': 'commercial',
           'description': '', 'location': '', 'size_sqm': None, 'status': 'active',
           'created_at': None, 'budget': None, 'sector': None,
           'start_date': None, 'end_date': None}
    with app.app_context():
        with patch('app.services.project_service.get_db', return_value=make_conn(row)):
            from app.services.project_service import delete_project
            with pytest.raises(Forbidden):
                delete_project(project_id=3, user_id=1)
