from app import create_app, db
from app.models.user import User  # Import all your models

app = create_app()
with app.app_context():
    # Print the database URI for verification
    print(f"Creating database at: {app.config['SQLALCHEMY_DATABASE_URI']}")
    db.create_all()
    print("Database tables created successfully!")
