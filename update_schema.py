from app import create_app, db

from sqlalchemy import text

app = create_app()
with app.app_context():
    conn = db.engine.connect()
    try:
        conn.execute(text('ALTER TABLE assessments ADD COLUMN draft_data TEXT'))
        print("Database schema updated successfully!")
    except Exception as e:
        print(f"Error updating schema: {e}")
