# Technical Architecture Overview

## System Components
- **Backend:** Python (Flask), modular structure:
  - `models/`: Database models for users, projects, assessments, SDG scores, etc.
  - `routes/`: Web and API routes for user, project, and assessment management.
  - `services/`: Business logic (e.g., scoring, SDG analysis).
  - `utils/`: Helper functions for database, authentication, etc.
- **Frontend:** Jinja2 templates, Bootstrap, and static assets for a responsive UI.
- **Database:** SQLite (development); migration scripts for schema management.
- **Authentication:** User registration, login, and password reset system.
- **Visualization:** Chart.js and custom JS modules for charts, graphs, and data export (CSV, PDF, image).
- **API:** RESTful endpoints for project, assessment, and SDG data (see `routes/api.py`).

## Data Flow
1. User registers/logs in.
2. User creates a project and completes the SDG assessment questionnaire.
3. Backend processes responses, calculates scores, and stores results.
4. User receives visual feedback (charts, graphs) and can review or export assessments from their dashboard.

## GDPR & Data Deletion
- Users can delete projects and assessments; all related data is removed (cascade deletion).
- Privacy policy and terms are provided; technical consent and erasure flows are being implemented.

## Extensibility
- Modular codebase enables easy addition of new features (e.g., AI analytics, new SDG modules).
- Designed for future migration to more scalable databases and deployment environments.

For more details, see the codebase and other documentation files.
