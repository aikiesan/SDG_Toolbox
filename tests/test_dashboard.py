"""
Tests for dashboard routes and admin functionality.

The dashboard is fully SQLAlchemy/ORM backed, so access-control, page-load, and
data-rendering assertions all run against the seeded test database.
"""

import pytest
from app.models.user import User
from app.models.project import Project
from app.models.assessment import Assessment, SdgScore
from app.models.sdg import SdgGoal
from datetime import datetime


class TestDashboardAccess:
    """Test dashboard access control."""

    def test_dashboard_requires_login(self, client):
        """Test that dashboard requires authentication."""
        response = client.get('/dashboard/')
        assert response.status_code == 302
        assert b'/auth/login' in response.data or response.location.endswith('/auth/login')

    def test_dashboard_requires_admin(self, client, test_user, auth):
        """Test that non-admin users cannot access dashboard."""
        auth.login(email=test_user.email, password='password')
        response = client.get('/dashboard/', follow_redirects=True)
        assert b'Administrator access required' in response.data or response.status_code == 403

    def test_admin_can_access_dashboard(self, client, admin_user, auth):
        """Test that admin users can access dashboard."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/')
        assert response.status_code == 200


class TestDashboardIndex:
    """Test the main dashboard index page."""

    def test_dashboard_displays_statistics(self, client, admin_user, auth):
        """Test that dashboard loads and shows admin stats."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/')
        assert response.status_code == 200
        assert b'Projects' in response.data or b'projects' in response.data
        assert b'Users' in response.data or b'users' in response.data

    def test_dashboard_shows_recent_activity(self, client, admin_user, auth):
        """Test that dashboard shows recent activity section."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/')
        assert response.status_code == 200
        assert b'Recent' in response.data or b'recent' in response.data

    def test_dashboard_shows_average_scores(self, client, admin_user, auth):
        """Test that dashboard displays score-related content."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/')
        assert response.status_code == 200
        assert b'Average' in response.data or b'average' in response.data or b'Score' in response.data


class TestDashboardUsers:
    """Test user management dashboard."""

    def test_users_list_displays_all_users(self, client, admin_user, auth, test_user, other_user):
        """The users list shows every user's email."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/users')
        assert response.status_code == 200
        assert test_user.email.encode() in response.data
        assert other_user.email.encode() in response.data

    def test_users_list_shows_statistics(self, client, admin_user, auth, test_user, multiple_projects):
        """The users list renders per-user project counts."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/users')
        assert response.status_code == 200
        # test_user owns the 5 multiple_projects; the row should show them.
        assert test_user.email.encode() in response.data
        assert b'>5<' in response.data  # project_count cell

    def test_user_detail_page(self, client, admin_user, auth, test_user, multiple_projects):
        """A user's detail page shows their name and project names."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get(f'/dashboard/users/{test_user.id}')
        assert response.status_code == 200
        assert test_user.name.encode() in response.data
        assert b'Test Project 1' in response.data

    def test_user_detail_not_found(self, client, admin_user, auth):
        """Test user detail page with non-existent user."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/users/99999', follow_redirects=True)
        assert response.status_code == 200

    def test_edit_user_page(self, client, admin_user, auth, test_user):
        """The edit form is pre-filled with the user's current values."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get(f'/dashboard/users/{test_user.id}/edit')
        assert response.status_code == 200
        assert test_user.email.encode() in response.data
        assert test_user.name.encode() in response.data

    def test_edit_user_updates_information(self, client, admin_user, auth, test_user):
        """Posting the edit form updates the user in the database."""
        from app import db
        from app.models.user import User
        auth.login(email=admin_user.email, password='adminpass')
        new_email = 'renamed_user@example.com'
        response = client.post(
            f'/dashboard/users/{test_user.id}/edit',
            data={'name': 'Renamed User', 'email': new_email},
            follow_redirects=True,
        )
        assert response.status_code == 200
        updated = db.session.get(User, test_user.id)
        assert updated.name == 'Renamed User'
        assert updated.email == new_email


class TestDashboardProjects:
    """Test project management dashboard."""

    def test_projects_list_loads(self, client, admin_user, auth):
        """Test that projects list page loads."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/projects')
        assert response.status_code == 200

    def test_projects_list_displays_all_projects(self, client, admin_user, auth, multiple_projects):
        """The projects list shows every project name."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/projects')
        assert response.status_code == 200
        assert b'Test Project 1' in response.data
        assert b'Test Project 5' in response.data

    def test_projects_list_shows_assessment_counts(self, client, admin_user, auth, test_project,
                                                    completed_assessment):
        """The projects list shows a project that has an assessment."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/projects')
        assert response.status_code == 200
        assert test_project.name.encode() in response.data


