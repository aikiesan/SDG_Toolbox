import sqlite3
import os
from datetime import datetime

# Path to your main SQLite database (update if needed)
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'sdgassessmentdev.db')

# Example SDG questions seed data
# You should expand this with your actual question set
sdg_questions = [
    # (text, type, sdg_id, options, display_order, max_score, created_at, updated_at)
    ("End poverty in all its forms everywhere", "select", 1, None, 1, 5.0, datetime.utcnow(), datetime.utcnow()),
    ("Ensure healthy lives and promote well-being for all at all ages", "select", 3, None, 2, 5.0, datetime.utcnow(), datetime.utcnow()),
    ("Achieve gender equality and empower all women and girls", "select", 5, None, 3, 5.0, datetime.utcnow(), datetime.utcnow()),
    ("Ensure availability and sustainable management of water and sanitation for all", "select", 6, None, 4, 5.0, datetime.utcnow(), datetime.utcnow()),
    # Add more questions as needed, referencing correct sdg_id from sdg_goals
]

def seed_sdg_questions():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO sdg_questions (text, type, sdg_id, options, display_order, max_score, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sdg_questions)
    conn.commit()
    conn.close()
    print(f"Seeded {len(sdg_questions)} SDG questions.")

if __name__ == '__main__':
    seed_sdg_questions()
