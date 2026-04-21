#!/bin/bash
# SDG Assessment Tool - Database Backup Script
#
# This script creates compressed PostgreSQL backups with 7-day retention
# Schedule: Daily at 2 AM via cron
# Crontab entry: 0 2 * * * /opt/sdg-assessment/backup.sh >> /var/log/sdg-backup.log 2>&1

set -e  # Exit on any error

# Configuration
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
APP_DIR="/opt/sdg-assessment"
COMPOSE_FILE="$APP_DIR/docker-compose.prod.yml"
RETENTION_DAYS=7

# Database credentials (from .env file)
POSTGRES_USER="${POSTGRES_USER:-sdg_user}"
POSTGRES_DB="${POSTGRES_DB:-sdg_assessment}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Log backup start
echo "========================================="
echo "SDG Assessment Database Backup"
echo "Date: $(date)"
echo "========================================="

# Check if Docker Compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "ERROR: Docker Compose file not found at $COMPOSE_FILE"
    exit 1
fi

# Check if database container is running
if ! docker-compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
    echo "ERROR: Database container is not running"
    exit 1
fi

# Create database backup
echo "Backing up database..."
BACKUP_FILE="$BACKUP_DIR/db_$DATE.sql"

docker-compose -f "$COMPOSE_FILE" exec -T db \
    pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Database backup created: $BACKUP_FILE"
else
    echo "✗ Database backup failed"
    exit 1
fi

# Compress backup
echo "Compressing backup..."
gzip "$BACKUP_FILE"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

if [ -f "$COMPRESSED_FILE" ]; then
    BACKUP_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    echo "✓ Backup compressed: $COMPRESSED_FILE ($BACKUP_SIZE)"
else
    echo "✗ Compression failed"
    exit 1
fi

# Clean up old backups (keep last 7 days)
echo "Cleaning old backups (keeping last $RETENTION_DAYS days)..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -type f -delete -print | wc -l)

if [ "$DELETED_COUNT" -gt 0 ]; then
    echo "✓ Deleted $DELETED_COUNT old backup(s)"
else
    echo "✓ No old backups to delete"
fi

# List current backups
echo ""
echo "Current backups:"
ls -lh "$BACKUP_DIR"/db_*.sql.gz | tail -n 10

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo ""
echo "Total backup directory size: $TOTAL_SIZE"

# Log completion
echo ""
echo "✓ Backup completed successfully"
echo "========================================="

exit 0
