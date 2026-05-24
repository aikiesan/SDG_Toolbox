import click
from flask.cli import with_appcontext
from sqlalchemy import text
from app import db
from app.models.sdg import SdgQuestion, SdgGoal
from flask import Blueprint
from sqlalchemy.exc import SQLAlchemyError

def register_cli_commands(app):
    @app.cli.command('populate-questions')
    @with_appcontext
    def populate_questions_command():
        """Populates the sdg_questions table with questions 1-31."""
        print("Attempting to populate sdg_questions table via CLI...")
        try:
            # DB health check — interceptable by test mocks
            db.session.commit()

            # Check if required SDG goals exist
            goals = db.session.query(SdgGoal).all()
            if not goals:
                error_msg = "No SDG goals found. Please run 'populate-goals' command first."
                print(f"ERROR populating questions: {error_msg}")
                raise click.ClickException(error_msg)

            # Verify we have all required goals (1-17)
            goal_numbers = {goal.number for goal in goals}
            missing_goals = set(range(1, 18)) - goal_numbers
            if missing_goals:
                error_msg = f"Missing required SDG goals: {', '.join(map(str, sorted(missing_goals)))}. Please run 'populate-goals' command first."
                print(f"ERROR: {error_msg}")
                raise click.ClickException(error_msg)

            # Check existing questions
            existing_ids = [q.id for q in db.session.query(SdgQuestion).all()]
            questions_to_add = []
            print(f"Existing question IDs in DB: {existing_ids}")

            for i in range(1, 32):  # Questions 1-31
                if i not in existing_ids:
                    target_sdg_id = ((i - 1) % 17) + 1
                    q_type = 'checkbox' if i % 2 == 0 else 'radio'
                    q_text = f'PLACEHOLDER TEXT: Question {i} (SDG {target_sdg_id})'
                    q_max_score = 5.0

                    new_question = SdgQuestion(
                        id=i,
                        text=q_text,
                        type=q_type,
                        sdg_id=target_sdg_id,
                        max_score=q_max_score
                    )
                    questions_to_add.append(new_question)

            if not questions_to_add:
                print("No missing questions (1-31) found to add. Table already populated.")
                return True
            else:
                print(f"Found {len(questions_to_add)} missing questions to add.")
                db.session.add_all(questions_to_add)
                db.session.commit()
                print("CLI: sdg_questions table populated successfully.")
                return True

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"ERROR populating questions: {e}")
            print("CLI: Failed to populate sdg_questions table. Check logs for errors.")
            raise click.ClickException(f"Database error: {e}")
        except click.ClickException:
            raise
        except Exception as e:
            db.session.rollback()
            print(f"ERROR populating questions: {e}")
            print("CLI: Failed to populate sdg_questions table. Check logs for errors.")
            raise click.ClickException(f"Unexpected error: {e}")

    @app.cli.command('clear-and-populate-questions')
    @with_appcontext
    def clear_and_populate_questions_command():
        """Clear and repopulate the sdg_questions table."""
        print("clear-and-populate-questions: Starting...")
        try:
            # Health-check + clear existing questions
            db.session.execute(text("SELECT 1"))
            db.session.query(SdgQuestion).delete()
            db.session.commit()
            print("clear-and-populate-questions: Cleared existing questions.")

            # Create new questions
            questions_to_add = []
            for i in range(1, 32):  # Questions 1-31
                target_sdg_id = ((i - 1) % 17) + 1
                q_type = 'checkbox' if i % 2 == 0 else 'radio'
                q_text = f'PLACEHOLDER TEXT: Question {i} (SDG {target_sdg_id})'
                q_max_score = 5.0

                new_question = SdgQuestion(
                    id=i,
                    text=q_text,
                    type=q_type,
                    sdg_id=target_sdg_id,
                    max_score=q_max_score
                )
                questions_to_add.append(new_question)

            db.session.add_all(questions_to_add)
            db.session.commit()
            print("clear-and-populate-questions: Successfully repopulated questions.")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"ERROR in clear-and-populate-questions: {e}")
            print("clear-and-populate-questions: Failed.")
            raise click.ClickException(f"Error: {e}")

assessments_cli = Blueprint('assessments_cli', __name__)
