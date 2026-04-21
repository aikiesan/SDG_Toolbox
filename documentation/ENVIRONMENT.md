# Environment Configuration

**Version:** 1.0.0  
**Last Updated:** 2025-04-25

This file describes the environment variables and configuration required for running the SDG Assessment Toolkit in different environments (development, testing, production).

## Prerequisites
- Python 3.9 or higher
- Access to environment variable configuration (e.g., .env file or system environment)

## Required Environment Variables

| Variable Name      | Description                                 | Required |
|--------------------|---------------------------------------------|----------|
| FLASK_CONFIG       | Flask config profile (dev/test/prod)         | Yes      |
| SECRET_KEY         | Flask secret key for sessions                | Yes      |
| DATABASE_URL       | Database connection string                   | Yes      |
| MAIL_SERVER        | SMTP server for outgoing email               | Yes      |
| MAIL_PORT          | SMTP port                                    | Yes      |
| MAIL_USERNAME      | Email username                               | Yes      |
| MAIL_PASSWORD      | Email password                               | Yes      |
| MAIL_USE_TLS       | Enable TLS (true/false)                      | Yes      |

## Configuration Profiles

- **Development:**
  - Use SQLite and enable debug mode
  - Set `FLASK_CONFIG=development`
- **Testing:**
  - Use a separate test database, enable testing mode
  - Set `FLASK_CONFIG=testing`
- **Production:**
  - Use a production-ready database and strong secret keys
  - Set `FLASK_CONFIG=production`

See `config.py` for more details on configuration options.

## Troubleshooting
- **App fails to start:** Check that all required environment variables are set and spelled correctly
- **Database connection errors:** Verify your `DATABASE_URL` and ensure the database server is running
- **Email not sending:** Double-check your mail server settings and credentials
- **Configuration changes not taking effect:** Restart the application after updating environment variables

For environment/configuration support, contact Lucas Nakamura at [lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com).

---
**Maintained by Lucas Nakamura**
