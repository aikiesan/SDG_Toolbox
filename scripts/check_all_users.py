#!/usr/bin/env python3
"""
Check all users and their projects.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.project import Project
from app.models.assessment import Assessment
from app.models.user import User

def check_all_users():
    app = create_app()
    with app.app_context():
        # Get all users
        users = User.query.all()
        print(f"Total users in database: {len(users)}")
        
        for i, user in enumerate(users, 1):
            print(f"\n--- User {i} ---")
            print(f"ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")
            print(f"Active: {user.is_active}")
            
            # Get projects for this user
            projects = Project.query.filter_by(user_id=user.id).all()
            print(f"Projects: {len(projects)}")
            
            for j, project in enumerate(projects, 1):
                assessments = Assessment.query.filter_by(project_id=project.id).all()
                print(f"  {j}. {project.name} - {len(assessments)} assessments")

if __name__ == '__main__':
    check_all_users() 