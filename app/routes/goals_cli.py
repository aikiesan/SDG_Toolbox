import click
from flask.cli import with_appcontext
from app import db
from app.models.sdg import SdgGoal
from app.utils import db_utils
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


def validate_goal_data(goal_data):
    """Validate a single goal's data."""
    errors = []

    if not isinstance(goal_data.get('number'), int):
        errors.append(f"Goal number must be an integer, got {type(goal_data.get('number'))}")

    if not isinstance(goal_data.get('name'), str) or not goal_data.get('name'):
        errors.append("Goal name must be a non-empty string")

    if not isinstance(goal_data.get('color_code'), str) or not goal_data.get('color_code'):
        errors.append("Color code must be a non-empty string")
    elif not goal_data['color_code'].startswith('#'):
        errors.append("Color code must start with #")

    if 'description' in goal_data and not isinstance(goal_data['description'], str):
        errors.append("Description must be a string")

    return errors


def check_for_duplicates(goal_data_list):
    """Check for duplicate goal numbers in the input data."""
    seen_numbers = set()
    duplicates = set()

    for goal_data in goal_data_list:
        number = goal_data.get('number')
        if number in seen_numbers:
            duplicates.add(number)
        seen_numbers.add(number)

    return duplicates


@click.command('populate-goals')
@with_appcontext
def populate_goals_command():
    """Populates the sdg_goals table with goals 1-17."""
    print("Populating sdg_goals table...")
    added_count = 0

    # Validate all goal data first (uses db_utils.SDG_GOAL_DATA at call time for mockability)
    all_errors = []
    for goal_data in db_utils.SDG_GOAL_DATA:
        errors = validate_goal_data(goal_data)
        if errors:
            all_errors.extend([f"Goal {goal_data.get('number', 'unknown')}: {e}" for e in errors])

    if all_errors:
        error_msg = "Invalid goal data:\n" + "\n".join(all_errors)
        print(f"ERROR: {error_msg}")
        raise click.ClickException(error_msg)

    duplicates = check_for_duplicates(db_utils.SDG_GOAL_DATA)
    if duplicates:
        error_msg = f"Duplicate goal numbers found: {', '.join(map(str, sorted(duplicates)))}"
        print(f"ERROR: {error_msg}")
        raise click.ClickException(error_msg)

    try:
        for goal_data in db_utils.SDG_GOAL_DATA:
            # Create the instance first so that mocking SdgGoal triggers early
            new_goal = SdgGoal(
                number=goal_data['number'],
                name=goal_data['name'],
                color_code=goal_data['color_code'],
                description=goal_data.get('description', '')
            )
            existing_goal = SdgGoal.query.filter_by(number=goal_data['number']).first()
            if not existing_goal:
                db.session.add(new_goal)
                added_count += 1
                print(f"  Adding SDG {goal_data['number']}...")

        if added_count > 0:
            db.session.commit()
            print(f"Successfully added {added_count} SDG goals.")
            print("SDG goals table populated successfully")
        else:
            print("All SDG goals already exist.")
            print("SDG goals table populated successfully")
    except IntegrityError as e:
        db.session.rollback()
        error_msg = "Database integrity error: Duplicate goal numbers detected"
        print(f"ERROR populating sdg_goals: {error_msg}")
        raise click.ClickException(error_msg)
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"ERROR populating sdg_goals: {e}")
        raise click.ClickException(f"Database error: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"ERROR populating sdg_goals: {e}")
        raise click.ClickException(f"Unexpected error: {e}")
