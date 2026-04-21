#!/usr/bin/env python3
"""
Check test user's data in detail.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.project import Project
from app.models.assessment import Assessment
from app.models.user import User

def check_test_data():
    app = create_app()
    with app.app_context():
        # Find the test user
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            print("❌ Test user not found!")
            return
        
        print(f"✓ Found test user: {test_user.name} (ID: {test_user.id})")
        
        # Get all projects for test user
        projects = Project.query.filter_by(user_id=test_user.id).all()
        print(f"✓ Projects for test user: {len(projects)}")
        
        for i, project in enumerate(projects, 1):
            print(f"\n--- Project {i} ---")
            print(f"ID: {project.id}")
            print(f"Name: {project.name}")
            print(f"Status: {project.status}")
            print(f"Created: {project.created_at}")
            print(f"assessment_count property: {project.assessment_count}")
            
            # Get assessments for this project
            assessments = Assessment.query.filter_by(project_id=project.id).all()
            print(f"Assessments in DB: {len(assessments)}")
            
            for j, assessment in enumerate(assessments, 1):
                print(f"  Assessment {j}:")
                print(f"    ID: {assessment.id}")
                print(f"    Type: {assessment.assessment_type}")
                print(f"    Status: {assessment.status}")
                print(f"    Completed: {assessment.completed_at}")
                print(f"    Overall Score: {assessment.overall_score}")
                print(f"    SDG Scores: {len(assessment.sdg_scores)}")
        
        # Test pagination query like the route does
        print(f"\n--- Testing Route Query ---")
        page = 1
        query = Project.query.filter_by(user_id=test_user.id)
        query = query.order_by(Project.created_at.desc())
        projects_paginated = query.paginate(page=page, per_page=10)
        
        print(f"Paginated query:")
        print(f"  Total: {projects_paginated.total}")
        print(f"  Items: {len(projects_paginated.items)}")
        print(f"  Has prev: {projects_paginated.has_prev}")
        print(f"  Has next: {projects_paginated.has_next}")
        
        for project in projects_paginated.items:
            print(f"  - {project.name} (assessments: {project.assessment_count})")

if __name__ == '__main__':
    check_test_data() 