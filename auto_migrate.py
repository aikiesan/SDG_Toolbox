import sqlite3
import os

# Path to your main SQLite database (update if needed)
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'sdgassessmentdev.db')

# Define the columns you want to ensure exist in the sdg_scores table
required_columns = [
    ('raw_score', 'REAL'),
    ('max_possible', 'REAL'),
    ('percentage_score', 'REAL'),
    ('question_count', 'INTEGER')
]

def get_existing_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def auto_migrate_sdg_scores():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        existing_columns = get_existing_columns(cursor, 'sdg_scores')
        for col_name, col_type in required_columns:
            if col_name not in existing_columns:
                print(f"Adding missing column: {col_name} {col_type}")
                cursor.execute(f"ALTER TABLE sdg_scores ADD COLUMN {col_name} {col_type}")
        conn.commit()
        print("Migration complete. All required columns are present.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    auto_migrate_sdg_scores()
