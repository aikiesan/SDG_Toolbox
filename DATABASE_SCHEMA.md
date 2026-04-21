# Database Schema Documentation

**Version:** 1.0.0
**Last Updated:** 2025-12-01
**Database Type:** SQLite (Development), PostgreSQL/MySQL (Production)
**ORM:** SQLAlchemy 2.0.30

---

## 📋 Table of Contents

- [Overview](#overview)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Table Definitions](#table-definitions)
- [Relationships](#relationships)
- [Indexes](#indexes)
- [Sample SQL Queries](#sample-sql-queries)
- [Migration Notes](#migration-notes)
- [Data Integrity Rules](#data-integrity-rules)
- [Backup Recommendations](#backup-recommendations)

---

## 🌐 Overview

The SDG Assessment Toolkit database consists of **8 main tables** that support:
- User authentication and management
- Project tracking and organization
- SDG assessment workflows
- Questionnaire responses
- SDG scoring and calculations
- SDG goal definitions and relationships

### Database Design Principles
- **Normalization**: 3NF (Third Normal Form) for data integrity
- **Referential Integrity**: Foreign key constraints with cascade deletes
- **Timestamps**: All tables have `created_at` and `updated_at` fields
- **Soft Deletes**: Not implemented (hard deletes with cascading)
- **ORM-First**: Designed for SQLAlchemy with compatibility for raw SQL

---

## 🗺️ Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABASE SCHEMA                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│      users       │
│──────────────────│
│ PK  id           │
│     name         │
│ UQ  email        │
│     password_hash│
│     is_admin     │
└────────┬─────────┘
         │
         │ 1:N (one user has many projects)
         │
         ▼
┌──────────────────┐
│    projects      │
│──────────────────│
│ PK  id           │
│     name         │
│     description  │
│     project_type │
│     location     │
│     size_sqm     │
│     budget       │
│     sector       │
│     status       │
│     start_date   │
│     end_date     │
│ FK  user_id      │◄────────────────────┐
│     created_at   │                     │ References users(id)
│     updated_at   │                     │
└────────┬─────────┘                     │
         │                               │
         │ 1:N (one project has many assessments)
         │                               │
         ▼                               │
┌──────────────────┐                     │
│   assessments    │                     │
│──────────────────│                     │
│ PK  id           │                     │
│ FK  project_id   │─────────────────────┘ References projects(id)
│     user_id      │ (denormalized for quick access)
│     status       │ (draft, in_progress, completed)
│     overall_score│
│     draft_data   │ (JSON blob for saving progress)
│     raw_expert_  │ (JSON blob for expert assessment)
│     data         │
│     assessment_  │ (standard, expert)
│     type         │
│     step1_       │
│     completed    │
│     step2_       │
│     completed    │
│     step3_       │
│     completed    │
│     step4_       │
│     completed    │
│     step5_       │
│     completed    │
│     created_at   │
│     updated_at   │
│     completed_at │
└────────┬─────────┘
         │
         ├─────────────────┬──────────────────┐
         │ 1:N             │ 1:N              │ 1:N
         │                 │                  │
         ▼                 ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  sdg_scores      │ │  question_   │ │   sdg_actions    │
│──────────────────│ │  responses   │ │──────────────────│
│ PK  id           │ │──────────────│ │ PK  id           │
│ FK  assessment_id│ │ PK  id       │ │ FK  assessment_id│
│ FK  sdg_id       │ │ FK  assessment│ │ FK  sdg_id       │
│     direct_score │ │     _id      │ │     action_text  │
│     bonus_score  │ │ FK  question │ │     priority     │
│     total_score  │ │     _id      │ │     status       │
│     raw_score    │ │     response │ │     created_at   │
│     max_possible │ │     _text    │ └──────────────────┘
│     percentage_  │ │     score    │
│     score        │ │     created_at│
│     question_    │ │     updated_at│
│     count        │ └──────┬───────┘
│     response_text│        │
│     notes        │        │ N:1
│     created_at   │        │
│     updated_at   │        ▼
└────────┬─────────┘ ┌──────────────────┐
         │           │  sdg_questions   │
         │           │──────────────────│
         │ N:1       │ PK  id           │
         │           │ FK  sdg_id       │
         │           │     question_text│
         │           │     category     │
         │           │     weight       │
         │           │     max_points   │
         │           │     question_type│
         │           │     created_at   │
         │           └──────────────────┘
         │
         │ N:1              ┌────────────────────┐
         └──────────────────►    sdg_goals       │
                            │────────────────────│
                            │ PK  id             │
                   ┌────────┤ UQ  number (1-17)  │
                   │        │     title          │
                   │        │     description    │
                   │        │     color_code     │
                   │        │     icon_url       │
                   │        │     created_at     │
                   │        └──────┬─────────────┘
                   │               │
                   │               │ Self-referencing M:N
                   │               │ (SDG synergies/relationships)
                   │               ▼
                   │        ┌──────────────────────┐
                   │        │  sdg_relationships   │
                   │        │──────────────────────│
                   │        │ PK  id               │
                   └────────┤ FK  goal1_id         │
                            │ FK  goal2_id         │
                            │     relationship_type│
                            │     strength         │
                            │     description      │
                            │     created_at       │
                            └──────────────────────┘

Legend:
  PK  = Primary Key
  FK  = Foreign Key
  UQ  = Unique Constraint
  1:N = One-to-Many Relationship
  N:1 = Many-to-One Relationship
  M:N = Many-to-Many Relationship
```

---

## 📊 Table Definitions

### 1. `users` Table

Stores user accounts and authentication credentials.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `name` | VARCHAR(128) | NULL | User's full name |
| `email` | VARCHAR(128) | UNIQUE, NOT NULL | User's email address (used for login) |
| `password_hash` | VARCHAR(128) | NOT NULL | Hashed password (PBKDF2 via Werkzeug) |
| `is_admin` | BOOLEAN | DEFAULT FALSE | Admin flag for elevated privileges |

**Indexes:**
- Primary: `id`
- Unique: `email`

**SQLAlchemy Model:** `app/models/user.py::User`

**Example:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128),
    email VARCHAR(128) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT 0
);
```

---

### 2. `projects` Table

Stores architectural and urban planning projects.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique project identifier |
| `name` | VARCHAR(255) | NOT NULL | Project name |
| `description` | TEXT | NULL | Detailed project description |
| `project_type` | VARCHAR(100) | NULL | Type of project (e.g., "Residential", "Commercial") |
| `location` | VARCHAR(255) | NULL | Project location/address |
| `size_sqm` | FLOAT | NULL | Project size in square meters |
| `budget` | FLOAT | NULL | Project budget in local currency |
| `sector` | VARCHAR(100) | NULL | Sector (Residential, Commercial, Education, etc.) |
| `status` | VARCHAR(50) | DEFAULT 'planning' | Project status (planning, in_progress, completed) |
| `start_date` | DATETIME | NULL | Planned/actual start date |
| `end_date` | DATETIME | NULL | Planned/actual end date |
| `user_id` | INTEGER | FOREIGN KEY → users(id), NOT NULL | Project owner |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, ON UPDATE | Last update timestamp |

**Indexes:**
- Primary: `id`
- Foreign Key: `user_id` → `users(id)` (CASCADE DELETE)
- Index: `user_id` (for fast user queries)
- Index: `updated_at` (for sorting)

**SQLAlchemy Model:** `app/models/project.py::Project`

**Example:**
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_type VARCHAR(100),
    location VARCHAR(255),
    size_sqm REAL,
    budget REAL,
    sector VARCHAR(100),
    status VARCHAR(50) DEFAULT 'planning',
    start_date DATETIME,
    end_date DATETIME,
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

### 3. `assessments` Table

Stores SDG assessments for projects.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique assessment identifier |
| `project_id` | INTEGER | FOREIGN KEY → projects(id), NOT NULL | Associated project |
| `user_id` | INTEGER | NOT NULL | Assessment creator (denormalized) |
| `status` | VARCHAR(32) | DEFAULT 'draft' | Assessment status (draft, in_progress, completed) |
| `assessment_type` | VARCHAR(50) | DEFAULT 'standard' | Type: 'standard' or 'expert' |
| `overall_score` | FLOAT | NULL | Calculated overall SDG alignment score (0-100) |
| `draft_data` | TEXT/JSON | NULL | JSON blob for saving progress |
| `raw_expert_data` | JSON | NULL | Raw JSON data from expert assessment form |
| `step1_completed` | BOOLEAN | DEFAULT FALSE | Project information step completed |
| `step2_completed` | BOOLEAN | DEFAULT FALSE | Questionnaire step completed |
| `step3_completed` | BOOLEAN | DEFAULT FALSE | Scoring step completed |
| `step4_completed` | BOOLEAN | DEFAULT FALSE | Results step completed |
| `step5_completed` | BOOLEAN | DEFAULT FALSE | Actions/recommendations step completed |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| `completed_at` | DATETIME | NULL | Assessment completion timestamp |

**Indexes:**
- Primary: `id`
- Foreign Key: `project_id` → `projects(id)` (CASCADE DELETE)
- Index: `user_id` (for user queries)
- Index: `status` (for filtering)
- Index: `created_at` (for sorting)

**SQLAlchemy Model:** `app/models/assessment.py::Assessment`

**Example:**
```sql
CREATE TABLE assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status VARCHAR(32) DEFAULT 'draft',
    assessment_type VARCHAR(50) DEFAULT 'standard',
    overall_score REAL,
    draft_data TEXT,
    raw_expert_data TEXT,  -- JSON stored as TEXT in SQLite
    step1_completed BOOLEAN DEFAULT 0,
    step2_completed BOOLEAN DEFAULT 0,
    step3_completed BOOLEAN DEFAULT 0,
    step4_completed BOOLEAN DEFAULT 0,
    step5_completed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

---

### 4. `sdg_scores` Table

Stores calculated SDG scores for each assessment.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique score record identifier |
| `assessment_id` | INTEGER | FOREIGN KEY → assessments(id), NOT NULL | Associated assessment |
| `sdg_id` | INTEGER | FOREIGN KEY → sdg_goals(id), NOT NULL | SDG goal being scored |
| `direct_score` | FLOAT | NULL | Score from direct questions (0-100) |
| `bonus_score` | FLOAT | NULL | Bonus from related SDGs (synergies) |
| `total_score` | FLOAT | NULL | Direct + Bonus (capped at 100) |
| `raw_score` | FLOAT | NULL | Sum of raw points from questions |
| `max_possible` | FLOAT | NULL | Maximum possible points for this SDG |
| `percentage_score` | FLOAT | NULL | (Raw / MaxPossible) * 100 |
| `question_count` | INTEGER | NULL | Number of questions answered |
| `response_text` | TEXT | NULL | Text response for expert assessment |
| `notes` | TEXT | NULL | Additional notes/justification |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- Primary: `id`
- Foreign Key: `assessment_id` → `assessments(id)` (CASCADE DELETE)
- Foreign Key: `sdg_id` → `sdg_goals(id)`
- Composite Index: `(assessment_id, sdg_id)` (UNIQUE)

**SQLAlchemy Model:** `app/models/assessment.py::SdgScore`

**Example:**
```sql
CREATE TABLE sdg_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    sdg_id INTEGER NOT NULL,
    direct_score REAL,
    bonus_score REAL,
    total_score REAL,
    raw_score REAL,
    max_possible REAL,
    percentage_score REAL,
    question_count INTEGER,
    response_text TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    FOREIGN KEY (sdg_id) REFERENCES sdg_goals(id),
    UNIQUE (assessment_id, sdg_id)
);
```

---

### 5. `sdg_goals` Table

Stores the 17 UN Sustainable Development Goals.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique SDG identifier |
| `number` | INTEGER | UNIQUE, NOT NULL | SDG number (1-17) |
| `title` | VARCHAR(255) | NOT NULL | SDG title (e.g., "No Poverty") |
| `description` | TEXT | NULL | Detailed SDG description |
| `color_code` | VARCHAR(7) | NULL | Hex color code for visualization (e.g., "#E5243B") |
| `icon_url` | VARCHAR(255) | NULL | URL or path to SDG icon |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Indexes:**
- Primary: `id`
- Unique: `number`

**SQLAlchemy Model:** `app/models/sdg.py::SdgGoal`

**Example:**
```sql
CREATE TABLE sdg_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    color_code VARCHAR(7),
    icon_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data:**
```sql
INSERT INTO sdg_goals (number, title, color_code) VALUES
(1, 'No Poverty', '#E5243B'),
(2, 'Zero Hunger', '#DDA63A'),
(3, 'Good Health and Well-being', '#4C9F38'),
-- ... (all 17 SDGs)
(17, 'Partnerships for the Goals', '#19486A');
```

---

### 6. `sdg_questions` Table

Stores questionnaire questions for each SDG.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique question identifier |
| `sdg_id` | INTEGER | FOREIGN KEY → sdg_goals(id), NOT NULL | Associated SDG goal |
| `question_text` | TEXT | NOT NULL | The actual question text |
| `category` | VARCHAR(100) | NULL | Question category (e.g., "Environmental", "Social") |
| `weight` | FLOAT | DEFAULT 1.0 | Question weight in scoring (1.0 = normal) |
| `max_points` | FLOAT | DEFAULT 10.0 | Maximum points for this question |
| `question_type` | VARCHAR(50) | DEFAULT 'multiple_choice' | Type: multiple_choice, text, boolean |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Indexes:**
- Primary: `id`
- Foreign Key: `sdg_id` → `sdg_goals(id)`
- Index: `sdg_id` (for filtering by SDG)

**SQLAlchemy Model:** `app/models/sdg.py::SdgQuestion`

**Example:**
```sql
CREATE TABLE sdg_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sdg_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    category VARCHAR(100),
    weight REAL DEFAULT 1.0,
    max_points REAL DEFAULT 10.0,
    question_type VARCHAR(50) DEFAULT 'multiple_choice',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sdg_id) REFERENCES sdg_goals(id)
);
```

---

### 7. `question_responses` Table

Stores user responses to questionnaire questions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique response identifier |
| `assessment_id` | INTEGER | FOREIGN KEY → assessments(id), NOT NULL | Associated assessment |
| `question_id` | INTEGER | FOREIGN KEY → sdg_questions(id), NOT NULL | Question being answered |
| `response_text` | TEXT | NULL | User's text response |
| `score` | FLOAT | NULL | Calculated score for this response |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- Primary: `id`
- Foreign Key: `assessment_id` → `assessments(id)` (CASCADE DELETE)
- Foreign Key: `question_id` → `sdg_questions(id)`
- Composite Index: `(assessment_id, question_id)` (UNIQUE)

**SQLAlchemy Model:** `app/models/response.py::QuestionResponse`

**Example:**
```sql
CREATE TABLE question_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    response_text TEXT,
    score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES sdg_questions(id),
    UNIQUE (assessment_id, question_id)
);
```

---

### 8. `sdg_relationships` Table

Stores synergistic relationships between SDGs (for bonus scoring).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique relationship identifier |
| `goal1_id` | INTEGER | FOREIGN KEY → sdg_goals(id), NOT NULL | First SDG in relationship |
| `goal2_id` | INTEGER | FOREIGN KEY → sdg_goals(id), NOT NULL | Second SDG in relationship |
| `relationship_type` | VARCHAR(50) | NULL | Type: synergy, trade-off, neutral |
| `strength` | FLOAT | DEFAULT 0.5 | Relationship strength (0.0-1.0) |
| `description` | TEXT | NULL | Description of the relationship |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Indexes:**
- Primary: `id`
- Foreign Key: `goal1_id` → `sdg_goals(id)`
- Foreign Key: `goal2_id` → `sdg_goals(id)`
- Composite Index: `(goal1_id, goal2_id)` (UNIQUE)

**SQLAlchemy Model:** `app/models/sdg_relationship.py::SdgRelationship`

**Example:**
```sql
CREATE TABLE sdg_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal1_id INTEGER NOT NULL,
    goal2_id INTEGER NOT NULL,
    relationship_type VARCHAR(50),
    strength REAL DEFAULT 0.5,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal1_id) REFERENCES sdg_goals(id),
    FOREIGN KEY (goal2_id) REFERENCES sdg_goals(id),
    UNIQUE (goal1_id, goal2_id)
);
```

**Sample Data:**
```sql
-- SDG 7 (Affordable Energy) synergizes with SDG 13 (Climate Action)
INSERT INTO sdg_relationships (goal1_id, goal2_id, relationship_type, strength, description)
VALUES (7, 13, 'synergy', 0.8, 'Renewable energy directly supports climate action');
```

---

## 🔗 Relationships

### One-to-Many Relationships

1. **users → projects** (1:N)
   - One user can create many projects
   - Delete user → CASCADE delete all projects

2. **projects → assessments** (1:N)
   - One project can have many assessments
   - Delete project → CASCADE delete all assessments

3. **assessments → sdg_scores** (1:N)
   - One assessment has 17 SDG scores (one per SDG)
   - Delete assessment → CASCADE delete all scores

4. **assessments → question_responses** (1:N)
   - One assessment has multiple question responses
   - Delete assessment → CASCADE delete all responses

5. **sdg_goals → sdg_questions** (1:N)
   - One SDG has multiple questions
   - Delete SDG → No cascade (prevent accidental deletion)

6. **sdg_questions → question_responses** (1:N)
   - One question can be answered in multiple assessments
   - Delete question → No cascade (preserve historical data)

### Many-to-One Relationships

7. **sdg_scores → sdg_goals** (N:1)
   - Many scores reference one SDG goal

8. **question_responses → sdg_questions** (N:1)
   - Many responses reference one question

### Many-to-Many Relationships

9. **sdg_goals ↔ sdg_goals** (M:N via sdg_relationships)
   - SDGs have synergistic relationships with other SDGs
   - Implemented via junction table `sdg_relationships`

---

## 🔍 Indexes

### Recommended Indexes for Performance

```sql
-- Users table
CREATE INDEX idx_users_email ON users(email);

-- Projects table
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_updated_at ON projects(updated_at DESC);

-- Assessments table
CREATE INDEX idx_assessments_project_id ON assessments(project_id);
CREATE INDEX idx_assessments_user_id ON assessments(user_id);
CREATE INDEX idx_assessments_status ON assessments(status);
CREATE INDEX idx_assessments_created_at ON assessments(created_at DESC);

-- SDG Scores table
CREATE UNIQUE INDEX idx_sdg_scores_assessment_sdg ON sdg_scores(assessment_id, sdg_id);
CREATE INDEX idx_sdg_scores_sdg_id ON sdg_scores(sdg_id);

-- Question Responses table
CREATE UNIQUE INDEX idx_responses_assessment_question ON question_responses(assessment_id, question_id);
CREATE INDEX idx_responses_question_id ON question_responses(question_id);

-- SDG Questions table
CREATE INDEX idx_questions_sdg_id ON sdg_questions(sdg_id);

-- SDG Relationships table
CREATE UNIQUE INDEX idx_relationships_goals ON sdg_relationships(goal1_id, goal2_id);
```

---

## 📝 Sample SQL Queries

### Query 1: Get all projects for a user with assessment counts

```sql
SELECT
    p.*,
    COUNT(a.id) as assessment_count
FROM projects p
LEFT JOIN assessments a ON p.id = a.project_id
WHERE p.user_id = 1
GROUP BY p.id
ORDER BY p.updated_at DESC;
```

### Query 2: Get assessment details with SDG scores

```sql
SELECT
    a.*,
    p.name as project_name,
    ss.sdg_id,
    g.title as sdg_title,
    ss.total_score,
    ss.percentage_score
FROM assessments a
JOIN projects p ON a.project_id = p.id
LEFT JOIN sdg_scores ss ON a.id = ss.assessment_id
LEFT JOIN sdg_goals g ON ss.sdg_id = g.id
WHERE a.id = 123
ORDER BY g.number;
```

### Query 3: Calculate average SDG scores across all assessments

```sql
SELECT
    g.number,
    g.title,
    AVG(ss.total_score) as avg_score,
    COUNT(DISTINCT ss.assessment_id) as assessment_count
FROM sdg_goals g
LEFT JOIN sdg_scores ss ON g.id = ss.sdg_id
LEFT JOIN assessments a ON ss.assessment_id = a.id
WHERE a.status = 'completed'
GROUP BY g.id
ORDER BY g.number;
```

### Query 4: Get all questions for a specific SDG

```sql
SELECT
    sq.*,
    g.title as sdg_title
FROM sdg_questions sq
JOIN sdg_goals g ON sq.sdg_id = g.id
WHERE g.number = 7  -- SDG 7: Affordable and Clean Energy
ORDER BY sq.id;
```

### Query 5: Get user's completed assessments with overall scores

```sql
SELECT
    a.id,
    a.created_at,
    a.completed_at,
    a.overall_score,
    p.name as project_name,
    p.location,
    COUNT(ss.id) as sdg_count
FROM assessments a
JOIN projects p ON a.project_id = p.id
LEFT JOIN sdg_scores ss ON a.id = ss.assessment_id
WHERE a.user_id = 1
  AND a.status = 'completed'
GROUP BY a.id
ORDER BY a.completed_at DESC;
```

### Query 6: Find SDG synergies for a specific goal

```sql
SELECT
    g1.number as sdg1_number,
    g1.title as sdg1_title,
    g2.number as sdg2_number,
    g2.title as sdg2_title,
    sr.relationship_type,
    sr.strength,
    sr.description
FROM sdg_relationships sr
JOIN sdg_goals g1 ON sr.goal1_id = g1.id
JOIN sdg_goals g2 ON sr.goal2_id = g2.id
WHERE g1.number = 13  -- SDG 13: Climate Action
ORDER BY sr.strength DESC;
```

### Query 7: Get assessment progress (step completion)

```sql
SELECT
    a.id,
    p.name as project_name,
    a.status,
    a.step1_completed,
    a.step2_completed,
    a.step3_completed,
    a.step4_completed,
    a.step5_completed,
    (CAST(a.step1_completed AS INTEGER) +
     CAST(a.step2_completed AS INTEGER) +
     CAST(a.step3_completed AS INTEGER) +
     CAST(a.step4_completed AS INTEGER) +
     CAST(a.step5_completed AS INTEGER)) * 20 as progress_percentage
FROM assessments a
JOIN projects p ON a.project_id = p.id
WHERE a.user_id = 1
  AND a.status IN ('draft', 'in_progress')
ORDER BY a.updated_at DESC;
```

---

## 🔄 Migration Notes

### Migrating from SQLite to PostgreSQL

#### 1. Export Data from SQLite

```bash
# Export using SQLite .dump
sqlite3 instance/sdgassessmentdev.db .dump > dump.sql

# Or use a Python script with SQLAlchemy
python scripts/export_sqlite.py
```

#### 2. Convert SQL Dialect

SQLite → PostgreSQL differences:
- `AUTOINCREMENT` → `SERIAL` or `BIGSERIAL`
- `DATETIME` → `TIMESTAMP`
- `REAL` → `DOUBLE PRECISION` or `NUMERIC`
- `BOOLEAN` (0/1 in SQLite) → `BOOLEAN` (true/false in PostgreSQL)

#### 3. Import to PostgreSQL

```bash
# Create database
createdb sdg_assessment

# Import schema via migrations
export DATABASE_URL='postgresql://user:pass@localhost/sdg_assessment'
flask db upgrade

# Import data
psql sdg_assessment < converted_dump.sql
```

### Migrating from SQLite to MySQL

#### Differences:
- `AUTOINCREMENT` → `AUTO_INCREMENT`
- Text fields may need explicit length limits
- `DATETIME` handling (MySQL is timezone-naive by default)

#### Import:
```bash
mysql -u root -p
CREATE DATABASE sdg_assessment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit

mysql -u root -p sdg_assessment < converted_dump.sql
```

### Schema Versioning

This project uses **Alembic** for database migrations:

```bash
# Create new migration
flask db migrate -m "Add new column to assessments"

# Review migration in migrations/versions/

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

---

## ✅ Data Integrity Rules

### Constraints

1. **Foreign Key Constraints:**
   - All foreign keys must reference existing records
   - Cascade deletes: user → projects → assessments → scores/responses
   - Prevent orphaned records

2. **Unique Constraints:**
   - `users.email` must be unique
   - `sdg_goals.number` must be unique (1-17)
   - `(assessment_id, sdg_id)` in `sdg_scores` must be unique
   - `(assessment_id, question_id)` in `question_responses` must be unique

3. **NOT NULL Constraints:**
   - Critical fields like `email`, `name`, `project_id`, `assessment_id` cannot be null

4. **Check Constraints (not enforced in SQLite, but recommended):**
   ```sql
   -- SDG number must be between 1 and 17
   CHECK (number >= 1 AND number <= 17)

   -- Scores must be 0-100
   CHECK (total_score >= 0 AND total_score <= 100)

   -- Size and budget must be positive
   CHECK (size_sqm > 0)
   CHECK (budget > 0)
   ```

### Application-Level Validation

Enforced in `app/models/*.py`:
- Email format validation
- Password strength requirements
- Project size limits (< 1,000,000 sqm)
- End date must be after start date
- Score capping at 100

---

## 💾 Backup Recommendations

### Development (SQLite)

```bash
# Simple file copy
cp instance/sdgassessmentdev.db instance/backups/sdg_$(date +%Y%m%d_%H%M%S).db

# Using SQLite .dump
sqlite3 instance/sdgassessmentdev.db .dump | gzip > backups/sdg_$(date +%Y%m%d).sql.gz
```

### Production (PostgreSQL)

```bash
# Full database backup
pg_dump -U sdg_user -F c -b -v -f backups/sdg_$(date +%Y%m%d).backup sdg_assessment

# SQL dump
pg_dump -U sdg_user sdg_assessment | gzip > backups/sdg_$(date +%Y%m%d).sql.gz

# Restore
pg_restore -U sdg_user -d sdg_assessment -v backups/sdg_20251201.backup
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /path/to/backup_script.sh  # Daily at 2 AM
```

**backup_script.sh:**
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/sdg_assessment"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U sdg_user sdg_assessment | gzip > $BACKUP_DIR/sdg_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "sdg_*.sql.gz" -mtime +30 -delete
```

### Backup Strategy

- **Frequency:** Daily backups, weekly full backups
- **Retention:** Keep 30 daily, 12 weekly, 12 monthly
- **Storage:** Off-site storage (S3, Google Cloud Storage, etc.)
- **Testing:** Regularly test backup restoration
- **Encryption:** Encrypt backups at rest

---

## 📚 Additional Resources

- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
- **Flask-SQLAlchemy:** https://flask-sqlalchemy.palletsprojects.com/
- **Alembic Migrations:** https://alembic.sqlalchemy.org/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **MySQL Documentation:** https://dev.mysql.com/doc/

---

## 🔧 Maintenance Scripts

### Check Database Integrity

```python
# scripts/check_db_integrity.py
from app import db
from app.models import User, Project, Assessment, SdgScore

def check_integrity():
    # Check for orphaned records
    orphaned_projects = db.session.query(Project).filter(
        ~Project.user_id.in_(db.session.query(User.id))
    ).count()

    print(f"Orphaned projects: {orphaned_projects}")

    # Check for assessments without scores
    assessments_without_scores = db.session.query(Assessment).filter(
        Assessment.status == 'completed',
        ~Assessment.id.in_(db.session.query(SdgScore.assessment_id))
    ).count()

    print(f"Completed assessments without scores: {assessments_without_scores}")
```

### Optimize Database

```sql
-- SQLite
VACUUM;
ANALYZE;

-- PostgreSQL
VACUUM ANALYZE;
REINDEX DATABASE sdg_assessment;

-- MySQL
OPTIMIZE TABLE users, projects, assessments, sdg_scores;
ANALYZE TABLE users, projects, assessments, sdg_scores;
```

---

**For questions or clarifications, contact:** [lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com)
