# Data Model Overview

**Version:** 1.0.0  
**Last Updated:** 2025-04-25

This document describes the main database tables and their relationships in the SDG Assessment Toolkit.

## Prerequisites
- Database server (SQLite for development, production DB for deployment)
- Python 3.9 or higher

## Main Tables

| Table Name           | Description                                  |
|---------------------|----------------------------------------------|
| users               | Stores user accounts and credentials         |
| projects            | User projects to be assessed                 |
| assessments         | SDG assessment records for each project      |
| question_responses  | Stores responses to SDG questionnaire        |
| sdg_scores          | Calculated SDG alignment scores              |
| sdg_actions         | Recommended actions based on assessment      |
| sdg_goals           | SDG goal definitions                         |
| sdg_relationships   | Relationships between SDGs                   |

> **Note:** If you have a visual ER diagram (image or PDF), consider adding it here for clarity. If you want to include one, please provide the file or let me know.

## Table Fields and Data Types
- For a complete list of fields and data types for each table, see `schema.sql` or migration scripts.
- If you would like these details included directly in this document, please provide the schema or confirm it's up to date.

## Relationships
- Each user can have multiple projects
- Each project can have multiple assessments
- Each assessment has multiple question responses and scores
- SDG actions are linked to assessments
- SDG goals and relationships are used for analysis

## Example ER Diagram (Textual)
```
users ---< projects ---< assessments ---< question_responses
                          |                |
                          |                >--- sdg_scores
                          >--- sdg_actions

sdg_goals ---< sdg_relationships
```

## Example SQL Query
```sql
-- Get all assessments for a user
SELECT a.* FROM assessments a
JOIN projects p ON a.project_id = p.id
JOIN users u ON p.user_id = u.id
WHERE u.email = 'lucassnakamura@gmail.com';
```

## Troubleshooting
- **Missing Tables/Error on Migration:** Ensure you have run all migration scripts and your database is up to date.
- **Foreign Key Errors:** Check for correct relationships and that referenced records exist.
- **Data Not Appearing:** Verify that data is inserted in the correct order (users → projects → assessments, etc.).

For full schema, see `schema.sql` or migration scripts.

---
**Maintained by Lucas Nakamura** ([lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com))
