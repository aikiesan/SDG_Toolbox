import pytest
from app import create_app, db
from app.models.sdg import SdgGoal, SdgQuestion
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from click.testing import CliRunner
import os
import random

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def runner(app):
    """Provides a CLI runner for testing commands."""
    return app.test_cli_runner()

@pytest.fixture
def mock_db_session():
    """Provides a mock DB session for testing."""
    mock_session = MagicMock()
    return mock_session

def test_init_db_command(runner, app):
    """Test the init-db command."""
    with app.app_context():
        result = runner.invoke(cli=app.cli, args=['init-db'])
        assert result.exit_code == 0
        assert 'Database initialized' in result.output

def test_init_sdg_data_command(runner, app):
    """Test the init-sdg-data command."""
    # Case 1: No existing SDG data
    with app.app_context():
        # Clear existing SDGs for test
        SdgGoal.query.delete()
        db.session.commit()
        
        result = runner.invoke(cli=app.cli, args=['init-sdg-data'])
        assert 'Successfully initialized' in result.output
        assert SdgGoal.query.count() > 0
    
    # Case 2: Data already exists
    with app.app_context():
        result = runner.invoke(cli=app.cli, args=['init-sdg-data'])
        assert 'SDG data already exists' in result.output

def test_init_sdg_data_error(runner, app):
    """Test error handling in init-sdg-data command."""
    with app.app_context():
        with patch('app.models.sdg.SdgGoal.query') as mock_query:
            mock_query.count.side_effect = Exception("Database error")
            result = runner.invoke(cli=app.cli, args=['init-sdg-data'])
            assert 'Error initializing SDG data' in result.output
            assert result.exit_code != 0

def test_populate_goals_command(runner, app):
    """Test the populate-goals command."""
    with app.app_context():
        # Clear existing SDGs for test
        SdgGoal.query.delete()
        db.session.commit()
        
        # Test populating goals
        result = runner.invoke(cli=app.cli, args=['populate-goals'])
        assert result.exit_code == 0
        assert "SDG goals table populated successfully" in result.output
        
        # Verify goals were added
        goals = SdgGoal.query.all()
        assert len(goals) == 17  # Should have all 17 SDGs
        
        # Check specific goals
        goal1 = SdgGoal.query.filter_by(number=1).first()
        assert goal1 is not None
        assert goal1.name == 'No Poverty'
        assert goal1.color_code == '#E5243B'
        
        # Test running command again with existing data
        result = runner.invoke(cli=app.cli, args=['populate-goals'])
        assert result.exit_code == 0
        assert "All goals already exist" in result.output or "goals already exist" in result.output

def test_populate_goals_error(runner, app):
    """Test error handling in populate-goals command."""
    with app.app_context():
        with patch('app.routes.goals_cli.SdgGoal') as mock_goal:
            # Simulate SQLAlchemy error
            mock_goal.side_effect = Exception("Database error")
            result = runner.invoke(cli=app.cli, args=['populate-goals'])
            assert result.exit_code != 0
            assert "ERROR" in result.output

def test_populate_questions_command(runner, app):
    """Test the populate-questions command."""
    with app.app_context():
        # First make sure we have goals
        runner.invoke(cli=app.cli, args=['populate-goals'])
        
        # Clear existing questions for test
        SdgQuestion.query.delete()
        db.session.commit()
        
        # Test populating questions
        result = runner.invoke(cli=app.cli, args=['populate-questions'])
        assert result.exit_code == 0
        assert "CLI: sdg_questions table populated successfully" in result.output
        
        # Verify questions were added
        questions = SdgQuestion.query.all()
        assert len(questions) == 31  # Should have 31 questions
        
        # Test running command again with existing data
        result = runner.invoke(cli=app.cli, args=['populate-questions'])
        assert result.exit_code == 0
        assert "No missing questions" in result.output or "already populated" in result.output

def test_populate_questions_no_goals(runner, app):
    """Test populate-questions with no SDG goals."""
    with app.app_context():
        # Clear goals and questions
        SdgGoal.query.delete()
        SdgQuestion.query.delete()
        db.session.commit()
        
        # Should fail because goals don't exist
        result = runner.invoke(cli=app.cli, args=['populate-questions'])
        assert result.exit_code != 0
        assert "No SDG goals found" in result.output or "Error" in result.output

def test_populate_questions_error(runner, app):
    """Test error handling in populate-questions command."""
    with app.app_context():
        # First make sure we have goals
        runner.invoke(cli=app.cli, args=['populate-goals'])
        
        # Simulate database error
        with patch('app.routes.assessments_cli.db.session') as mock_session:
            mock_session.query.side_effect = Exception("Database error")
            result = runner.invoke(cli=app.cli, args=['populate-questions'])
            assert result.exit_code != 0
            assert "ERROR" in result.output

def test_clear_and_populate_questions_command(runner, app):
    """Test the clear-and-populate-questions command."""
    with app.app_context():
        # First make sure we have goals
        runner.invoke(cli=app.cli, args=['populate-goals'])
        
        # Add a test question with known content
        test_question = SdgQuestion(
            id=999,
            text="Test question that should be cleared",
            type="radio",
            sdg_id=1,
            max_score=5.0
        )
        db.session.add(test_question)
        db.session.commit()
        
        # Then test clearing and repopulating questions
        result = runner.invoke(cli=app.cli, args=['clear-and-populate-questions'])
        assert result.exit_code == 0
        assert "clear-and-populate-questions: Successfully repopulated questions" in result.output
        
        # Verify the test question is gone and we have 31 fresh questions
        assert SdgQuestion.query.filter_by(id=999).first() is None
        assert SdgQuestion.query.count() == 31

