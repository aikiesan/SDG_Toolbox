from app import create_app, db
from app.models.user import User  # Import all your models

app = create_app()
with app.app_context():
    # Drop all existing tables
    db.drop_all()
    # Create all tables fresh
    db.create_all()
    print("Database tables recreated successfully!")
