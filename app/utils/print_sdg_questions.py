import sqlite3
import os

def print_sdg_questions():
    """Print all rows from the sdg_questions table for verification."""
    # Adjust the path as needed for your environment
    db_path = os.path.join(os.path.dirname(__file__), '../../instance/sdgassessmentdev.db')
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute('SELECT * FROM sdg_questions ORDER BY id').fetchall()
        print(f"Found {len(rows)} questions in sdg_questions table:")
        for row in rows:
            print(dict(row))
    finally:
        conn.close()

if __name__ == "__main__":
    print_sdg_questions()
