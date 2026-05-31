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


@click.command('create-admin')
@click.argument('email')
@click.argument('password')
@click.option('--name', default='Admin', help='Display name for the admin user.')
@with_appcontext
def create_admin_command(email, password, name):
    """Create (or promote) a confirmed admin user.

    Usage: flask create-admin <email> <password> [--name "Full Name"]
    Idempotent: if the user already exists it is promoted to admin, marked
    confirmed, and its password is reset to the supplied value.
    """
    from app.models.user import User
    from werkzeug.security import generate_password_hash
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_admin = True
            user.email_confirmed = True
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            click.echo(f"Updated existing user '{email}' -> admin (confirmed, password reset).")
            return
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=True,
            email_confirmed=True,
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f"Created admin user '{email}'.")
    except Exception as e:
        db.session.rollback()
        raise click.ClickException(str(e))


def register_cli_commands(app):
    """Register CLI commands with the Flask app."""
    from app.routes.goals_cli import populate_goals_command
    from app.routes.assessments_cli import register_cli_commands as register_assessment_cli

    app.cli.add_command(init_db_command)
    app.cli.add_command(init_sdg_data_command)
    app.cli.add_command(populate_goals_command)
    app.cli.add_command(update_schema_command)
    app.cli.add_command(create_admin_command)

    # Register populate-questions and clear-and-populate-questions from assessments_cli
    register_assessment_cli(app)
