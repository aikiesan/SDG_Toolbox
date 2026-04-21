import os
import sys
from decimal import Decimal # Use Decimal for potentially more precise strength values

# --- Path Setup ---
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- End Path Setup ---

# --- Flask App and DB Setup ---
# Import necessary components AFTER setting the path
try:
    from app import create_app, db
    from app.models.sdg import SdgGoal
    from app.models.sdg_relationship import SdgRelationship
except ImportError as e:
    print(f"Error importing Flask app or models: {e}")
    print("Ensure the script is run from the project root directory containing the 'app' package.")
    print(f"Project root used: {project_root}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)
# --- End Flask App and DB Setup ---

# --- Define Your Relationship Data ---
# List of dictionaries: {'source': source_id, 'target': target_id, 'strength': value}
# Strength Scale Suggestion:
#   0.8 - 1.0: Very Strong Positive Synergy
#   0.5 - 0.7: Moderate Positive Synergy
#   0.1 - 0.4: Weak Positive Synergy
#   0.0: Neutral / No direct synergy considered for bonus
#   (Negative values could be used for trade-offs if your logic handles them)

# !!! --- CUSTOMIZE THIS LIST BASED ON SDG INTERACTIONS --- !!!
RELATIONSHIP_DATA = [
    {'source': 1, 'target': 2, 'strength': 0.8},
    {'source': 1, 'target': 3, 'strength': 0.7},
    {'source': 1, 'target': 4, 'strength': 0.7},
    {'source': 1, 'target': 8, 'strength': 0.9},
    {'source': 1, 'target': 10, 'strength': 0.9},
    {'source': 3, 'target': 1, 'strength': 0.7},
    {'source': 3, 'target': 2, 'strength': 0.8},
    {'source': 3, 'target': 4, 'strength': 0.6},
    {'source': 3, 'target': 6, 'strength': 0.8},
    {'source': 4, 'target': 1, 'strength': 0.7},
    {'source': 4, 'target': 3, 'strength': 0.6},
    {'source': 4, 'target': 5, 'strength': 0.8},
    {'source': 4, 'target': 8, 'strength': 0.8},
    {'source': 4, 'target': 10, 'strength': 0.7},
    {'source': 5, 'target': 4, 'strength': 0.8},
    {'source': 5, 'target': 8, 'strength': 0.7},
    {'source': 5, 'target': 10, 'strength': 0.8},
    {'source': 6, 'target': 3, 'strength': 0.8},
    {'source': 6, 'target': 14, 'strength': 0.6},
    {'source': 6, 'target': 15, 'strength': 0.6},
    {'source': 7, 'target': 8, 'strength': 0.7},
    {'source': 7, 'target': 9, 'strength': 0.8},
    {'source': 7, 'target': 11, 'strength': 0.6},
    {'source': 7, 'target': 13, 'strength': 0.9},
    {'source': 8, 'target': 1, 'strength': 0.9},
    {'source': 8, 'target': 9, 'strength': 0.7},
    {'source': 9, 'target': 7, 'strength': 0.6},
    {'source': 9, 'target': 8, 'strength': 0.7},
    {'source': 9, 'target': 11, 'strength': 0.8},
    {'source': 11, 'target': 1, 'strength': 0.6},
    {'source': 11, 'target': 9, 'strength': 0.8},
    {'source': 11, 'target': 12, 'strength': 0.7},
    {'source': 12, 'target': 6, 'strength': 0.5},
    {'source': 12, 'target': 7, 'strength': 0.5},
    {'source': 12, 'target': 13, 'strength': 0.7},
    {'source': 12, 'target': 14, 'strength': 0.6},
    {'source': 12, 'target': 15, 'strength': 0.6},
    {'source': 13, 'target': 7, 'strength': 0.7},
    {'source': 13, 'target': 14, 'strength': 0.8},
    {'source': 13, 'target': 15, 'strength': 0.8},
    {'source': 16, 'target': 1, 'strength': 0.5},
    {'source': 16, 'target': 8, 'strength': 0.6},
    {'source': 16, 'target': 10, 'strength': 0.7},
    *[{'source': 17, 'target': i, 'strength': 0.2} for i in range(1, 17)],
]
# --- End Relationship Data ---

def populate_relationships():
    """Populates the sdg_relationships table."""
    app = create_app() # Create the Flask app instance
    with app.app_context(): # Push an application context
        print("Checking existing relationships...")
        try:
            existing_count = db.session.query(SdgRelationship).count()
        except Exception as e:
             print(f"Error querying existing relationships: {e}")
             print("Ensure your database connection is configured correctly in config.py and the database exists.")
             return # Exit if we can't even query

        if existing_count > 0:
            print(f"Database already contains {existing_count} relationships.")
            # Ask user if they want to clear and repopulate
            confirm = input("Do you want to clear existing relationships and repopulate? (yes/no): ").lower()
            if confirm == 'yes':
                try:
                    print("Clearing existing relationships...")
                    db.session.query(SdgRelationship).delete()
                    db.session.commit()
                    print("Existing relationships cleared.")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error clearing relationships: {e}")
                    return
            else:
                print("Skipping population.")
                return

        print("Populating SDG relationships...")
        added_count = 0
        skipped_count = 0
        try:
            # Fetch valid SDG IDs once to check if source/target exist
            valid_sdg_ids = {goal.id for goal in db.session.query(SdgGoal.id).all()}
            if not valid_sdg_ids:
                print("Error: No SDG Goals found in the 'sdg_goals' table. Cannot create relationships.")
                return

            for rel_data in RELATIONSHIP_DATA:
                source_id = rel_data.get('source')
                target_id = rel_data.get('target')
                # Use .get with a default for strength
                strength_val = rel_data.get('strength')

                # Basic validation
                if source_id is None or target_id is None or strength_val is None:
                    print(f"  Warning: Skipping incomplete relationship data: {rel_data}")
                    skipped_count += 1
                    continue

                # Convert strength to float (Decimal might be overkill here)
                try:
                    strength = float(strength_val)
                except (ValueError, TypeError):
                     print(f"  Warning: Skipping relationship ({source_id} -> {target_id}) due to invalid strength value: {strength_val}")
                     skipped_count += 1
                     continue

                # Check if source and target IDs are valid SDGs
                if source_id in valid_sdg_ids and target_id in valid_sdg_ids:
                    # Check if this specific relationship already exists (handles re-runs after clearing)
                    exists = db.session.query(SdgRelationship).filter_by(
                        source_sdg_id=source_id,
                        target_sdg_id=target_id
                    ).first()

                    if not exists:
                        relationship = SdgRelationship(
                            source_sdg_id=source_id,
                            target_sdg_id=target_id,
                            strength=strength # Assign the float value to the 'strength' column
                        )
                        db.session.add(relationship)
                        added_count += 1
                    else:
                        skipped_count += 1
                else:
                    print(f"  Warning: Skipping invalid relationship ({source_id} -> {target_id}). Check if SDG IDs exist in sdg_goals table.")
                    skipped_count += 1

            db.session.commit()
            print(f"\nSuccessfully added {added_count} new SDG relationships.")
            if skipped_count > 0:
                print(f"Skipped {skipped_count} relationships (duplicates or invalid IDs).")

        except Exception as e:
            db.session.rollback()
            print(f"\nAn error occurred during population: {e}")
            print("Database transaction rolled back.")
            import traceback
            traceback.print_exc() # Print full traceback for debugging
        finally:
             # The context is popped automatically by the 'with' statement
             pass

# Make the script runnable
if __name__ == "__main__":
    print("Attempting to populate SDG relationships...")
    populate_relationships()
    print("Script finished.")
