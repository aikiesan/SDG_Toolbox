"""
Flask CLI commands for database management.
"""

import click
from flask.cli import with_appcontext
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.sdg import SdgGoal, SdgQuestion
from app.utils.db_utils import SDG_GOAL_DATA


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
        existing = SdgGoal.query.count()
        if existing > 0:
            click.echo(f'SDG data already exists ({existing} goals found).')
            return

        for sdg_data in SDG_GOAL_DATA:
            new_sdg = SdgGoal(**sdg_data)
            db.session.add(new_sdg)

        db.session.commit()
        click.echo(f'Successfully initialized {len(SDG_GOAL_DATA)} SDG goals.')

    except Exception as e:
        db.session.rollback()
        click.echo(f'Error initializing SDG data: {str(e)}')
        raise click.ClickException(str(e))


@click.command('update-schema')
@with_appcontext
def update_schema_command():
    """Update the database schema."""
    try:
        db.session.execute(text("SELECT 1"))
        db.session.commit()
        click.echo('Schema updated successfully.')
    except (SQLAlchemyError, Exception) as e:
        db.session.rollback()
        click.echo(f'Error updating schema: {str(e)}')
        raise click.ClickException(str(e))


def register_cli_commands(app):
    """Register CLI commands with the Flask app."""
    from app.routes.goals_cli import populate_goals_command
    from app.routes.assessments_cli import register_cli_commands as register_assessment_cli

    app.cli.add_command(init_db_command)
    app.cli.add_command(init_sdg_data_command)
    app.cli.add_command(populate_goals_command)
    app.cli.add_command(update_schema_command)

    # Register populate-questions and clear-and-populate-questions from assessments_cli
    register_assessment_cli(app)
