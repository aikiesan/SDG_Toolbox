# SDG Assessment Tool - Production Deployment Guide

This guide covers deploying the SDG Assessment Tool to a production VPS environment.

## Table of Contents

1. [VPS Requirements](#vps-requirements)
2. [Initial VPS Setup](#initial-vps-setup)
3. [Application Deployment](#application-deployment)
4. [SSL/HTTPS Configuration](#sslhttps-configuration)
5. [Backup Strategy](#backup-strategy)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Updating the Application](#updating-the-application)
8. [Troubleshooting](#troubleshooting)

---

## VPS Requirements

### Recommended: OVHcloud VPS-1

| Specification | VPS-1 | Capacity |
|---------------|-------|----------|
| vCPU | 2 | Optimal for 2 Gunicorn workers |
| RAM | 4GB | 100-500 users |
| Storage | 80GB SSD | Sufficient for DB + backups |
| Bandwidth | 100 Mbps | Adequate for expected traffic |
| **Price/year** | **€35-45** | 70% cheaper than VPS-3 |

**Upgrade Path**: If traffic grows to 500-1500 users, upgrade to VPS-2 (8GB RAM).

### Architecture

```
┌────────────────────────────────┐
│  VPS-1 (2 vCPU, 4GB RAM)      │
│                                │
│  ┌──────────────────────────┐ │
│  │   Docker Compose         │ │
│  │                          │ │
│  │  ┌────────────────────┐ │ │
│  │  │ Nginx (50MB)       │ │ │ ← Reverse proxy
│  │  └─────────┬──────────┘ │ │
│  │            ↓            │ │
│  │  ┌────────────────────┐ │ │
│  │  │ Gunicorn (800MB)   │ │ │ ← Flask app
│  │  └─────────┬──────────┘ │ │
│  │            ↓            │ │
│  │  ┌────────────────────┐ │ │
│  │  │ PostgreSQL (800MB) │ │ │ ← Database
│  │  └────────────────────┘ │ │
│  └──────────────────────────┘ │
│                                │
│  Total: ~2.65GB / 4GB (66%)   │
└────────────────────────────────┘
```

---

## Initial VPS Setup

### 1. Connect to VPS

```bash
# SSH into your VPS as root
ssh root@your-vps-ip
```

### 2. Install Docker & Docker Compose

```bash
# Install Docker using official script
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt update
apt install docker-compose -y

# Verify installations
docker --version
docker-compose --version
```

### 3. Configure Firewall

```bash
# Install UFW (Uncomplicated Firewall)
apt install ufw -y

# Allow SSH (CRITICAL - do this first!)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

**Output should show:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

### 4. Create Application Directory

```bash
# Create directory for the application
mkdir -p /opt/sdg-assessment
cd /opt/sdg-assessment
```

### 5. Setup Git (Optional but Recommended)

```bash
# Install git
apt install git -y

# Clone repository
git clone https://github.com/YOUR_ORG/sdg-assessment.git .

# Or upload files manually via SCP/SFTP
```

---

## Application Deployment

### 1. Create Production Environment File

```bash
cd /opt/sdg-assessment

# Copy template
cp .env.production.template .env

# Generate strong SECRET_KEY
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

**Copy the output** and edit `.env`:

```bash
nano .env
```

**Configure the following critical settings:**

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<paste-generated-secret-key-here>

# Database Configuration
POSTGRES_USER=sdg_user
POSTGRES_PASSWORD=<create-strong-password>
POSTGRES_DB=sdg_assessment

# Email Configuration (adjust for your provider)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password

# Application Settings
APP_URL=http://your-vps-ip  # Update with domain after DNS setup
ADMIN_EMAIL=admin@yourdomain.com
```

**Save and exit** (Ctrl+X, Y, Enter in nano)

### 2. Build and Start Application

```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Start services in detached mode
docker-compose -f docker-compose.prod.yml up -d

# Check logs to verify startup
docker-compose -f docker-compose.prod.yml logs -f web
```

**Expected output:**
```
web_1   | ====================
web_1   | Starting SDG Assessment Application
web_1   | Environment: production
web_1   | ====================
web_1   | Database is up!
web_1   | Migrations complete!
web_1   | Starting Gunicorn server...
web_1   | [2026-02-20 10:00:00 +0000] [1] [INFO] Starting gunicorn 21.2.0
web_1   | [2026-02-20 10:00:00 +0000] [1] [INFO] Listening at: http://0.0.0.0:5000 (1)
web_1   | [2026-02-20 10:00:00 +0000] [1] [INFO] Using worker: sync
web_1   | [2026-02-20 10:00:00 +0000] [7] [INFO] Booting worker with pid: 7
web_1   | [2026-02-20 10:00:00 +0000] [8] [INFO] Booting worker with pid: 8
```

Press **Ctrl+C** to exit log view (containers keep running).

### 3. Verify Deployment

```bash
# Check running containers
docker-compose -f docker-compose.prod.yml ps

# Test HTTP access
curl http://localhost

# Test from external machine
curl http://your-vps-ip
```

**Expected:** HTML content from the landing page.

---

## SSL/HTTPS Configuration

### 1. Configure DNS

**Before proceeding**, ensure your domain points to your VPS IP:

```bash
# Test DNS resolution
nslookup yourdomain.com
# Should return your VPS IP
```

### 2. Install Certbot

```bash
# Install Certbot for Let's Encrypt
apt install certbot -y
```

### 3. Stop Nginx Temporarily

```bash
cd /opt/sdg-assessment
docker-compose -f docker-compose.prod.yml stop nginx
```

### 4. Obtain SSL Certificate

```bash
# Request certificate (replace yourdomain.com)
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to Terms of Service
# - Choose whether to share email with EFF
```

**Expected output:**
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/yourdomain.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 5. Update Nginx Configuration

```bash
nano nginx.conf
```

**Uncomment the HTTPS server block** (lines 77-122) and update `server_name`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;  # ← Update this

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    # ... rest of config
}
```

**Also uncomment HTTP → HTTPS redirect** (lines 40-42):

```nginx
location / {
    return 301 https://$host$request_uri;
}
```

**And comment out the HTTP proxy block** (lines 45-60).

**Save and exit.**

### 6. Update Docker Compose for SSL

```bash
nano docker-compose.prod.yml
```

**Update nginx volumes** to include SSL certificates:

```yaml
nginx:
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
    - ./app/static:/static:ro
    - /etc/letsencrypt:/etc/letsencrypt:ro  # Add this line
```

**Save and exit.**

### 7. Restart Services

```bash
# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Verify HTTPS works
curl https://yourdomain.com
```

### 8. Setup Auto-Renewal

```bash
# Test renewal (dry run)
certbot renew --dry-run

# Add to crontab for automatic renewal
crontab -e
```

**Add this line** (renews daily at 2 AM):

```bash
0 2 * * * /usr/bin/certbot renew --quiet && docker-compose -f /opt/sdg-assessment/docker-compose.prod.yml restart nginx
```

**Save and exit.**

---

## Backup Strategy

### 1. Create Backup Script

```bash
nano /opt/sdg-assessment/backup.sh
```

**Paste the following:**

```bash
#!/bin/bash
set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
APP_DIR="/opt/sdg-assessment"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting backup at $DATE"

# Backup database
echo "Backing up database..."
docker-compose -f $APP_DIR/docker-compose.prod.yml exec -T db \
  pg_dump -U sdg_user sdg_assessment > $BACKUP_DIR/db_$DATE.sql

# Compress backup
echo "Compressing backup..."
gzip $BACKUP_DIR/db_$DATE.sql

# Keep only last 7 days of backups
echo "Cleaning old backups..."
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
```

**Save, exit, and make executable:**

```bash
chmod +x /opt/sdg-assessment/backup.sh
```

### 2. Test Backup

```bash
/opt/sdg-assessment/backup.sh
```

**Check backup exists:**

```bash
ls -lh /opt/backups/
```

### 3. Schedule Daily Backups

```bash
crontab -e
```

**Add this line** (runs daily at 2 AM):

```bash
0 2 * * * /opt/sdg-assessment/backup.sh >> /var/log/sdg-backup.log 2>&1
```

**Save and exit.**

### 4. Restore from Backup (if needed)

```bash
# Stop application
cd /opt/sdg-assessment
docker-compose -f docker-compose.prod.yml down

# Restore database
gunzip < /opt/backups/db_20260220_020000.sql.gz | \
  docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U sdg_user -d sdg_assessment

# Restart application
docker-compose -f docker-compose.prod.yml up -d
```

---

## Monitoring & Maintenance

### Check Application Status

```bash
cd /opt/sdg-assessment

# View running containers
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# View resource usage
docker stats
```

### Monitor Disk Space

```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df
```

### Clean Up Docker

```bash
# Remove unused images/containers
docker system prune -a

# Remove old volumes (CAUTION: only if you have backups!)
docker volume prune
```

### Check Application Health

```bash
# HTTP health check
curl http://localhost/health

# Database connection
docker-compose -f docker-compose.prod.yml exec db psql -U sdg_user -d sdg_assessment -c "SELECT 1;"
```

---

## Updating the Application

### Standard Update Process

```bash
cd /opt/sdg-assessment

# Pull latest changes
git pull origin main

# Rebuild images
docker-compose -f docker-compose.prod.yml build

# Stop current containers
docker-compose -f docker-compose.prod.yml down

# Start updated containers
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web flask db upgrade

# Verify deployment
docker-compose -f docker-compose.prod.yml logs -f web
```

### Rollback Procedure

```bash
# If update fails, rollback to previous version
cd /opt/sdg-assessment

# Stop containers
docker-compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild and start
docker-compose -f docker-compose.prod.yml up -d --build

# Restore database if needed (see Backup section)
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs web

# Check database connectivity
docker-compose -f docker-compose.prod.yml exec web nc -zv db 5432

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Database Connection Errors

```bash
# Check database is running
docker-compose -f docker-compose.prod.yml ps db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Access database shell
docker-compose -f docker-compose.prod.yml exec db psql -U sdg_user -d sdg_assessment
```

### Nginx Errors

```bash
# Check nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Test nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Reload nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Out of Memory

```bash
# Check memory usage
free -h

# Check container memory
docker stats

# If needed, upgrade to VPS-2 (8GB RAM) or reduce workers:
nano gunicorn_config.prod.py
# Change: workers = 1
```

### SSL Certificate Issues

```bash
# Check certificate expiry
certbot certificates

# Force renewal
certbot renew --force-renewal

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## Support & Contact

For issues or questions:

- **Technical Issues**: Check application logs and this troubleshooting guide
- **Bug Reports**: [GitHub Issues](https://github.com/YOUR_ORG/sdg-assessment/issues)
- **UIA IT Support**: Contact Patrick or the UIA IT Team

---

## Security Checklist

- [ ] Firewall configured (UFW enabled, only ports 22/80/443 open)
- [ ] Strong SECRET_KEY generated and set in .env
- [ ] Strong database password set
- [ ] SSL/HTTPS configured with Let's Encrypt
- [ ] Auto-renewal for SSL certificates enabled
- [ ] Daily backups scheduled
- [ ] Application running as non-root user (appuser in Docker)
- [ ] .env file not committed to version control
- [ ] Email configuration tested and working

---

**Last Updated**: 2026-02-20
**Version**: 1.0
