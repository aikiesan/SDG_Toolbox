import os
import sys
from decimal import Decimal # Use Decimal for potentially more precise strength values

# --- Path Setup ---
# Add the project root directory to the Python path
# This allows us to import the 'app' module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- End Path Setup ---

from app import create_app, db
from app.models.sdg import SdgGoal # Needed to verify SDG IDs exist (optional but good)
from app.models.sdg_relationship import SdgRelationship

# --- Define Your Relationship Data ---
# (Source_ID, Target_ID, Strength)
# Strength: Use a scale meaningful to your bonus logic.
# Example: 1.0 (Strong Positive), 0.5 (Moderate Positive), 0 (Neutral), -0.5 (Conflict), etc.
# NOTE: This is just example data based on common knowledge, refine based on expert sources!
RELATIONSHIP_DATA = [
    # Positive Synergies (Examples)
    {'source': 1, 'target': 2, 'strength': 0.8},   # Poverty -> Hunger
    {'source': 1, 'target': 3, 'strength': 0.7},   # Poverty -> Health
    {'source': 1, 'target': 4, 'strength': 0.7},   # Poverty -> Education
    {'source': 1, 'target': 5, 'strength': 0.6},   # Poverty -> Gender Equality
    {'source': 1, 'target': 6, 'strength': 0.5},   # Poverty -> Water
    {'source': 1, 'target': 8, 'strength': 0.9},   # Poverty -> Decent Work
    {'source': 1, 'target': 10, 'strength': 0.9},  # Poverty -> Inequality
    {'source': 1, 'target': 16, 'strength': 0.5},  # Poverty -> Peace/Justice

    {'source': 2, 'target': 1, 'strength': 0.8},   # Hunger -> Poverty
    {'source': 2, 'target': 3, 'strength': 0.9},   # Hunger -> Health
    {'source': 2, 'target': 4, 'strength': 0.6},   # Hunger -> Education
    {'source': 2, 'target': 15, 'strength': 0.5},  # Hunger -> Life on Land

    {'source': 3, 'target': 1, 'strength': 0.7},   # Health -> Poverty
    {'source': 3, 'target': 2, 'strength': 0.9},   # Health -> Hunger
    {'source': 3, 'target': 4, 'strength': 0.7},   # Health -> Education
    {'source': 3, 'target': 5, 'strength': 0.6},   # Health -> Gender Equality
    {'source': 3, 'target': 6, 'strength': 0.8},   # Health -> Water
    {'source': 3, 'target': 8, 'strength': 0.6},   # Health -> Decent Work

    {'source': 4, 'target': 1, 'strength': 0.7},   # Education -> Poverty
    {'source': 4, 'target': 3, 'strength': 0.7},   # Education -> Health
    {'source': 4, 'target': 5, 'strength': 0.8},   # Education -> Gender Equality
    {'source': 4, 'target': 8, 'strength': 0.8},   # Education -> Decent Work
    {'source': 4, 'target': 10, 'strength': 0.7},  # Education -> Inequality
    {'source': 4, 'target': 16, 'strength': 0.6},  # Education -> Peace/Justice

    {'source': 5, 'target': 1, 'strength': 0.6},   # Gender Eq -> Poverty
    {'source': 5, 'target': 3, 'strength': 0.6},   # Gender Eq -> Health
    {'source': 5, 'target': 4, 'strength': 0.8},   # Gender Eq -> Education
    {'source': 5, 'target': 8, 'strength': 0.7},   # Gender Eq -> Decent Work
    {'source': 5, 'target': 10, 'strength': 0.8},  # Gender Eq -> Inequality

    {'source': 6, 'target': 3, 'strength': 0.8},   # Water -> Health
    {'source': 6, 'target': 11, 'strength': 0.5},  # Water -> Cities
    {'source': 6, 'target': 14, 'strength': 0.6},  # Water -> Life Below Water
    {'source': 6, 'target': 15, 'strength': 0.6},  # Water -> Life on Land

    {'source': 7, 'target': 8, 'strength': 0.7},   # Energy -> Decent Work
    {'source': 7, 'target': 9, 'strength': 0.8},   # Energy -> Industry/Infra
    {'source': 7, 'target': 11, 'strength': 0.6},  # Energy -> Cities
    {'source': 7, 'target': 12, 'strength': 0.5},  # Energy -> Consumption
    {'source': 7, 'target': 13, 'strength': 0.8},  # Energy -> Climate Action (Clean energy helps)

    {'source': 8, 'target': 1, 'strength': 0.9},   # Decent Work -> Poverty
    {'source': 8, 'target': 9, 'strength': 0.7},   # Decent Work -> Industry/Infra
    {'source': 8, 'target': 10, 'strength': 0.7},  # Decent Work -> Inequality

    {'source': 9, 'target': 7, 'strength': 0.6},   # Industry/Infra -> Energy
    {'source': 9, 'target': 8, 'strength': 0.7},   # Industry/Infra -> Decent Work
    {'source': 9, 'target': 11, 'strength': 0.8},  # Industry/Infra -> Cities

    {'source': 11, 'target': 1, 'strength': 0.6},  # Cities -> Poverty
    {'source': 11, 'target': 6, 'strength': 0.5},  # Cities -> Water
    {'source': 11, 'target': 7, 'strength': 0.6},  # Cities -> Energy
    {'source': 11, 'target': 9, 'strength': 0.8},  # Cities -> Industry/Infra
    {'source': 11, 'target': 12, 'strength': 0.7}, # Cities -> Consumption

    {'source': 12, 'target': 6, 'strength': 0.5},  # Consumption -> Water
    {'source': 12, 'target': 7, 'strength': 0.5},  # Consumption -> Energy
    {'source': 12, 'target': 13, 'strength': 0.7}, # Consumption -> Climate
    {'source': 12, 'target': 14, 'strength': 0.6}, # Consumption -> Life Below Water
    {'source': 12, 'target': 15, 'strength': 0.6}, # Consumption -> Life on Land

    {'source': 13, 'target': 7, 'strength': 0.7},  # Climate -> Energy (Need for transition)
    {'source': 13, 'target': 11, 'strength': 0.5}, # Climate -> Cities (Resilience)
    {'source': 13, 'target': 14, 'strength': 0.8}, # Climate -> Life Below Water
    {'source': 13, 'target': 15, 'strength': 0.8}, # Climate -> Life on Land

    {'source': 16, 'target': 1, 'strength': 0.5},  # Peace/Justice -> Poverty
    {'source': 16, 'target': 8, 'strength': 0.6},  # Peace/Justice -> Decent Work
    {'source': 16, 'target': 10, 'strength': 0.7}, # Peace/Justice -> Inequality

    {'source': 17, 'target': -1, 'strength': 0.2} # Partnerships helps all others generally (use -1 or handle in logic)
    # Add potential negative interactions / trade-offs if your bonus logic uses them
    # {'source': 7, 'target': 13, 'strength': -0.6}, # Fossil fuel energy conflicts with climate action
    # {'source': 8, 'target': 15, 'strength': -0.5}, # Unsustainable growth conflicts with life on land
]

