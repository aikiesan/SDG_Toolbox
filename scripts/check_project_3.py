#!/usr/bin/env python3
"""
Check project 3 and recent assessments.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.project import Project
from app.models.assessment import Assessment
from app.models.user import User

def check_project_3():
    app = create_app()
    with app.app_context():
        # Check project ID 3 specifically
        project = Project.query.get(3)
        if project:
            print(f'✓ Project 3 found: {project.name}')
            print(f'  Owner: {project.user.name} ({project.user.email})')
            print(f'  Assessment count: {project.assessment_count}')
            
            assessments = Assessment.query.filter_by(project_id=3).order_by(Assessment.id.desc()).all()
            print(f'  Assessments in DB: {len(assessments)}')
            for i, a in enumerate(assessments, 1):
                print(f'    {i}. ID:{a.id} Type:{a.assessment_type} Status:{a.status} Score:{a.overall_score}')
                print(f'       Completed: {a.completed_at}')
        else:
            print('❌ Project 3 not found')
            
        # Check the most recent assessments across all projects
        print(f'\n--- Most Recent 10 Assessments ---')
        recent_assessments = Assessment.query.order_by(Assessment.id.desc()).limit(10).all()
        for a in recent_assessments:
            project_name = a.project.name if a.project else 'Unknown'
            print(f'ID:{a.id} Project:{project_name}(ID:{a.project_id}) Type:{a.assessment_type} Score:{a.overall_score}')

if __name__ == '__main__':
    check_project_3() 