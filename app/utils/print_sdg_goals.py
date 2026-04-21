import sqlite3
import os

def print_sdg_goals():
    db_path = os.path.join(os.path.dirname(__file__), '../../instance/sdgassessmentdev.db')
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute('SELECT * FROM sdg_goals ORDER BY id').fetchall()
        print(f"Found {len(rows)} rows in sdg_goals table:")
        for row in rows:
            print(dict(row))
    finally:
        conn.close()

if __name__ == "__main__":
    print_sdg_goals()
