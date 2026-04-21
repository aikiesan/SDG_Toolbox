# Deployment Guide

**Version:** 1.0.0  
**Last Updated:** 2025-04-25

This guide explains how to deploy the SDG Assessment Toolkit in development, staging, or production environments.

## Prerequisites
- Python 3.9 or higher
- Git
- All dependencies listed in `requirements.txt`
- Database server (SQLite for development, production DB for deployment)
- Mail server for notifications (optional)

## Deployment Steps

1. **Clone the repository and set up environment**
    ```bash
    git clone https://github.com/aikiesan/sdg-assessment.git
    cd sdg-assessment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
2. **Configure environment variables**
    - Set variables as described in [ENVIRONMENT.md](./ENVIRONMENT.md).
    - Example:
      ```env
      FLASK_CONFIG=development
      SECRET_KEY=your_secret_key
      DATABASE_URL=sqlite:///sdg_assessment.db
      ```
3. **Initialize the database**
    ```bash
    python create_db.py
    python create_tables.py
    python seed_sdg_questions.py
    ```
    - Or use migration scripts if upgrading.
4. **Run the application**
    ```bash
    python run.py
    ```
    - The app will be available at http://localhost:5001
5. **Production Considerations**
    - Use a production-ready WSGI server (e.g., Gunicorn or uWSGI)
    - Set `FLASK_CONFIG=production`
    - Use a strong `SECRET_KEY`
    - Set up HTTPS
    - Configure proper backups and monitoring
6. **Database Migrations**
    - Use `flask db migrate` and `flask db upgrade` for schema changes.

## Server Requirements
- Python 3.9+
- Sufficient RAM and CPU for expected load
- Persistent storage for the database

## Troubleshooting
- **App won't start:** Check logs for errors and verify all environment variables are set correctly.
- **Database errors:** Ensure the database server is running and all migration scripts have been applied.
- **Cannot send email:** Verify mail server settings in your environment variables.
- **Port already in use:** Make sure no other process is using port 5001 or change the port in your run command.
- **Other issues:** Review the [README](../README.md) and [ENVIRONMENT.md](./ENVIRONMENT.md) for additional setup details.

For further deployment support, contact Lucas Nakamura at [lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com).

---
**Maintained by Lucas Nakamura**
