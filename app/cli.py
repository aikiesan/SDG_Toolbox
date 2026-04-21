"""
Flask CLI commands for database management.
"""

import click
from flask.cli import with_appcontext
from app import db
from app.utils.db import get_db
from app.models.sdg import SdgGoal, SdgQuestion
from app.utils.db_utils import SDG_GOAL_DATA, SDG_QUESTION_DATA

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    try:
        db.create_all()
        click.echo('Database initialized.')
    except Exception as e:
        click.echo(f'Error initializing database: {str(e)}')
        raise

@click.command('init-sdg-data')
@with_appcontext
def init_sdg_data_command():
    """Initialize SDG data in the database."""
    try:
        # Check if SDG goals already exist
        existing = SdgGoal.query.count()
        if existing > 0:
            click.echo(f'SDG data already exists ({existing} goals found).')
            return
        
        # Insert SDGs from data
        for sdg_data in SDG_GOAL_DATA:
            new_sdg = SdgGoal(**sdg_data)
            db.session.add(new_sdg)
        
        db.session.commit()
        click.echo(f'Successfully initialized {len(SDG_GOAL_DATA)} SDG goals.')
    
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error initializing SDG data: {str(e)}')

@click.command('populate-goals')
@with_appcontext
def populate_goals_command():
    """Populate SDG goals table with data."""
    try:
        # Check if goals already exist
        existing = SdgGoal.query.count()
        if existing > 0:
            click.echo("All goals already exist")
            return

        # Add goals from data
        for goal_data in SDG_GOAL_DATA:
            goal = SdgGoal(**goal_data)
            db.session.add(goal)
        
        db.session.commit()
        click.echo("SDG goals table populated successfully")
    except Exception as e:
        db.session.rollback()
        click.echo(f"ERROR populating sdg_goals: {str(e)}")
        raise

@click.command('populate-questions')
@with_appcontext
def populate_questions_command():
    """Populate SDG questions table with data."""
    try:
        # Check if we have goals
        if SdgGoal.query.count() == 0:
            click.echo("No SDG goals found. Please run populate-goals first.")
            return

        # Add questions from data
        for question_data in SDG_QUESTION_DATA:
            question = SdgQuestion(**question_data)
            db.session.add(question)
        
        db.session.commit()
        click.echo("CLI: sdg_questions table populated successfully")
    except Exception as e:
        db.session.rollback()
        click.echo(f"ERROR populating sdg_questions: {str(e)}")
        raise

@click.command('clear-and-populate-questions')
@with_appcontext
def clear_and_populate_questions_command():
    """Clear and repopulate SDG questions table."""
    try:
        # Clear existing questions
        SdgQuestion.query.delete()
        db.session.commit()
        
        # Repopulate questions
        for question_data in SDG_QUESTION_DATA:
            question = SdgQuestion(**question_data)
            db.session.add(question)
        
        db.session.commit()
        click.echo("clear-and-populate-questions: Successfully repopulated questions")
    except Exception as e:
        db.session.rollback()
        click.echo(f"ERROR: {str(e)}")
        raise

def register_cli_commands(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_sdg_data_command)
    app.cli.add_command(populate_goals_command)
    app.cli.add_command(populate_questions_command)
    app.cli.add_command(clear_and_populate_questions_command)
