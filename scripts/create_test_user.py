from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    if not User.query.filter_by(email='test@example.com').first():
        user = User(
            name='Test User',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        print('Test user created successfully!')
    else:
        print('Test user already exists.') 