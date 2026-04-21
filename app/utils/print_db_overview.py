import sqlite3
import os

def print_table(conn, table_name):
    print(f"\n--- {table_name} ---")
    try:
        rows = conn.execute(f'SELECT * FROM {table_name}').fetchall()
        print(f"{len(rows)} rows found.")
        for row in rows:
            print(dict(row))
    except Exception as e:
        print(f"Error reading {table_name}: {e}")

def main():
    db_path = os.path.join(os.path.dirname(__file__), '../../instance/sdgassessmentdev.db')
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        # List all tables
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("Tables in database:", tables)
        for t in tables:
            print_table(conn, t)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