def test_clear_and_populate_questions_error(runner, app):
    """Test error handling in clear-and-populate-questions command."""
    with app.app_context():
        with patch('app.routes.assessments_cli.db.session') as mock_session:
            mock_session.query.side_effect = Exception("Database error")
            result = runner.invoke(cli=app.cli, args=['clear-and-populate-questions'])
            assert "ERROR" in result.output
            assert result.exit_code != 0

def test_update_schema_command(runner, app):
    """Test the update-schema command."""
    with patch('app.models.project.Project') as mock_project:
        result = runner.invoke(cli=app.cli, args=['update-schema'])
        assert result.exit_code == 0
        assert "Schema updated successfully" in result.output or "Schema update completed" in result.output

def test_cli_command_error_handling(runner, app):
    """Test error handling in CLI commands."""
    # Test populate-goals command with database error
    with patch('app.db.session.commit', side_effect=SQLAlchemyError("Simulated DB error")):
        result = runner.invoke(cli=app.cli, args=['populate-goals'])
        assert result.exit_code != 0
        assert "ERROR populating sdg_goals" in result.output
        assert "Simulated DB error" in result.output

    # Test populate-questions command with database error
    with patch('app.db.session.commit', side_effect=SQLAlchemyError("Simulated DB error")):
        result = runner.invoke(cli=app.cli, args=['populate-questions'])
        assert result.exit_code != 0
        assert "ERROR populating questions" in result.output
        assert "Simulated DB error" in result.output

    # Test clear-and-populate-questions command with database error
    with patch('app.db.session.execute', side_effect=SQLAlchemyError("Simulated DB error")):
        result = runner.invoke(cli=app.cli, args=['clear-and-populate-questions'])
        assert result.exit_code != 0
        assert "ERROR in clear-and-populate-questions" in result.output
        assert "Simulated DB error" in result.output

    # Test update-schema command with database error
    with patch('app.db.session.execute', side_effect=SQLAlchemyError("Simulated DB error")):
        result = runner.invoke(cli=app.cli, args=['update-schema'])
        assert result.exit_code != 0
        assert "Error updating schema" in result.output
        assert "Simulated DB error" in result.output

def test_invalid_input_handling(runner, app):
    """Test handling of invalid input data in CLI commands."""
    # Test populate-goals with invalid goal data
    with patch('app.utils.db_utils.SDG_GOAL_DATA', [{
        'number': 'invalid',  # Should be integer
        'name': None,  # Should be string
        'color_code': 'invalid-color',  # Invalid color code
        'description': 123  # Should be string
    }]):
        result = runner.invoke(cli=app.cli, args=['populate-goals'])
        assert result.exit_code != 0
        assert "ERROR" in result.output

    # Test populate-questions with missing SDG goals
    with patch('app.models.sdg.SdgGoal.query.all', return_value=[]):
        result = runner.invoke(cli=app.cli, args=['populate-questions'])
        assert result.exit_code != 0
        assert "No SDG goals found" in result.output

    # Test clear-and-populate-questions with invalid SQL
    with patch('app.db.session.execute', side_effect=DataError("Invalid SQL", "params", "orig")):
        result = runner.invoke(cli=app.cli, args=['clear-and-populate-questions'])
        assert result.exit_code != 0
        assert "ERROR" in result.output

    # Test update-schema with invalid column type
    with patch('app.db.session.execute', side_effect=DataError("Invalid column type", "params", "orig")):
        result = runner.invoke(cli=app.cli, args=['update-schema'])
        assert result.exit_code != 0
        assert "Error updating schema" in result.output

def test_duplicate_data_handling(runner, app):
    """Test handling of duplicate data in CLI commands."""
    # Test populate-goals with duplicate goal numbers
    with patch('app.utils.db_utils.SDG_GOAL_DATA', [
        {'number': 1, 'name': 'Goal 1', 'color_code': '#000000', 'description': 'Desc 1'},
        {'number': 1, 'name': 'Goal 1 Duplicate', 'color_code': '#000000', 'description': 'Desc 1'}
    ]):
        result = runner.invoke(cli=app.cli, args=['populate-goals'])
        assert result.exit_code != 0
        assert "ERROR" in result.output

    # Test populate-questions with duplicate question IDs
    with patch('app.models.sdg.SdgQuestion.query.all', return_value=[
        SdgQuestion(id=1, text='Question 1', type='radio', sdg_id=1, max_score=5.0)
    ]):
        result = runner.invoke(cli=app.cli, args=['populate-questions'])
        assert result.exit_code != 0
        assert "ERROR" in result.output

def test_missing_dependencies(runner, app):
    """Test handling of missing dependencies in CLI commands."""
    # Test populate-questions without goals
    result = runner.invoke(cli=app.cli, args=['populate-questions'])
    assert result.exit_code != 0
    assert "No SDG goals found" in result.output

    # Test clear-and-populate-questions without database connection
    with patch('app.db.session.execute', side_effect=SQLAlchemyError("No database connection")):
        result = runner.invoke(cli=app.cli, args=['clear-and-populate-questions'])
        assert result.exit_code != 0
        assert "ERROR" in result.output

    # Test update-schema with missing table
    with patch('app.db.session.execute', side_effect=SQLAlchemyError("Table does not exist")):
        result = runner.invoke(cli=app.cli, args=['update-schema'])
        assert result.exit_code != 0
        assert "Error updating schema" in result.output 