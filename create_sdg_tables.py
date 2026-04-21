import sqlite3
import os
from app import create_app

app = create_app()
with app.app_context():
    # Get the database path from your app config
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the sdg_goals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sdg_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number INTEGER NOT NULL UNIQUE,
        name TEXT NOT NULL,
        description TEXT,
        color_code TEXT
    );
    ''')

    # Create the sdg_scores table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sdg_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL,
        sdg_id INTEGER NOT NULL,
        total_score REAL,
        comment TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assessment_id) REFERENCES assessments(id),
        FOREIGN KEY (sdg_id) REFERENCES sdg_goals(id)
    );
    ''')

    # Insert the 17 SDG goals
    sdg_goals_data = [
        (1, 'No Poverty', '#e5243b'),
        (2, 'Zero Hunger', '#dda63a'),
        (3, 'Good Health and Well-being', '#4c9f38'),
        (4, 'Quality Education', '#c5192d'),
        (5, 'Gender Equality', '#ff3a21'),
        (6, 'Clean Water and Sanitation', '#26bde2'),
        (7, 'Affordable and Clean Energy', '#fcc30b'),
        (8, 'Decent Work and Economic Growth', '#a21942'),
        (9, 'Industry, Innovation and Infrastructure', '#fd6925'),
        (10, 'Reduced Inequalities', '#dd1367'),
        (11, 'Sustainable Cities and Communities', '#fd9d24'),
        (12, 'Responsible Consumption and Production', '#bf8b2e'),
        (13, 'Climate Action', '#3f7e44'),
        (14, 'Life Below Water', '#0a97d9'),
        (15, 'Life on Land', '#56c02b'),
        (16, 'Peace, Justice and Strong Institutions', '#00689d'),
        (17, 'Partnerships for the Goals', '#19486a')
    ]

    # Insert data
    cursor.executemany('INSERT OR IGNORE INTO sdg_goals (number, name, color_code) VALUES (?, ?, ?)', sdg_goals_data)

    conn.commit()
    conn.close()

    print('sdg_goals table created and initialized successfully.')
