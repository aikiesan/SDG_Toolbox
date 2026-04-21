# app/utils/db_utils.py
from flask import current_app
from app import db
from app.models.sdg import SdgGoal, SdgQuestion
from app.models import SdgScore, Project, Assessment, QuestionResponse
from datetime import datetime
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

SDG_GOAL_DATA = [
    {'number': 1,  'name': 'No Poverty',                          'color_code': '#E5243B', 'description': 'End poverty in all its forms everywhere'},
    {'number': 2,  'name': 'Zero Hunger',                         'color_code': '#DDA63A', 'description': 'End hunger, achieve food security and improved nutrition and promote sustainable agriculture'},
    {'number': 3,  'name': 'Good Health and Well-being',          'color_code': '#4C9F38', 'description': 'Ensure healthy lives and promote well-being for all at all ages'},
    {'number': 4,  'name': 'Quality Education',                   'color_code': '#C5192D', 'description': 'Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all'},
    {'number': 5,  'name': 'Gender Equality',                     'color_code': '#FF3A21', 'description': 'Achieve gender equality and empower all women and girls'},
    {'number': 6,  'name': 'Clean Water and Sanitation',          'color_code': '#26BDE2', 'description': 'Ensure availability and sustainable management of water and sanitation for all'},
    {'number': 7,  'name': 'Affordable and Clean Energy',         'color_code': '#FCC30B', 'description': 'Ensure access to affordable, reliable, sustainable and modern energy for all'},
    {'number': 8,  'name': 'Decent Work and Economic Growth',     'color_code': '#A21942', 'description': 'Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all'},
    {'number': 9,  'name': 'Industry, Innovation and Infrastructure', 'color_code': '#FD6925', 'description': 'Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation'},
    {'number': 10, 'name': 'Reduced Inequalities',                'color_code': '#DD1367', 'description': 'Reduce inequality within and among countries'},
    {'number': 11, 'name': 'Sustainable Cities and Communities',  'color_code': '#FD9D24', 'description': 'Make cities and human settlements inclusive, safe, resilient and sustainable'},
    {'number': 12, 'name': 'Responsible Consumption and Production', 'color_code': '#BF8B2E', 'description': 'Ensure sustainable consumption and production patterns'},
    {'number': 13, 'name': 'Climate Action',                      'color_code': '#3F7E44', 'description': 'Take urgent action to combat climate change and its impacts'},
    {'number': 14, 'name': 'Life Below Water',                    'color_code': '#0A97D9', 'description': 'Conserve and sustainably use the oceans, seas and marine resources for sustainable development'},
    {'number': 15, 'name': 'Life on Land',                        'color_code': '#56C02B', 'description': 'Protect, restore and promote sustainable use of terrestrial ecosystems'},
    {'number': 16, 'name': 'Peace, Justice and Strong Institutions', 'color_code': '#00689D', 'description': 'Promote peaceful and inclusive societies for sustainable development'},
    {'number': 17, 'name': 'Partnerships for the Goals',          'color_code': '#19486A', 'description': 'Strengthen the means of implementation and revitalize the global partnership for sustainable development'},
]

SDG_QUESTION_DATA = [
    {
        'id': 1,
        'text': 'How does your project address poverty reduction?',
        'type': 'radio',
        'sdg_id': 1,
        'max_score': 5.0
    },
    {
        'id': 2,
        'text': 'Does your project contribute to food security?',
        'type': 'checkbox',
        'sdg_id': 2,
        'max_score': 5.0
    },
    {
        'id': 3,
        'text': 'How does your project promote health and well-being?',
        'type': 'radio',
        'sdg_id': 3,
        'max_score': 5.0
    },
    {
        'id': 4,
        'text': 'Does your project support quality education?',
        'type': 'checkbox',
        'sdg_id': 4,
        'max_score': 5.0
    },
    {
        'id': 5,
        'text': 'How does your project promote gender equality?',
        'type': 'radio',
        'sdg_id': 5,
        'max_score': 5.0
    }
    # Add more questions as needed - this is a basic set for testing
]

def get_db():
    """Get the current SQLAlchemy session."""
    return db.session

def populate_goals():
    """Populates the sdg_goals table using SQLAlchemy session."""
    print("populate_goals: Starting...")
    added_count = 0
    try:
        for goal_data in SDG_GOAL_DATA:
            existing_goal = db.session.execute(db.select(SdgGoal).filter_by(number=goal_data['number'])).scalar_one_or_none()
            if not existing_goal:
                new_goal = SdgGoal(
                    number=goal_data['number'],
                    name=goal_data['name'],
                    color_code=goal_data['color_code'],
                    description=goal_data.get('description', '')
                )
                db.session.add(new_goal)
                added_count += 1
                print(f"  Adding SDG {goal_data['number']}...")

        if added_count > 0:
            print(f"populate_goals: Prepared {added_count} goals.")
        else:
            print("populate_goals: All goals already exist.")
        print("populate_goals: Succeeded.")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"ERROR populating sdg_goals: {e}")
        print("populate_goals: Failed.")
        return False

def populate_questions():
    """Populate the sdg_questions table with all required questions."""
    final_success = False
    try:
        # Check existing questions
        existing_ids = [q.id for q in db.session.query(SdgQuestion).all()]
        questions_to_add = []
        current_app.logger.info(f"Existing question IDs in DB: {existing_ids}")

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
            current_app.logger.info("No missing questions (1-31) found to add. Table already populated.")
            final_success = True
        else:
            current_app.logger.info(f"Found {len(questions_to_add)} missing questions to add.")
            db.session.add_all(questions_to_add)
            db.session.commit()
            final_success = True

    except Exception as e:
        current_app.logger.error(f"Error populating questions: {str(e)}")
        db.session.rollback()
        final_success = False

    if final_success:
        print("populate_questions: Succeeded.")
    else:
        print("populate_questions: Failed.")
    return final_success

def populate_sdg_relationships():
    """Populate the sdg_relationships table with relationships between SDGs."""
    try:
        # Check if relationships already exist
        existing_count = db.session.query(SdgRelationship).count()
        if existing_count > 0:
            current_app.logger.info(f"SDG relationships table already has {existing_count} entries")
            return True
        
        # Define relationships (source_sdg_id, target_sdg_id, relationship_strength)
        relationships = [
            # SDG 1 (No Poverty) relationships
            (1, 2, 0.8),  # Strong relationship with SDG 2 (Zero Hunger)
            (1, 3, 0.7),  # Strong relationship with SDG 3 (Good Health)
            (1, 4, 0.9),  # Very strong relationship with SDG 4 (Education)
            
            # SDG 2 (Zero Hunger) relationships
            (2, 1, 0.8),  # Strong relationship with SDG 1 (No Poverty)
            (2, 3, 0.9),  # Very strong relationship with SDG 3 (Good Health)
            (2, 15, 0.7),  # Strong relationship with SDG 15 (Life on Land)
        ]
        
        # Create and add relationship objects
        for source_id, target_id, strength in relationships:
            relationship = SdgRelationship(
                source_sdg_id=source_id,
                target_sdg_id=target_id,
                relationship_strength=strength
            )
            db.session.add(relationship)
            
        db.session.commit()
        current_app.logger.info(f"Added {len(relationships)} SDG relationships to the database")
        return True
    except Exception as e:
        current_app.logger.error(f"Error populating SDG relationships: {str(e)}")
        db.session.rollback()
        return False