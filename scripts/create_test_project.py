#!/usr/bin/env python3
"""
Create a test project for the test user.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.project import Project
from app.models.user import User

def create_test_project():
    app = create_app()
    with app.app_context():
        # Find the test user
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            print("Test user not found!")
            return
        
        print(f"Found test user: {test_user.name} (ID: {test_user.id})")
        
        # Check if test user already has projects
        existing_projects = Project.query.filter_by(user_id=test_user.id).all()
        if existing_projects:
            print(f"Test user already has {len(existing_projects)} projects:")
            for project in existing_projects:
                print(f"  - {project.name} (ID: {project.id})")
            return
        
        # Create a test project for the test user
        test_project = Project(
            name="Test Project for Assessments",
            description="A test project to verify assessment functionality",
            project_type="Commercial",
            location="Test City, Test Country",
            size_sqm=1000.0,
            budget=50000.0,
            sector="Technology",
            user_id=test_user.id
        )
        
        db.session.add(test_project)
        db.session.commit()
        
        print(f"✓ Created test project: {test_project.name} (ID: {test_project.id})")
        print(f"✓ Project belongs to user: {test_user.name}")
        print(f"✓ Now you can log in as test@example.com and create assessments for this project!")

if __name__ == '__main__':
    create_test_project() 