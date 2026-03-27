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
  /app/scripts/alert-telegram.sh "🚨 BACKUP FAILED: $1 on $(hostname)"
  exit 1
}

# Check external drive
if [ ! -d "/mnt/d" ]; then
  die "External drive not mounted"
fi

log "Starting backup $DATE"

# 1. Postgres dump (CRITICAL)
if ! /usr/bin/docker exec n8n-lab-postgres-1 pg_dumpall -U n8n > "$DAILY/postgres-$DATE.sql"; then
  die "Postgres backup failed"
fi

# 2. Copy stack config
cp /home/ianw/docker/n8n-lab/docker-compose.yml "$DAILY/" || log "WARNING: compose copy failed"
cp /home/ianw/docker/n8n-lab/.env "$DAILY/" || log "WARNING: .env copy failed"

# 3. Copy scripts
tar -czf "$DAILY/scripts-$DATE.tar.gz" /app/scripts || log "WARNING: scripts backup failed"

# 4. Retention (7 days)
find "$DAILY" -type f -mtime +7 -delete

# Verify backup is valid SQL
if ! grep -q "PostgreSQL database dump" "$DAILY/postgres-$DATE.sql"; then
  die "Backup verification failed"
fi

SIZE=$(stat -c%s "$DAILY/postgres-$DATE.sql")

if [ "$SIZE" -lt 1000 ]; then
  die "Backup too small — likely failed"
fi

LOG_DIR="/mnt/d/backups/logs"

if [ -d "$LOG_DIR" ]; then
  find "$LOG_DIR" -type f -mtime +14 -delete
fi

# Compress backup file
gzip -c "$DAILY/postgres-$DATE.sql" > "$DAILY/postgres-$DATE.sql.gz"

# Create Checksum
sha256sum "$DAILY/postgres-$DATE.sql.gz" > "$DAILY/postgres-$DATE.sql.gz.sha256"

# Checksum  verification
if sha256sum -c "$DAILY/postgres-$DATE.sql.gz.sha256"; then
  log "Checksum verification passed"
else
  log "ERROR: Checksum verification failed"
  /app/scripts/alert-telegram.sh "🚨 Backup corrupted before upload"
  exit 1
fi

# Daily Offsite backup
if command -v rclone >/dev/null 2>&1; then
  if rclone copy "$DAILY/postgres-$DATE.sql.gz" onedrive-crypt:daily/; then
    log "Offsite backup successful"

    # Verify ONLY if upload succeeded
    if rclone lsf onedrive-crypt:daily | grep -q "postgres-$DATE.sql.gz"; then
      log "Cloud upload verified"
    else
      log "ERROR: Cloud upload verification failed"
      /app/scripts/alert-telegram.sh "🚨 Cloud backup verification FAILED"
    fi

  else
    log "WARNING: Offsite backup failed"
    /app/scripts/alert-telegram.sh "⚠️ Cloud backup failed on $(hostname)"
  fi
else
  log "WARNING: rclone not installed"
fi

# Weekly backup (Sunday)
if [ "$(date +%u)" -eq 7 ]; then
  rclone copy "$DAILY/postgres-$DATE.sql.gz" onedrive-crypt:weekly/
  log "Weekly backup created"
fi

# Monthly backup (1st day of month)
if [ "$(date +%d)" -eq 01 ]; then
  rclone copy "$DAILY/postgres-$DATE.sql.gz" onedrive-crypt:monthly/
  log "Monthly backup created"
fi

# Cloud retention (keep last 7 days)
if command -v rclone >/dev/null 2>&1; then
  if rclone delete onedrive-crypt:daily --min-age 7d; then
    log "Cloud retention cleanup successful"
  else
    log "WARNING: Cloud retention cleanup failed"
  fi
fi

# Remove backup file. Leave compressed
rm "$DAILY/postgres-$DATE.sql"

log "Backup completed successfully"
