-- Schema for sdg_scores table with all required columns
CREATE TABLE IF NOT EXISTS sdg_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    sdg_id INTEGER NOT NULL,
    score REAL,
    notes TEXT,
    direct_score REAL,
    bonus_score REAL,
    total_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id),
    FOREIGN KEY (sdg_id) REFERENCES sdg_goals(id)
);
