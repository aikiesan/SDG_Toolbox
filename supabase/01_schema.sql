-- =============================================================================
-- SDG Assessment Tool — Full Schema (PostgreSQL / Supabase)
-- Mirrors all Flask-Migrate migrations in order:
--   32f963355613 → 8cdad1c84069 → caee37c95edb → 25a094b7dccf → a1b2c3d4e5f6
--
-- Usage: Run once in Supabase SQL Editor to initialize the database.
-- After running, flask db upgrade will detect alembic_version = a1b2c3d4e5f6
-- and skip all migrations (already applied).
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Alembic version tracking
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- ---------------------------------------------------------------------------
-- Migration: 32f963355613 — Initial migration
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sdg_goals (
    id          SERIAL PRIMARY KEY,
    number      INTEGER,
    name        VARCHAR(255),
    description TEXT,
    color_code  VARCHAR(16),
    icon        VARCHAR(255),
    created_at  TIMESTAMP,
    updated_at  TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "user" (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(128),
    email         VARCHAR(128) NOT NULL,
    is_admin      BOOLEAN,
    password_hash VARCHAR(128),
    CONSTRAINT uq_user_email UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS projects (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    description  TEXT,
    project_type VARCHAR(100),
    location     VARCHAR(255),
    size_sqm     FLOAT,
    user_id      INTEGER NOT NULL REFERENCES "user"(id),
    created_at   TIMESTAMP,
    updated_at   TIMESTAMP,
    start_date   TIMESTAMP,
    end_date     TIMESTAMP,
    budget       FLOAT,
    sector       VARCHAR(100),
    status       VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS sdg_questions (
    id            SERIAL PRIMARY KEY,
    text          TEXT NOT NULL,
    type          VARCHAR(64),
    sdg_id        INTEGER NOT NULL REFERENCES sdg_goals(id),
    options       TEXT,
    display_order INTEGER,
    max_score     FLOAT,
    created_at    TIMESTAMP,
    updated_at    TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sdg_relationships (
    id            SERIAL PRIMARY KEY,
    source_sdg_id INTEGER REFERENCES sdg_goals(id),
    target_sdg_id INTEGER REFERENCES sdg_goals(id),
    strength      FLOAT NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS assessments (
    id               SERIAL PRIMARY KEY,
    project_id       INTEGER NOT NULL REFERENCES projects(id),
    user_id          INTEGER NOT NULL,
    status           VARCHAR(32),
    overall_score    FLOAT,
    created_at       TIMESTAMP,
    updated_at       TIMESTAMP,
    completed_at     TIMESTAMP,
    step1_completed  BOOLEAN,
    step2_completed  BOOLEAN,
    step3_completed  BOOLEAN,
    step4_completed  BOOLEAN,
    step5_completed  BOOLEAN,
    draft_data       TEXT,
    raw_expert_data  JSON,
    assessment_type  VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS question_responses (
    id             SERIAL PRIMARY KEY,
    assessment_id  INTEGER NOT NULL REFERENCES assessments(id),
    question_id    INTEGER NOT NULL REFERENCES sdg_questions(id),
    response_score FLOAT,
    response_text  TEXT,
    created_at     TIMESTAMP,
    updated_at     TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sdg_scores (
    id               SERIAL PRIMARY KEY,
    assessment_id    INTEGER NOT NULL REFERENCES assessments(id),
    sdg_id           INTEGER NOT NULL REFERENCES sdg_goals(id),
    direct_score     FLOAT,
    bonus_score      FLOAT,
    total_score      FLOAT,
    raw_score        FLOAT,
    max_possible     FLOAT,
    percentage_score FLOAT,
    question_count   INTEGER,
    response_text    TEXT,
    notes            TEXT,
    created_at       TIMESTAMP,
    updated_at       TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- Migration: 8cdad1c84069 — Create sdg_questions_view
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW sdg_questions_view AS
SELECT
    q.id,
    q.text,
    q.type,
    q.sdg_id    AS primary_sdg_id,
    g.number    AS sdg_number,
    g.name      AS sdg_name,
    q.max_score
FROM sdg_questions q
JOIN sdg_goals g ON q.sdg_id = g.id;

-- ---------------------------------------------------------------------------
-- Migration: caee37c95edb — Add UIA integration fields to user
-- ---------------------------------------------------------------------------

ALTER TABLE "user"
    ADD COLUMN IF NOT EXISTS uia_user_id  VARCHAR(64),
    ADD COLUMN IF NOT EXISTS organization VARCHAR(256),
    ADD COLUMN IF NOT EXISTS uia_role     VARCHAR(64);

CREATE UNIQUE INDEX IF NOT EXISTS ix_user_uia_user_id ON "user" (uia_user_id);

-- ---------------------------------------------------------------------------
-- Migration: 25a094b7dccf — Add performance indexes
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS ix_assessments_project_id     ON assessments (project_id);
CREATE INDEX IF NOT EXISTS ix_assessments_user_id        ON assessments (user_id);
CREATE INDEX IF NOT EXISTS ix_assessments_status         ON assessments (status);
CREATE INDEX IF NOT EXISTS ix_assessments_project_status ON assessments (project_id, status);

CREATE INDEX IF NOT EXISTS ix_sdg_scores_assessment_id   ON sdg_scores (assessment_id);
CREATE INDEX IF NOT EXISTS ix_sdg_scores_sdg_id          ON sdg_scores (sdg_id);
CREATE INDEX IF NOT EXISTS ix_sdg_scores_assessment_sdg  ON sdg_scores (assessment_id, sdg_id);

CREATE INDEX IF NOT EXISTS ix_question_responses_assessment_id ON question_responses (assessment_id);
CREATE INDEX IF NOT EXISTS ix_question_responses_question_id   ON question_responses (question_id);

CREATE INDEX IF NOT EXISTS ix_projects_user_id ON projects (user_id);

-- ---------------------------------------------------------------------------
-- Migration: a1b2c3d4e5f6 — Add share_token and share_expires to assessments
-- ---------------------------------------------------------------------------

ALTER TABLE assessments
    ADD COLUMN IF NOT EXISTS share_token   VARCHAR(64),
    ADD COLUMN IF NOT EXISTS share_expires TIMESTAMP;

CREATE UNIQUE INDEX IF NOT EXISTS ix_assessments_share_token ON assessments (share_token);

-- ---------------------------------------------------------------------------
-- UIA Import Extension — Add project metadata columns for Excel import
-- ---------------------------------------------------------------------------

ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS external_code VARCHAR(16),
    ADD COLUMN IF NOT EXISTS authors       TEXT,
    ADD COLUMN IF NOT EXISTS organization  VARCHAR(255),
    ADD COLUMN IF NOT EXISTS uia_region    VARCHAR(64),
    ADD COLUMN IF NOT EXISTS selected      BOOLEAN DEFAULT false;

CREATE INDEX IF NOT EXISTS ix_projects_external_code ON projects (external_code);

-- ---------------------------------------------------------------------------
-- Set alembic version to current head so flask db upgrade is a no-op
-- ---------------------------------------------------------------------------

INSERT INTO alembic_version (version_num)
VALUES ('a1b2c3d4e5f6')
ON CONFLICT DO NOTHING;
