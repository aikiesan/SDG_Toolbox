import sqlite3

# Define your strength values here as a list of tuples:
# (source_sdg_id, target_sdg_id, strength)
STRENGTHS = [
    # Example entries - REPLACE with your actual SDG relationship strengths
    (1, 2, 0.8),
    (2, 3, 0.9),
    (3, 4, 0.7),
    # Add more as needed...
]

DB_PATH = 'sdg_assessment.db'  # Adjust if your DB is elsewhere

def populate_strengths():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    updated = 0
    for src, tgt, strength in STRENGTHS:
        cursor.execute(
            'UPDATE sdg_relationships SET strength = ? WHERE source_sdg_id = ? AND target_sdg_id = ?',
            (strength, src, tgt)
        )
        updated += cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Updated {updated} sdg_relationships with strength values.")

if __name__ == '__main__':
    populate_strengths()
