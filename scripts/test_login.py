#!/usr/bin/env python3
"""
Test login as test user.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User

def test_login():
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            # Find the test user
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                print("❌ Test user not found!")
                return
            
            print(f"✓ Found test user: {test_user.name} (ID: {test_user.id})")
            
            # Test login page
            response = client.get('/auth/login')
            print(f"Login page status: {response.status_code}")
            
            # Try to login
            response = client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'testpassword123',
                'csrf_token': 'dummy'  # You might need to extract this from the form
            }, follow_redirects=True)
            
            print(f"Login attempt status: {response.status_code}")
            print(f"Final URL: {response.request.path if response.request else 'unknown'}")
            
            # Try to access projects page
            response = client.get('/projects/', follow_redirects=True)
            print(f"Projects page status: {response.status_code}")
            
            # Check if we see project data in the response
            if 'Test Project for Assessments' in response.get_data(as_text=True):
                print("✓ Project found in response!")
            else:
                print("❌ Project NOT found in response")
                
            # Check if we see the empty state
            if 'Start Your Sustainability Journey' in response.get_data(as_text=True):
                print("❌ Showing empty state (no projects found)")
            else:
                print("✓ Not showing empty state")

if __name__ == '__main__':
    test_login() 