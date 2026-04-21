#!/usr/bin/env python3
"""
Test assessment creation manually.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.project import Project
from app.models.assessment import Assessment, SdgScore
from app.models.user import User
from app.models.sdg import SdgGoal
from app.scoring_logic import calculate_scores_python

def test_assessment_creation():
    app = create_app()
    with app.app_context():
        # Find the test user and project
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            print("Test user not found!")
            return
        
        test_project = Project.query.filter_by(user_id=test_user.id).first()
        if not test_project:
            print("Test project not found!")
            return
        
        print(f"Found test user: {test_user.name} (ID: {test_user.id})")
        print(f"Found test project: {test_project.name} (ID: {test_project.id})")
        
        # Create sample expert assessment data
        sample_data = {
            'sdg1_cost_reduction': 'cost_reduc_3',
            'sdg1_baseline_cost': 'Test baseline cost data',
            'sdg1_notes': 'Test notes for SDG 1',
            'sdg2_food_integration': 'community',
            'sdg2_notes': 'Test notes for SDG 2',
            'sdg3_actions': ['materials', 'air_quality'],
            'sdg3_health_summary': '3',
            'sdg3_notes': 'Test notes for SDG 3'
        }
        
        print(f"Creating assessment with sample data...")
        
        # Create Assessment Record
        new_assessment = Assessment(
            project_id=test_project.id,
            user_id=test_user.id,
            status='completed',
            assessment_type='expert',
            raw_expert_data=sample_data,
            completed_at=datetime.utcnow()
        )
        
        db.session.add(new_assessment)
        
        try:
            # Calculate scores
            calculated_scores = calculate_scores_python(sample_data)
            print(f"Calculated scores: {len(calculated_scores)} SDGs")
            
            # Create SdgScore Records  
            total_sum = 0
            valid_scores_count = 0
            sdg_goals_map = {goal.number: goal.id for goal in SdgGoal.query.all()}
            
            for score_data in calculated_scores[:3]:  # Just first 3 for testing
                sdg_number = score_data.get('number')
                sdg_goal_id = sdg_goals_map.get(sdg_number)
                
                if sdg_goal_id is None:
                    print(f"Could not find SDG Goal ID for number {sdg_number}")
                    continue
                
                sdg_score_record = SdgScore(
                    sdg_id=sdg_goal_id,
                    total_score=score_data.get('total_score', 0),
                    notes=sample_data.get(f'sdg{sdg_number}_notes', ''),
                    direct_score=score_data.get('direct_score', 0),
                    bonus_score=score_data.get('bonus_score', 0)
                )
                new_assessment.sdg_scores.append(sdg_score_record)
                
                # For calculating overall score
                if score_data.get('total_score') is not None:
                    total_sum += score_data['total_score']
                    valid_scores_count += 1
            
            # Calculate overall score
            new_assessment.overall_score = (total_sum / valid_scores_count) if valid_scores_count > 0 else 0
            
            # Commit to database
            db.session.commit()
            
            print(f"✓ Assessment created successfully!")
            print(f"✓ Assessment ID: {new_assessment.id}")
            print(f"✓ Overall Score: {new_assessment.overall_score}")
            print(f"✓ Project now has {test_project.assessment_count} assessments")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating assessment: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_assessment_creation() 