class TestDashboardAssessments:
    """Test assessment management dashboard."""

    def test_assessments_list_loads(self, client, admin_user, auth):
        """Test that assessments list page loads."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/assessments')
        assert response.status_code == 200

    def test_assessments_list_displays_all_assessments(self, client, admin_user, auth, completed_assessment):
        """The assessments list shows the completed assessment's status."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/assessments')
        assert response.status_code == 200
        assert b'completed' in response.data

    def test_assessments_list_shows_project_names(self, client, admin_user, auth, test_project,
                                                   completed_assessment):
        """The assessments list shows the owning project's name."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/assessments')
        assert response.status_code == 200
        assert test_project.name.encode() in response.data


class TestDashboardAnalytics:
    """Test analytics dashboard."""

    def test_analytics_page_loads(self, client, admin_user, auth):
        """Test that analytics page loads successfully."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/analytics')
        assert response.status_code == 200

    def test_analytics_shows_sdg_content(self, client, admin_user, auth):
        """Test that analytics page shows SDG-related content."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/analytics')
        assert response.status_code == 200
        assert b'SDG' in response.data or b'Goal' in response.data

    def test_analytics_shows_sdg_scores(self, client, admin_user, auth, completed_assessment):
        """With scored SDGs present, the analytics table renders goal names."""
        from app import cache
        cache.clear()  # analytics is @cache.cached; clear stale empty result
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/analytics')
        assert response.status_code == 200
        # completed_assessment scores the first 5 goals (incl. "No Poverty").
        assert b'No Poverty' in response.data
        assert b'No SDG score data yet' not in response.data

    def test_analytics_shows_charts_data(self, client, admin_user, auth, completed_assessment):
        """The analytics score table is populated (not the empty-state row)."""
        from app import cache
        cache.clear()
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/analytics')
        assert response.status_code == 200
        assert b'No SDG score data yet' not in response.data


class TestDashboardSDGManagement:
    """Test SDG management dashboard."""

    def test_sdg_management_page_loads(self, client, admin_user, auth):
        """Test that SDG management page loads."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/sdg-management')
        assert response.status_code == 200

    def test_sdg_management_shows_goals(self, client, admin_user, auth, session):
        """Test that SDG management page contains SDG content."""
        auth.login(email=admin_user.email, password='adminpass')
        goals = session.query(SdgGoal).all()
        assert len(goals) > 0, "No SDG goals in database"
        response = client.get('/dashboard/sdg-management')
        assert response.status_code == 200
        assert b'SDG' in response.data or b'Goal' in response.data


class TestDashboardQuestionManagement:
    """Test question management dashboard."""

    def test_question_management_page_loads(self, client, admin_user, auth):
        """Test that question management page loads."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/question-management')
        assert response.status_code == 200

    def test_question_management_shows_content(self, client, admin_user, auth):
        """Test that question management page shows question-related content."""
        auth.login(email=admin_user.email, password='adminpass')
        response = client.get('/dashboard/question-management')
        assert response.status_code == 200
        assert b'Question' in response.data or b'question' in response.data
