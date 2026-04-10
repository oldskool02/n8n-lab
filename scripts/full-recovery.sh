#!/bin/bash
set -Eeuo pipefail

BACKUP_FILE="${1:-}"

read -p "This will overwrite the database. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
  echo "Aborted"
  exit 1
fi

read -p "Are you sure you want to overwrite the database. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
  echo "Aborted"
  exit 1
fi

LOG="/mnt/d/backups/logs/full-recovery.log"
BACKUP_DIR="/mnt/d/backups/daily"
PROJECT_DIR="/opt/n8n-lab"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG"
}

log "🚨 Starting FULL RECOVERY"

# Step 1 — Ensure backup folder exists
mkdir -p "$BACKUP_DIR"

# Step 2 — Pull latest backups from OneDrive
if ! command -v rclone >/dev/null 2>&1; then
  log "❌ rclone not installed"
  exit 1
fi

log "⬇️ Pulling backups from OneDrive..."
if rclone copy onedrive-crypt:daily "$BACKUP_DIR"; then
  log "✅ Backup download complete"
else
  log "❌ Failed to download backups"
  exit 1
fi

# Step 3 — Find latest backup
if [ -n "$BACKUP_FILE" ]; then
  LATEST="$BACKUP_FILE"
else
  LATEST=$(find "$BACKUP_DIR" -name "postgres-*.sql.gz" -type f -printf '%T@ %p\n' | sort -nr | head -n1 | cut -d' ' -f2-)
fi

if [ -z "$LATEST" ]; then
  log "❌ No backup file found"
  exit 1
fi

if ! gunzip -t "$LATEST"; then
  log "❌ Backup file is corrupted"
  exit 1
fi

log "📦 Latest backup: $LATEST"

# Step 4 — Start ONLY Postgres
log "🐳 Starting Postgres..."
cd "$PROJECT_DIR"
docker compose up -d postgres

# Wait for Postgres
until docker exec n8n-lab-postgres-1 pg_isready -U n8n >/dev/null 2>&1; do
  sleep 1
done

# Step 5 — Restore database
log "🛠 Restoring database..."

gunzip -c "$LATEST" > /tmp/restore.sql

# Drop and recreate n8n DB cleanly
docker exec n8n-lab-postgres-1 psql -U n8n -d postgres -c "DROP DATABASE IF EXISTS n8n;"
docker exec n8n-lab-postgres-1 psql -U n8n -d postgres -c "CREATE DATABASE n8n;"

# Restore
docker exec -i n8n-lab-postgres-1 psql -U n8n -d n8n < /tmp/restore.sql

log "✅ n8n database restored"

# Restore crm database
log "🛠 Restoring database..."
CRM_LATEST=$(ls -t "$BACKUP_DIR"/crm-*.sql.gz 2>/dev/null | head -n1)

if [ -n "$CRM_LATEST" ]; then
  log "🛠 Restoring CRM database..."

  gunzip -c "$CRM_LATEST" > /tmp/crm_restore.sql

  docker exec n8n-lab-postgres-1 psql -U n8n -d postgres -c "DROP DATABASE IF EXISTS crm;"
  docker exec n8n-lab-postgres-1 psql -U n8n -d postgres -c "CREATE DATABASE crm;"

  docker exec -i n8n-lab-postgres-1 psql -U n8n -d crm < /tmp/crm_restore.sql

  rm /tmp/crm_restore.sql

  log "✅ CRM database restored"
else
  log "⚠️ No CRM backup found"
fi

# Verify n8n data
ROWS=$(docker exec n8n-lab-postgres-1 psql -U n8n -d n8n -t -c "SELECT COUNT(*) FROM workflow_entity;" | xargs)

if [ "$ROWS" -lt 1 ]; then
  log "❌ Restore failed: no workflows"
  exit 1
fi

log "✅ Restore verified: $ROWS workflows"

# Step 6 — Cleanup
log "🚀 Starting full stack..."
docker compose up -d

rm /tmp/restore.sql

# Step 7 — Final check
log "🔍 Verifying services..."

if docker ps | grep -q n8n-lab-n8n-1; then
  log "✅ n8n container running"
else
  log "⚠️ n8n container not detected"
fi

log "🎉 FULL RECOVERY COMPLETE"
