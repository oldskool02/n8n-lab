#!/bin/bash
set -Eeuo pipefail

export PATH="/usr/bin:/bin"

BACKUP_ROOT="/mnt/d/backups"
DAILY="$BACKUP_ROOT/daily"
LOG="$BACKUP_ROOT/logs/backup.log"

DATE=$(date +%F-%H-%M)

mkdir -p "$DAILY"
mkdir -p "$(dirname "$LOG")"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" >> "$LOG"
}

die() {
  log "ERROR: $1"
  /opt/n8n-lab/scripts/alert-telegram.sh "🚨 BACKUP FAILED: $1 on $(hostname)"
  exit 1
}

# Check external drive
if [ ! -d "/mnt/d" ]; then
  die "External drive not mounted"
fi

# Ensure Postgres is healthy before backup
if ! docker exec n8n-lab-postgres-1 pg_isready -U n8n >/dev/null 2>&1; then
  die "Postgres is not ready"
fi

log "Starting backup $DATE"

# 1. Postgres dump (CRITICAL)
if ! /usr/bin/docker exec n8n-lab-postgres-1 pg_dump -U n8n -d n8n > "$DAILY/postgres-$DATE.sql"; then
  die "Postgres backup failed"
fi

log "n8n backup completed"

# Backup CRM database
if ! /usr/bin/docker exec n8n-lab-postgres-1 pg_dump -U n8n -d crm > "$DAILY/crm-$DATE.sql"; then
  die "CRM backup failed"
fi

log "CRM backup completed"

# Validate CRM backup
if ! grep -q "CREATE TABLE" "$DAILY/crm-$DATE.sql"; then
  die "CRM backup verification failed"
fi

CRM_SIZE=$(stat -c%s "$DAILY/crm-$DATE.sql")
if [ "$CRM_SIZE" -lt 1000 ]; then
  die "CRM backup too small — likely failed"
fi

log "CRM backup validated"

# Validate workflows exist
if ! grep -q "workflow_entity" "$DAILY/postgres-$DATE.sql"; then
  die "CRITICAL: No workflows found in backup"
fi

COUNT=$(grep -c "INSERT INTO workflow_entity" "$DAILY/postgres-$DATE.sql" || true)
log "Workflow rows in backup: $COUNT"

if [ "$COUNT" -lt 1 ]; then
  die "CRITICAL: Backup contains ZERO workflows"
fi

# Verify backup is valid SQL
if ! grep -q "PostgreSQL database dump" "$DAILY/postgres-$DATE.sql"; then
  die "Backup verification failed"
fi

SIZE=$(stat -c%s "$DAILY/postgres-$DATE.sql")
if [ "$SIZE" -lt 1000 ]; then
  die "Backup too small — likely failed"
fi

# Compress backups
gzip -c "$DAILY/postgres-$DATE.sql" > "$DAILY/postgres-$DATE.sql.gz"
gzip -c "$DAILY/crm-$DATE.sql" > "$DAILY/crm-$DATE.sql.gz"

# Remove raw SQL
rm "$DAILY/postgres-$DATE.sql"
rm "$DAILY/crm-$DATE.sql"

LATEST="$DAILY/postgres-$DATE.sql.gz"

# Checksum
sha256sum "$LATEST" > "$LATEST.sha256"

if sha256sum -c "$LATEST.sha256"; then
  log "Checksum verification passed"
else
  die "Checksum verification failed"
fi

# 🔴 CRITICAL ADD — TEST RESTORE (before upload!)
log "Testing restore..."

docker run --rm -d --name test-restore \
  -e POSTGRES_PASSWORD=test \
  postgres:16-alpine >/dev/null

# Wait for test DB to be ready
until docker exec test-restore pg_isready -U postgres >/dev/null 2>&1; do
  sleep 1
done

docker exec -i test-restore psql -U postgres -c "CREATE DATABASE n8n;" >/dev/null

gunzip -c "$LATEST" | docker exec -i test-restore psql -U postgres -d n8n >/dev/null

ROWS=$(docker exec test-restore psql -U postgres -d n8n -t -c "SELECT COUNT(*) FROM workflow_entity;" | xargs)

if [ "$ROWS" -lt 1 ]; then
  docker rm -f test-restore >/dev/null
  die "Restore test failed: no workflow data"
fi

log "Restore test passed with $ROWS workflows"

docker rm -f test-restore >/dev/null

docker exec -i test-restore psql -U postgres -c "CREATE DATABASE crm;" >/dev/null

gunzip -c "$DAILY/crm-$DATE.sql.gz" | docker exec -i test-restore psql -U postgres -d crm >/dev/null

if docker exec test-restore psql -U postgres -d crm -c "\dt" | grep -q "accounts"; then
  log "CRM restore test passed"
else
  docker rm -f test-restore >/dev/null
  die "CRM restore test failed"
fi

# 2. Copy stack config
cp /opt/n8n-lab/docker-compose.yml "$DAILY/" || log "WARNING: compose copy failed"
cp /opt/n8n-lab/.env "$DAILY/" || log "WARNING: .env copy failed"

# 3. Copy scripts
tar -czf "$DAILY/scripts-$DATE.tar.gz" /opt/n8n-lab/scripts || log "WARNING: scripts backup failed"

# 3.1 Full stack backup
tar -czf "$DAILY/full-stack-$DATE.tar.gz" \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='*.log' \
  /opt/n8n-lab \
  /opt/n8n-lab/cloudflared \
  || log "WARNING: full stack backup failed"

# Retention local (7 days)
find "$DAILY" -type f -mtime +7 -delete

# Clean logs (14 days)
LOG_DIR="/mnt/d/backups/logs"
if [ -d "$LOG_DIR" ]; then
  find "$LOG_DIR" -type f -mtime +14 -delete
fi

# Upload
if command -v rclone >/dev/null 2>&1; then
  if rclone copy "$DAILY/" onedrive-crypt:daily/ --include "*$DATE*"; then
    log "Offsite backup successful"

    if rclone lsf onedrive-crypt:daily | grep -q "postgres-$DATE.sql.gz"; then
      log "Cloud upload verified"
    else
      /opt/n8n-lab/scripts/alert-telegram.sh "🚨 Cloud backup verification FAILED"
    fi
  else
    log "WARNING: Offsite backup failed"
    /opt/n8n-lab/scripts/alert-telegram.sh "⚠️ Cloud backup failed on $(hostname)"
  fi
else
  log "WARNING: rclone not installed"
fi

# Weekly (Sunday)
if [ "$(date +%u)" -eq 7 ]; then
  rclone copy "$LATEST" onedrive-crypt:weekly/
  log "Weekly backup created"
fi

# Monthly
if [ "$(date +%d)" -eq 01 ]; then
  rclone copy "$LATEST" onedrive-crypt:monthly/
  log "Monthly backup created"
fi

# Cloud retention
if command -v rclone >/dev/null 2>&1; then
  rclone delete onedrive-crypt:daily --min-age 7d || log "WARNING: Cloud retention cleanup failed"
fi

log "Backup completed successfully"