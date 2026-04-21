# UIA IT Department Handoff — SDG Assessment Toolkit
**To:** Patrick, IT Department of UIA  
**From:** Development Team  
**Project Repository:** [https://github.com/aikiesan/SDG_Toolbox](https://github.com/aikiesan/SDG_Toolbox)  
**Date:** April 21, 2026

---

## 1. Overview
The SDG Assessment Toolkit is a Flask-based web application designed for the International Union of Architects (UIA). This document provides everything needed to deploy the application on a Virtual Machine using Docker, Nginx, and UIA's official SSL certificates.

## 2. Infrastructure Requirements
- **Host OS:** Linux (Ubuntu 22.04+ recommended)
- **Software:** Docker Engine, Docker Compose (v2.0+)
- **Network:** Ports 80 and 443 open for public traffic.

## 3. Preparation & Configuration

### Step A: Clone the Repository
```bash
git clone https://github.com/aikiesan/SDG_Toolbox.git
cd SDG_Toolbox
```

### Step B: Environment Variables
Create a file named `.env.production` in the root directory. You MUST populate this with your production secrets:
```env
# Database Settings
POSTGRES_USER=uia_admin
POSTGRES_PASSWORD=generate_a_strong_password
POSTGRES_DB=sdg_assessment

# Flask Settings
SECRET_KEY=generate_a_very_long_random_string_here
FLASK_ENV=production

# Mail Server Settings (UIA Official SMTP)
MAIL_SERVER=smtp.your-server.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=notifications@uia-architectes.org
MAIL_PASSWORD=your_smtp_password
```

### Step C: SSL Certificate Setup
1. Create a `certs/` directory in the project root: `mkdir certs`
2. Place your official UIA SSL files inside this folder:
   - `uia_certificate.crt` (The public certificate/chain)
   - `uia_private.key` (The private key)
3. Ensure the filenames match those referenced in `nginx.conf` (or rename them accordingly).

## 4. Deployment Execution

### Step D: Build and Run Containers
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```
This command will build the Python image, pull the Postgres and Nginx images, and start the services in the background.

### Step E: Database Initialization (First Run Only)
Once the containers are running, you must initialize the database schema and seed the standard SDG data. Execute these commands:

```bash
# 1. Apply database migrations
docker-compose -f docker-compose.prod.yml exec web flask db upgrade

# 2. Seed the database with SDG questions and standard data
docker-compose -f docker-compose.prod.yml exec web python seed_sdg_questions.py
docker-compose -f docker-compose.prod.yml exec web python populate_strength_values.py
```

## 5. Enabling HTTPS (Nginx)
The provided `nginx.conf` has the HTTPS block commented out by default to allow for initial testing on port 80. To enable HTTPS:
1. Open `nginx.conf`.
2. Uncomment the entire `server { listen 443 ssl ... }` block.
3. Update `server_name` to your production domain (e.g., `sdg.uia-architectes.org`).
4. (Optional) Uncomment the redirect block in the port 80 server to force HTTPS.
5. Reload Nginx: `docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload`

## 6. Maintenance & Operations
- **View Logs:** `docker-compose -f docker-compose.prod.yml logs -f web` (or `nginx`/`db`)
- **Restart Services:** `docker-compose -f docker-compose.prod.yml restart`
- **Backup Database:**
  ```bash
  docker-compose -f docker-compose.prod.yml exec db pg_dump -U uia_admin sdg_assessment > backup_$(date +%Y%m%d).sql
  ```

---
**Contact Information:**
For technical support regarding the application logic, contact Lucas Nakamura at [lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com).
