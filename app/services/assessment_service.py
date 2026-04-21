"""
Assessment service module.

Contains business logic for assessment management, separated from routes.
"""

from flask import current_app
import json
from datetime import datetime

from app import db
from app.models.assessment import Assessment, SdgScore
from app.models.project import Project

def get_assessment(assessment_id):
    """Get an assessment by ID."""
    return db.session.get(Assessment, assessment_id)

def get_project_for_assessment(assessment_id):
    """Get the project associated with an assessment."""
    assessment = db.session.get(Assessment, assessment_id)
    if assessment:
        return db.session.get(Project, assessment.project_id)
    return None

def update_assessment(assessment_id, data):
    """Update an assessment."""
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        return None
    
    for key, value in data.items():
        if hasattr(assessment, key):
            setattr(assessment, key, value)
    
    assessment.updated_at = datetime.now()
    db.session.commit()
    return assessment

def create_assessment(project_id, user_id):
    """Create a new assessment for a project."""
    assessment = Assessment(
        project_id=project_id,
        user_id=user_id,
        status='draft',
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.session.add(assessment)
    db.session.commit()
    
    return assessment

def save_assessment_scores(assessment_id, sdgs, form_data):
    """Save SDG scores from form data."""
    try:
        for sdg in sdgs:
            score_value = form_data.get(f'score_{sdg.id}')
            notes = form_data.get(f'notes_{sdg.id}')
            
            if score_value:
                existing = SdgScore.query.filter_by(assessment_id=assessment_id, sdg_id=sdg.id).first()
                
                if existing:
                    existing.score = score_value
                    existing.notes = notes
                else:
                    new_score = SdgScore(
                        assessment_id=assessment_id,
                        sdg_id=sdg.id,
                        score=score_value,
                        notes=notes
                    )
                    db.session.add(new_score)
        
        # Update assessment timestamp
        assessment = db.session.get(Assessment, assessment_id)
        assessment.updated_at = datetime.now()
        
        db.session.commit()
        return True
    
    except Exception as e:
        current_app.logger.error(f"Error saving SDG scores: {str(e)}")
        db.session.rollback()
        return False
