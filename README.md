# SDG Assessment Toolkit

**Version:** 1.0.0
**Last Updated:** 2025-12-01
**Maintained by:** Lucas Nakamura ([lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com))

A comprehensive web-based toolkit for architects, urban planners, and sustainability professionals to evaluate how their projects align with the United Nations Sustainable Development Goals (SDGs). The system provides both guided questionnaire-based assessments and expert-level direct assessment capabilities.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Target Users](#target-users)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Integration Guide](#integration-guide)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## 🌍 Overview

The SDG Assessment Toolkit is a Flask-based web application that enables professionals to:
- Assess architectural and urban planning projects against all 17 UN SDGs
- Generate detailed, data-driven reports with visualizations
- Track multiple projects and assessments over time
- Export results for presentations and further analysis
- Integrate SDG assessment capabilities into existing workflows via API

### Target Users

- **Architects** - Evaluate sustainability of building designs
- **Urban Planners** - Assess city development projects against SDGs
- **Sustainability Consultants** - Provide SDG compliance reports to clients
- **Government Agencies** - Ensure public projects meet SDG targets
- **Research Institutions** - Analyze SDG alignment across multiple projects
- **UIA (Union Internationale des Architectes)** - Integrate SDG assessment into member services

---

## ✨ Key Features

### 1. **5-Step Assessment Process**

#### Step 1: Project Information
- Capture project details (name, description, location, type)
- Record project specifications (size, budget, sector, timeline)
- Support for various project types: Residential, Commercial, Education, Healthcare, etc.

#### Step 2: SDG Questionnaire
- Comprehensive questionnaire covering all 17 SDGs
- Multiple-choice and text-based responses
- Context-aware questions based on project type
- Draft saving and progress tracking

#### Step 3: Scoring & Analysis
- Automatic scoring based on questionnaire responses
- Direct scores for primary SDG alignment
- Bonus scores for synergistic relationships between SDGs
- Total score calculation (capped at 100%)
- Raw score tracking for detailed analysis

#### Step 4: Results Visualization
- Interactive charts using Chart.js
- SDG-specific color-coded visualizations
- Radar charts showing alignment across all 17 SDGs
- Bar charts for comparative analysis
- Export capabilities (CSV, PNG, PDF)

#### Step 5: Recommendations & Actions
- AI-powered suggestions for improving SDG alignment
- Prioritized action items
- Resource links to SDG documentation
- Best practices from similar projects

### 2. **Expert Assessment Mode**
- Direct input of SDG scores by qualified experts
- Text-based assessment with notes
- Bypass questionnaire for experienced assessors
- Maintain audit trail of expert assessments

### 3. **User Management**
- Secure user registration and authentication
- Email confirmation workflow
- Password reset functionality
- User profiles and preferences
- Multi-user support with data isolation

### 4. **Project Management**
- Create and manage multiple projects
- Track assessment history per project
- Project comparison across SDGs
- Bulk project operations
- Project archival and deletion (GDPR-compliant)

### 5. **Dashboard & Analytics**
- Personal dashboard with key metrics
- Project comparison views
- SDG trend analysis
- Assessment completion tracking
- Visual summaries and reports

### 6. **API Access**
- RESTful API for external integrations
- JWT-based authentication
- CRUD operations for projects and assessments
- Webhook support for real-time updates
- Comprehensive API documentation via Swagger

### 7. **Data Export & Reporting**
- Export assessments as CSV
- Generate PDF reports
- Download charts as images (PNG, SVG)
- Bulk export capabilities
- Custom report templates

### 8. **Security & Privacy**
- CSRF protection
- XSS prevention via input sanitization (bleach)
- SQL injection protection (ORM-based queries)
- Secure password hashing (Werkzeug)
- HTTPS support
- GDPR-compliant data handling

---

## 🛠️ Technology Stack

### Backend
- **Python 3.9+** - Core programming language
- **Flask 2.3.3** - Web framework
- **SQLAlchemy 2.0.30** - ORM for database operations
- **Flask-Login** - User session management
- **Flask-Mail** - Email notifications
- **Flask-WTF** - Form handling and CSRF protection
- **PyJWT** - API authentication via JSON Web Tokens
- **Gunicorn** - Production WSGI server

### Database
- **SQLite** - Development database (file-based, no server needed)
- **PostgreSQL** - Recommended production database (scalable, robust)
- **MySQL/MariaDB** - Alternative production option
- **SQL Server** - Enterprise option
- **Alembic** - Database migrations

### Frontend
- **Jinja2** - Server-side templating
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Data visualization
- **JavaScript (ES6+)** - Client-side interactivity
- **jQuery** - DOM manipulation and AJAX

### Security
- **Werkzeug** - Password hashing (PBKDF2)
- **bleach** - HTML sanitization
- **itsdangerous** - Cryptographic signing
- **Flask-WTF** - CSRF protection
- **email-validator** - Email validation

### Testing
- **pytest** - Testing framework
- **pytest-flask** - Flask-specific test utilities
- **pytest-cov** - Code coverage reporting
- **BeautifulSoup4** - HTML parsing in tests

### Deployment & DevOps
- **Gunicorn** - WSGI application server
- **Nginx** - Reverse proxy and static file serving (recommended)
- **systemd** - Service management (Linux)
- **Docker** - Containerization (optional)
- **Git** - Version control

### API Documentation
- **Flasgger** - Automatic Swagger UI generation
- **OpenAPI 3.0** - API specification standard

---

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web Browser │  │  Mobile App  │  │  API Client  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │ HTTPS            │ HTTPS            │ HTTPS + JWT
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────┐
│                    WEB SERVER (Nginx)                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Static Files  │  Reverse Proxy  │  SSL/TLS        │     │
│  └────────────────────────────────────────────────────┘     │
└─────────┬────────────────────────────────────────────────────┘
          │
          │ HTTP (Internal)
          │
┌─────────▼────────────────────────────────────────────────────┐
│              APPLICATION SERVER (Gunicorn + Flask)            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                     FLASK APP                         │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │   Routes   │  │  Services  │  │   Models   │     │   │
│  │  │            │  │            │  │            │     │   │
│  │  │ • Auth     │  │ • Scoring  │  │ • User     │     │   │
│  │  │ • Projects │  │ • Email    │  │ • Project  │     │   │
│  │  │ • Assess.  │  │ • Project  │  │ • Assess.  │     │   │
│  │  │ • API      │  │ • Assess.  │  │ • SDG      │     │   │
│  │  │ • Dashboard│  │            │  │ • Response │     │   │
│  │  └────┬───────┘  └─────┬──────┘  └─────┬──────┘     │   │
│  │       │                │               │            │   │
│  │       └────────────────┼───────────────┘            │   │
│  └────────────────────────┼──────────────────────────────┘   │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐   │
│  │            ORM Layer (SQLAlchemy)                     │   │
│  └────────────────────────┬──────────────────────────────┘   │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            │ SQL Queries
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                   DATABASE LAYER                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  SQLite (Dev) / PostgreSQL (Prod) / MySQL / MSSQL    │    │
│  │                                                       │    │
│  │  Tables:                                              │    │
│  │  • users          • assessments    • sdg_scores      │    │
│  │  • projects       • sdg_goals      • sdg_relationships│   │
│  │  • question_responses              • sdg_questions   │    │
│  └──────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  SMTP Server │  │  File Storage│  │  CDN (opt.)  │        │
│  │  (Email)     │  │  (S3, etc.)  │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

### Data Flow Example: Creating an Assessment
1. User authenticates via `/auth/login` → Session created
2. User creates project via `/projects/new` → Project stored in DB
3. User starts assessment → Redirected to `/questionnaire/<assessment_id>`
4. User answers questions → Responses saved via AJAX to `/api/save-progress`
5. User submits assessment → Scoring service calculates SDG scores
6. Results displayed → Charts rendered with Chart.js
7. User exports data → CSV/PDF generated server-side

---

## 📦 Installation Guide

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git
- Virtual environment tool (venv, virtualenv, or conda)
- (Optional) PostgreSQL for production deployment

### Development Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/aikiesan/sdg-assessment.git
cd sdg-assessment
```

#### 2. Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
cp .env.example .env  # If example exists, otherwise create manually
```

Edit `.env` with your configuration (see [Configuration](#configuration) section).

#### 5. Initialize Database
```bash
# Create database and tables
python create_db.py

# Seed SDG data
python seed_sdg_questions.py

# (Optional) Populate SDG relationships
python scripts/populate_relationships.py
```

#### 6. Run Development Server
```bash
python run.py
```

Visit `http://localhost:5001` in your browser.

### Production Installation

#### 1. Follow Steps 1-5 Above

#### 2. Set Production Environment Variables
```bash
export FLASK_CONFIG=production
export SECRET_KEY='your-secure-random-key-here'
export DATABASE_URL='postgresql://user:pass@localhost/sdg_assessment'
```

#### 3. Use Production Database
```bash
# PostgreSQL example
createdb sdg_assessment
flask db upgrade
python seed_sdg_questions.py
```

#### 4. Run with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

#### 5. Set Up Nginx (Recommended)
See [Deployment](#deployment) section for Nginx configuration.

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Flask Configuration
FLASK_CONFIG=development          # Options: development, testing, production
SECRET_KEY=your-secret-key-here   # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
DEBUG=True                        # Set to False in production

# Database Configuration
DATABASE_URL=sqlite:///instance/sdgassessmentdev.db  # Development
# DATABASE_URL=postgresql://user:password@localhost/sdg_assessment  # Production

# Mail Server Configuration (for email notifications)
MAIL_SERVER=smtp.googlemail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
ADMIN_EMAIL=lucassnakamura@gmail.com

# Application Settings
APP_NAME=SDG Assessment Toolkit
APP_URL=http://localhost:5001     # Update to your domain in production

# Security Settings
SESSION_COOKIE_SECURE=False       # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# API Settings
API_RATE_LIMIT=100                # Requests per hour per user
```

### Configuration Classes

The application uses different configuration classes defined in `config.py`:

- **DevelopmentConfig** - Debug enabled, SQLite database
- **TestingConfig** - In-memory SQLite, email suppressed
- **ProductionConfig** - Debug disabled, production database

Set via `FLASK_CONFIG` environment variable.

---

## 🗄️ Database Setup

### SQLite (Development)
No additional setup required. Database file is created automatically at:
```
instance/sdgassessmentdev.db
```

### PostgreSQL (Production Recommended)

#### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

#### Create Database
```bash
sudo -u postgres psql
CREATE DATABASE sdg_assessment;
CREATE USER sdg_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE sdg_assessment TO sdg_user;
\q
```

#### Update Environment Variable
```bash
export DATABASE_URL='postgresql://sdg_user:secure_password@localhost/sdg_assessment'
```

#### Run Migrations
```bash
flask db upgrade
python seed_sdg_questions.py
```

### MySQL (Alternative)

#### Create Database
```sql
CREATE DATABASE sdg_assessment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sdg_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON sdg_assessment.* TO 'sdg_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Install MySQL Driver
```bash
pip install mysqlclient  # or PyMySQL
```

#### Update Environment Variable
```bash
export DATABASE_URL='mysql://sdg_user:secure_password@localhost/sdg_assessment'
```

### Database Migrations

```bash
# Initialize migrations (first time only)
flask db init

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade
```

For detailed database schema information, see [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md).

---

## 🚀 Running the Application

### Method 1: Flask Development Server
```bash
python run.py
# Access at: http://localhost:5001
```

### Method 2: Flask CLI
```bash
export FLASK_APP=run.py
flask run --host=0.0.0.0 --port=5001
```

### Method 3: Gunicorn (Production)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 run:app

# With worker class for better concurrency:
gunicorn -w 4 -k gevent -b 0.0.0.0:8000 run:app
```

### Stopping the Application
```bash
# Development server: Ctrl+C

# Gunicorn:
pkill gunicorn
# or
ps aux | grep gunicorn  # Find PID
kill <PID>
```

---

## 📁 Project Structure

```
sdg-assessment/
│
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory, extensions initialization
│   ├── cli.py                   # Custom CLI commands
│   ├── scoring_logic.py         # Core SDG scoring algorithms
│   │
│   ├── models/                  # Database models (SQLAlchemy ORM)
│   │   ├── __init__.py
│   │   ├── user.py              # User model with authentication
│   │   ├── project.py           # Project model
│   │   ├── assessment.py        # Assessment & SdgScore models
│   │   ├── sdg.py               # SdgGoal, SdgQuestion models
│   │   ├── response.py          # QuestionResponse model
│   │   └── sdg_relationship.py  # SDG synergy relationships
│   │
│   ├── routes/                  # Request handlers (blueprints)
│   │   ├── __init__.py
│   │   ├── main.py              # Homepage, about, contact routes
│   │   ├── auth.py              # Registration, login, logout
│   │   ├── projects.py          # Project CRUD operations
│   │   ├── assessments.py       # Assessment workflows
│   │   ├── questionnaire.py     # Questionnaire step handling
│   │   ├── api.py               # RESTful API endpoints
│   │   └── dashboard.py         # User dashboard and analytics
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── project_service.py   # Project operations
│   │   ├── assessment_service.py # Assessment workflows
│   │   ├── scoring_service.py   # SDG score calculations
│   │   └── email_utils.py       # Email sending utilities
│   │
│   ├── utils/                   # Helper functions and utilities
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication helpers
│   │   ├── db.py                # Database utilities
│   │   ├── email_utils.py       # Email templates and sending
│   │   ├── errors.py            # Error handlers (404, 500)
│   │   ├── filters.py           # Jinja2 template filters
│   │   ├── validation.py        # Input validation
│   │   └── sdg_data.py          # SDG constants and data
│   │
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Base template with navigation
│   │   ├── index.html           # Homepage
│   │   ├── auth/                # Authentication templates
│   │   ├── projects/            # Project templates
│   │   ├── assessments/         # Assessment templates
│   │   ├── questionnaire/       # Questionnaire templates
│   │   └── dashboard/           # Dashboard templates
│   │
│   └── static/                  # Static assets
│       ├── css/                 # Stylesheets
│       ├── js/                  # JavaScript files
│       ├── images/              # Images and icons
│       └── sdg_icons/           # SDG goal icons
│
├── migrations/                  # Database migration scripts (Alembic)
│   ├── versions/                # Individual migration files
│   └── env.py                   # Migration environment config
│
├── tests/                       # Test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── test_auth.py             # Authentication tests
│   ├── test_projects.py         # Project tests
│   ├── test_assessments.py      # Assessment tests
│   ├── test_api.py              # API tests
│   └── test_models.py           # Model tests
│
├── scripts/                     # Utility scripts
│   ├── populate_relationships.py # Populate SDG relationships
│   ├── create_test_user.py      # Create test users
│   └── check_test_data.py       # Verify test data
│
├── documentation/               # Additional documentation
│   ├── README.md                # Documentation index
│   ├── DATA_MODEL.md            # Database schema overview
│   ├── ARCHITECTURE.md          # System architecture
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── ENVIRONMENT.md           # Environment variables
│   ├── INTEGRATION_GUIDE.md     # Integration options
│   ├── USER_GUIDE.md            # End-user guide
│   ├── CONTRIBUTING.md          # Contribution guidelines
│   ├── SECURITY.md              # Security policy
│   └── ROADMAP.md               # Future plans
│
├── instance/                    # Instance-specific files (not in git)
│   └── sdgassessmentdev.db      # SQLite database (development)
│
├── .env                         # Environment variables (not in git)
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── config.py                    # Flask configuration classes
├── run.py                       # Application entry point
├── create_db.py                 # Database initialization script
├── seed_sdg_questions.py        # Seed SDG questions
├── schema.sql                   # SQL schema reference
├── pytest.ini                   # Pytest configuration
├── README.md                    # This file
└── LICENSE                      # License information
```

---

## 🔌 API Documentation

The application provides a RESTful API for external integrations. API documentation is available at:
```
http://localhost:5001/apidocs  # Swagger UI (if Flasgger enabled)
```

### Authentication

All API endpoints (except login) require JWT authentication.

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1
}
```

#### Using the Token
```http
GET /api/projects
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Core Endpoints

#### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List all user's projects |
| POST | `/api/projects` | Create a new project |
| GET | `/api/projects/<id>` | Get project details |
| PUT | `/api/projects/<id>` | Update project |
| DELETE | `/api/projects/<id>` | Delete project |

#### Assessments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/<id>/assessments` | Create assessment for project |
| GET | `/api/assessments/<id>` | Get assessment details |
| PUT | `/api/assessments/<id>` | Update assessment |
| DELETE | `/api/assessments/<id>` | Delete assessment |
| POST | `/api/assessments/<id>/finalize` | Finalize and score assessment |
| GET | `/api/assessments/<id>/summary` | Get assessment results |

#### SDG Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sdg/goals` | List all 17 SDG goals |
| GET | `/api/sdg/relationships` | Get SDG synergy relationships |

#### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | Get user dashboard metrics |

### Example API Usage

#### Create a Project
```bash
curl -X POST http://localhost:5001/api/projects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Building Project",
    "description": "Sustainable office complex",
    "project_type": "Commercial",
    "location": "São Paulo, Brazil",
    "size_sqm": 5000,
    "sector": "Commercial",
    "budget": 2000000,
    "start_date": "2025-01-01",
    "end_date": "2026-12-31"
  }'
```

#### Get Assessment Results
```bash
curl -X GET http://localhost:5001/api/assessments/123/summary \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

For complete API documentation, see [documentation/INTEGRATION_GUIDE.md](./documentation/INTEGRATION_GUIDE.md).

---

## 🔗 Integration Guide

### Option 1: Iframe Embedding

Embed the assessment tool in your existing website:

```html
<iframe
  src="https://your-sdg-toolkit.com/assessments/new?token=YOUR_TOKEN"
  width="100%"
  height="800px"
  frameborder="0">
</iframe>
```

### Option 2: RESTful API

Integrate via API calls (see [API Documentation](#api-documentation)).

### Option 3: Single Sign-On (SSO)

The toolkit supports SSO integration:
1. Configure OAuth2 provider in `config.py`
2. Implement custom authentication provider in `app/utils/auth.py`
3. Map external user IDs to local user accounts

For detailed integration instructions, see [documentation/INTEGRATION_GUIDE.md](./documentation/INTEGRATION_GUIDE.md).

---

## 🌐 Deployment

### Production Checklist

- [ ] Set `FLASK_CONFIG=production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Use PostgreSQL/MySQL instead of SQLite
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure firewall rules
- [ ] Enable database backups
- [ ] Set up monitoring and logging
- [ ] Configure email server
- [ ] Review security settings
- [ ] Run security audit
- [ ] Set up rate limiting
- [ ] Configure CORS if needed
- [ ] Optimize static file serving
- [ ] Set up CDN for assets (optional)

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name sdg-assessment.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sdg-assessment.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static {
        alias /path/to/sdg-assessment/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### Systemd Service (Linux)

Create `/etc/systemd/system/sdg-assessment.service`:

```ini
[Unit]
Description=SDG Assessment Toolkit
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/sdg-assessment
Environment="PATH=/path/to/sdg-assessment/venv/bin"
Environment="FLASK_CONFIG=production"
EnvironmentFile=/path/to/sdg-assessment/.env
ExecStart=/path/to/sdg-assessment/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable sdg-assessment
sudo systemctl start sdg-assessment
sudo systemctl status sdg-assessment
```

For detailed deployment instructions, see [documentation/DEPLOYMENT.md](./documentation/DEPLOYMENT.md).

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
# View coverage report: open htmlcov/index.html
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
```

### Run Specific Test
```bash
pytest tests/test_auth.py::test_register_user
```

### Run Tests in Verbose Mode
```bash
pytest -v
```

### Test Structure
- `tests/conftest.py` - Fixtures (test client, database, users)
- `tests/test_auth.py` - Authentication tests
- `tests/test_projects.py` - Project CRUD tests
- `tests/test_assessments.py` - Assessment workflow tests
- `tests/test_api.py` - API endpoint tests
- `tests/test_models.py` - Database model tests

---

## 🤝 Contributing

Contributions are welcome! Please see [documentation/CONTRIBUTING.md](./documentation/CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

### Code Standards
- Follow PEP 8 style guide
- Write docstrings for all functions
- Add tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

---

## 📞 Support

### Documentation
- [User Guide](./documentation/USER_GUIDE.md)
- [API Documentation](./documentation/INTEGRATION_GUIDE.md)
- [Database Schema](./DATABASE_SCHEMA.md)
- [Deployment Guide](./documentation/DEPLOYMENT.md)
- [FAQ](./documentation/FAQ.md)

### Contact
- **Email:** [lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com)
- **GitHub Issues:** [https://github.com/aikiesan/sdg-assessment/issues](https://github.com/aikiesan/sdg-assessment/issues)

### Reporting Bugs
Please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs

### Feature Requests
Open an issue on GitHub with the "enhancement" label.

---

## 🙏 Acknowledgments

- United Nations for the Sustainable Development Goals framework
- Flask and SQLAlchemy communities
- Chart.js for visualization capabilities
- All contributors to this project

---

**Made with ❤️ for a sustainable future**
"# UIA_SDG_Toolbox" 
