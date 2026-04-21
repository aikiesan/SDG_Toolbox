# SDG Assessment Tool - Development Guide

This guide covers local development setup, testing procedures, and contribution guidelines for the SDG Assessment Tool.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Git Workflow](#git-workflow)
6. [Testing](#testing)
7. [Code Style Guidelines](#code-style-guidelines)
8. [Common Development Tasks](#common-development-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker Desktop** (Windows/Mac) or **Docker Engine + Docker Compose** (Linux)
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Minimum version: Docker 20.10+, Docker Compose 1.29+

- **Git** for version control
  - [Download Git](https://git-scm.com/downloads)

- **Code Editor** (recommended)
  - [Visual Studio Code](https://code.visualstudio.com/) with Python extension
  - [PyCharm](https://www.jetbrains.com/pycharm/)

### Optional Tools

- **Python 3.11+** (for running tests outside Docker)
- **PostgreSQL client** (for direct database access)

---

## Local Development Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/sdg-assessment.git
cd sdg-assessment
```

### 2. Create Development Environment File

```bash
# Copy the example .env file
cp .env.example .env

# Or create manually
nano .env
```

**Minimal development .env configuration:**

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration
POSTGRES_USER=sdg_user
POSTGRES_PASSWORD=sdg_password
POSTGRES_DB=sdg_assessment_dev

# Database URL (for Flask-SQLAlchemy)
DATABASE_URL=postgresql://sdg_user:sdg_password@db:5432/sdg_assessment_dev

# Email Configuration (development - prints to console)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USERNAME=
MAIL_PASSWORD=
```

### 3. Start Development Environment

```bash
# Build and start containers
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

**Expected output:**
```
Creating network "sdg-assessment_default" with the default driver
Creating sdg-assessment_db_1 ... done
Creating sdg-assessment_web_1 ... done
```

### 4. Access the Application

- **Web Interface**: http://localhost:5000
- **PostgreSQL Database**: localhost:5432
  - Username: `sdg_user`
  - Password: `sdg_password`
  - Database: `sdg_assessment_dev`

### 5. Create Admin User (Optional)

```bash
# Access Flask shell
docker-compose exec web flask shell

# In the Flask shell
>>> from app import db
>>> from app.models.user import User
>>> admin = User(username='admin', email='admin@example.com', is_admin=True)
>>> admin.set_password('admin123')
>>> db.session.add(admin)
>>> db.session.commit()
>>> exit()
```

---

## Project Structure

```
sdg-assessment/
├── app/                          # Application package
│   ├── __init__.py              # App factory
│   ├── models/                  # Database models
│   │   ├── user.py             # User model
│   │   ├── project.py          # Project model
│   │   └── assessment.py       # Assessment model
│   ├── routes/                  # Route blueprints
│   │   ├── auth.py             # Authentication routes
│   │   ├── main.py             # Main routes
│   │   ├── projects.py         # Project CRUD routes
│   │   └── questionnaire.py    # Assessment routes
│   ├── services/                # Business logic
│   │   ├── email_utils.py      # Email service
│   │   └── scoring.py          # Scoring algorithms
│   ├── static/                  # Static assets
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript files
│   │   └── img/                # Images
│   └── templates/               # Jinja2 templates
│       ├── base.html           # Base template
│       ├── auth/               # Auth templates
│       ├── dashboard/          # Dashboard templates
│       ├── projects/           # Project templates
│       └── questionnaire/      # Assessment templates
├── migrations/                  # Database migrations
├── tests/                       # Test suite
│   ├── test_auth.py            # Auth tests
│   ├── test_projects.py        # Project tests
│   └── test_assessment.py      # Assessment tests
├── docker-compose.yml           # Development Docker config
├── docker-compose.prod.yml      # Production Docker config
├── Dockerfile                   # Development Dockerfile
├── Dockerfile.prod              # Production Dockerfile
├── requirements.txt             # Python dependencies
├── gunicorn_config.py           # Development Gunicorn config
├── gunicorn_config.prod.py      # Production Gunicorn config
├── entrypoint.sh                # Container startup script
├── .env                         # Environment variables (gitignored)
├── .env.production.template     # Production env template
└── README.md                    # Project overview
```

---

## Development Workflow

### Hot Reload

The development environment is configured for **automatic code reloading**:

- **Python code changes** → Gunicorn auto-reloads (via `reload=True` in `gunicorn_config.py`)
- **Template changes** → Flask auto-reloads templates
- **Static files** → Changes reflected immediately (volume-mounted)

**No need to restart containers** for most changes!

### Making Code Changes

1. **Edit files locally** in your code editor
2. **Save the file**
3. **Refresh browser** to see changes (Python/template) or hard refresh (CSS/JS with Ctrl+F5)

### Database Migrations

#### Creating a New Migration

```bash
# After modifying models (e.g., app/models/user.py)

# Create migration
docker-compose exec web flask db migrate -m "Add new field to User model"

# Review generated migration in migrations/versions/

# Apply migration
docker-compose exec web flask db upgrade
```

#### Rollback a Migration

```bash
# Downgrade one migration
docker-compose exec web flask db downgrade

# Downgrade to specific revision
docker-compose exec web flask db downgrade <revision_id>
```

### Viewing Logs

```bash
# View all logs
docker-compose logs -f

# View web container logs only
docker-compose logs -f web

# View database logs
docker-compose logs -f db
```

### Accessing Container Shell

```bash
# Access web container shell
docker-compose exec web sh

# Access database shell
docker-compose exec db psql -U sdg_user -d sdg_assessment_dev
```

---

## Git Workflow

### Branch Strategy

```
main (production)
  ↑
develop (staging)
  ↑
feature/... (development branches)
```

### Creating a Feature Branch

```bash
# Ensure you're on develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Examples:
# git checkout -b feature/add-project-export
# git checkout -b fix/navigation-validation
# git checkout -b refactor/scoring-logic
```

### Committing Changes

```bash
# Check status
git status

# Add specific files (preferred)
git add app/routes/projects.py app/templates/projects/show.html

# Commit with descriptive message
git commit -m "Add project export functionality

- Add export button to project detail page
- Implement CSV export endpoint
- Add tests for export feature"
```

**Commit Message Guidelines:**

- Use imperative mood ("Add feature" not "Added feature")
- First line: brief summary (50 chars max)
- Blank line, then detailed description if needed
- Reference issues: "Fixes #123" or "Closes #456"

### Pushing and Creating Pull Request

```bash
# Push feature branch
git push origin feature/your-feature-name

# Create PR on GitHub targeting 'develop' branch
# Use PR template and ensure CI tests pass
```

### Merging Workflow

1. **Feature → Develop**: Create PR, get review, merge to `develop`
2. **Develop → Main**: After testing in staging, merge to `main` for production
3. **Hotfix**: Branch from `main`, fix, merge back to both `main` and `develop`

---

## Testing

See [TESTING.md](TESTING.md) for comprehensive testing procedures.

### Quick Test Commands

```bash
# Run all tests
docker-compose exec web pytest

# Run specific test file
docker-compose exec web pytest tests/test_auth.py

# Run with coverage
docker-compose exec web pytest --cov=app

# Run with verbose output
docker-compose exec web pytest -v
```

### Manual Testing Checklist

Before submitting a PR:

- [ ] Test all modified functionality manually
- [ ] Check browser console for JavaScript errors
- [ ] Test on both desktop and mobile viewports
- [ ] Verify no broken links or 404 errors
- [ ] Check form validation works correctly
- [ ] Test with different user roles (admin, regular user)

---

## Code Style Guidelines

### Python Code

Follow **PEP 8** style guide:

```bash
# Check code style (if flake8 installed)
docker-compose exec web flake8 app/

# Auto-format with black (if installed)
docker-compose exec web black app/
```

**Guidelines:**

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Max 100 characters
- **Imports**: Group standard library, third-party, local
- **Docstrings**: Use for all functions/classes
- **Variable names**: `snake_case` for functions/variables, `PascalCase` for classes

**Example:**

```python
from flask import Blueprint, render_template, flash
from app.models.project import Project


def calculate_project_score(project_id):
    """Calculate sustainability score for a project.

    Args:
        project_id (int): ID of the project to score

    Returns:
        dict: Score breakdown by SDG category
    """
    project = Project.query.get_or_404(project_id)
    # ... implementation
    return score_data
```

### HTML/Jinja2 Templates

- **Indentation**: 2 spaces
- **Use semantic HTML5** elements (`<header>`, `<nav>`, `<main>`, `<footer>`)
- **Extend base template**: `{% extends "base.html" %}`
- **Use blocks**: `{% block content %}...{% endblock %}`
- **Escape user input**: Use `{{ variable }}` (auto-escaped), not `{{ variable|safe }}`

### CSS

- **Use existing UIA design tokens**:
  ```css
  color: var(--uia-red);      /* #AF201C */
  color: var(--uia-dark);     /* #32373c */
  ```
- **Avoid inline styles** (use classes)
- **Mobile-first approach** (base styles for mobile, then `@media` for desktop)
- **Consistent naming**: Use BEM methodology when appropriate

### JavaScript

- **Use modern ES6+ syntax**
- **Avoid jQuery** (use vanilla JS)
- **Add event listeners** via `addEventListener`, not inline `onclick`
- **Use `const`/`let`**, not `var`
- **Comment complex logic**

---

## Common Development Tasks

### Add a New Page

1. **Create route** in appropriate blueprint (e.g., `app/routes/projects.py`)
2. **Create template** in `app/templates/<section>/`
3. **Add to navigation** if needed (edit `base.html`)
4. **Add tests** in `tests/`

### Add a New Model

1. **Create model** in `app/models/`
2. **Import in `app/__init__.py`** if needed for relationships
3. **Create migration**: `docker-compose exec web flask db migrate -m "Add NewModel"`
4. **Apply migration**: `docker-compose exec web flask db upgrade`
5. **Add tests** for CRUD operations

### Add New Dependencies

```bash
# Add to requirements.txt
echo "new-package==1.2.3" >> requirements.txt

# Rebuild containers
docker-compose up --build
```

### Debug Database

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U sdg_user -d sdg_assessment_dev

# Useful SQL commands:
\dt                          -- List tables
\d users                     -- Describe users table
SELECT * FROM users;         -- Query users
\q                          -- Quit
```

### Reset Database

```bash
# WARNING: This deletes all data!

# Stop containers
docker-compose down

# Remove database volume
docker volume rm sdg-assessment_postgres_data

# Restart (will create fresh DB)
docker-compose up
```

---

## Troubleshooting

### Port Already in Use

**Error:** `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solution:**

```bash
# Find process using port 5000
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000

# Kill the process or change port in docker-compose.yml
```

### Database Connection Errors

**Error:** `FATAL: password authentication failed`

**Solution:**

1. Check `.env` file has correct credentials
2. Restart containers: `docker-compose down && docker-compose up`
3. If persists, remove volumes and restart

### Code Changes Not Reflected

**Solution:**

1. **Python**: Check Gunicorn logs for reload errors: `docker-compose logs -f web`
2. **Templates**: Clear browser cache (Ctrl+F5)
3. **Static files**: Do hard refresh (Ctrl+Shift+R)
4. **Last resort**: Rebuild containers: `docker-compose up --build`

### Migration Errors

**Error:** `Target database is not up to date`

**Solution:**

```bash
# Check current migration
docker-compose exec web flask db current

# Upgrade to latest
docker-compose exec web flask db upgrade

# If broken, reset migrations (WARNING: destroys data)
docker-compose down -v
docker-compose up
```

---

## VS Code Configuration (Optional)

Create `.vscode/settings.json` for IDE integration:

```json
{
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

Install recommended extensions:

- Python (Microsoft)
- Pylance
- Docker
- GitLens
- Jinja (wholroyd)

---

## Contributing

### Pull Request Process

1. **Create feature branch** from `develop`
2. **Make changes** following code style guidelines
3. **Add tests** for new functionality
4. **Run tests locally**: `docker-compose exec web pytest`
5. **Commit with clear messages**
6. **Push and create PR** to `develop` branch
7. **Wait for review** and address feedback
8. **Squash and merge** after approval

### Code Review Checklist

Reviewers should verify:

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] No console errors or warnings
- [ ] Database migrations included if models changed
- [ ] Documentation updated if needed
- [ ] No sensitive data (passwords, API keys) committed

---

## Getting Help

- **Documentation**: Check README.md, DEPLOYMENT.md, TESTING.md
- **Issues**: Search [GitHub Issues](https://github.com/YOUR_ORG/sdg-assessment/issues)
- **Discussions**: Use GitHub Discussions for questions
- **Team**: Contact the development team on Slack/email

---

**Last Updated**: 2026-02-20
**Version**: 1.0
