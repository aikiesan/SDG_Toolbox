#!/usr/bin/env python3
"""
Simulate what each user sees on the projects page.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.project import Project
from app.models.assessment import Assessment
from app.models.user import User

def simulate_projects_page():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        
        for user in users:
            print(f"\n=== PROJECTS PAGE FOR {user.name} ({user.email}) ===")
            
            # Simulate the route query
            page = 1
            query = Project.query.filter_by(user_id=user.id)
            query = query.order_by(Project.created_at.desc())
            projects_paginated = query.paginate(page=page, per_page=10)
            
            print(f"Total projects: {projects_paginated.total}")
            print(f"Projects on this page: {len(projects_paginated.items)}")
            
            if projects_paginated.items:
                print("Projects would be displayed:")
                for project in projects_paginated.items:
                    print(f"  - {project.name}")
                    print(f"    Type: {project.project_type}")
                    print(f"    Status: {project.status}")
                    print(f"    Assessments: {project.assessment_count}")
                    print(f"    Location: {project.location or 'Not specified'}")
            else:
                print("❌ NO PROJECTS - Would show empty state message")
            
            print("-" * 50)

if __name__ == '__main__':
    simulate_projects_page() 