def populate_relationships():
    """Populates the sdg_relationships table."""
    app = create_app() # Create the Flask app instance
    with app.app_context(): # Push an application context
        print("Checking existing relationships...")
        existing_count = db.session.query(SdgRelationship).count()

        if existing_count > 0:
            print(f"Database already contains {existing_count} relationships. Skipping population.")
            # Option: Add logic here to clear existing relationships if needed
            # db.session.query(SdgRelationship).delete()
            # db.session.commit()
            # print("Cleared existing relationships.")
            return

        print("Populating SDG relationships...")
        added_count = 0
        skipped_count = 0
        try:
            # Optional: Fetch valid SDG IDs once to check if source/target exist
            valid_sdg_ids = {goal.id for goal in db.session.query(SdgGoal.id).all()}

            for rel_data in RELATIONSHIP_DATA:
                source_id = rel_data['source']
                target_id = rel_data['target']
                strength = Decimal(str(rel_data['strength'])) # Use Decimal for precision

                # Handle the general partnership case (SDG 17)
                if source_id == 17 and target_id == -1:
                    # Create relationships from 17 to all other SDGs (1-16)
                    for actual_target_id in range(1, 17):
                         # Check if relationship already exists (optional, good practice)
                         exists = db.session.query(SdgRelationship).filter_by(source_sdg_id=source_id, target_sdg_id=actual_target_id).first()
                         if not exists:
                             relationship = SdgRelationship(
                                 source_sdg_id=source_id,
                                 target_sdg_id=actual_target_id,
                                 relationship_strength=strength
                             )
                             db.session.add(relationship)
                             added_count += 1
                         else:
                            skipped_count +=1
                elif source_id in valid_sdg_ids and target_id in valid_sdg_ids:
                     # Check if relationship already exists
                     exists = db.session.query(SdgRelationship).filter_by(source_sdg_id=source_id, target_sdg_id=target_id).first()
                     if not exists:
                        relationship = SdgRelationship(
                            source_sdg_id=source_id,
                            target_sdg_id=target_id,
                            relationship_strength=strength
                        )
                        db.session.add(relationship)
                        added_count += 1
                     else:
                        skipped_count += 1
                else:
                    print(f"  Warning: Skipping invalid relationship ({source_id} -> {target_id}). Check SDG IDs.")
                    skipped_count += 1

            db.session.commit()
            print(f"Successfully added {added_count} new SDG relationships.")
            if skipped_count > 0:
                print(f"Skipped {skipped_count} relationships (duplicates or invalid IDs).")

        except Exception as e:
            db.session.rollback()
            print(f"\nAn error occurred: {e}")
            print("Database transaction rolled back.")
        finally:
             # The context is popped automatically by the 'with' statement
             pass

# Make the script runnable
if __name__ == "__main__":
    print("Attempting to populate SDG relationships...")
    populate_relationships()
    print("Script finished.")