#!/bin/bash
set -Eeuo pipefail

LOG="/mnt/d/backups/logs/rebuild.log"
PROJECT_DIR="/opt/n8n-lab"
BACKUP_DIR="/mnt/d/backups/daily"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG"
}

die() {
  log "❌ $1"
  exit 1
}

log "🚨 FULL SYSTEM REBUILD STARTED"

# Safety confirmation
read -p "⚠️ This will DESTROY and rebuild everything. Type YES to continue: " confirm
if [ "$confirm" != "YES" ]; then
  die "Aborted"
fi

# Check dependencies
command -v docker >/dev/null || die "Docker not installed"
command -v rclone >/dev/null || die "rclone not installed"

# Step 1 — Use local backups
mkdir -p "$BACKUP_DIR"

# log "📦 Using local backups from $BACKUP_DIR"
# if [ -z "${LATEST_N8N:-}" ]; then
#   die "No n8n backup found"
# fi

# log "Latest n8n backup: $LATEST_N8N"

# if ! rclone copy onedrive-crypt:daily "$BACKUP_DIR"; then
#  die "Failed to pull backups"
# fi

# Step 2 — Find latest backups
# LATEST_N8N=$(ls -t "$BACKUP_DIR"/postgres-*.sql.gz 2>/dev/null | head -n1)
# LATEST_N8N=$(ls -t "$BACKUP_DIR"/postgres-*.sql.gz 2>/dev/null | head -n1 || true)
LATEST_N8N=$(find "$BACKUP_DIR" -type f -name "postgres-*.sql.gz" | sort | tail -n1)
# LATEST_CRM=$(ls -t "$BACKUP_DIR"/crm-*.sql.gz 2>/dev/null | head -n1)
# LATEST_CRM=$(ls -t "$BACKUP_DIR"/crm-*.sql.gz 2>/dev/null | head -n1 || true)
LATEST_CRM=$(find "$BACKUP_DIR" -type f -name "crm-*.sql.gz" | sort | tail -n1 || true)

if [ -z "${LATEST_N8N:-}" ]; then
  die "No n8n backup found"
fi

log "Latest n8n backup: $LATEST_N8N"

[ -z "$LATEST_N8N" ] && die "No n8n backup found"

log "📦 Using:"
log "n8n: $LATEST_N8N"
[ -n "$LATEST_CRM" ] && log "crm: $LATEST_CRM"

# Validate backups
gunzip -t "$LATEST_N8N" || die "n8n backup corrupted"
[ -n "$LATEST_CRM" ] && gunzip -t "$LATEST_CRM" || true

# Step 3 — Stop everything
log "🛑 Stopping stack..."
cd "$PROJECT_DIR"
docker compose down || true

# Step 4 — Start ONLY Postgres
log "🐘 Starting Postgres..."
docker compose up -d postgres

until docker exec n8n-lab-postgres-1 pg_isready -U n8n >/dev/null 2>&1; do
  sleep 1
done

# Step 5 — Restore n8n DB
log "🛠 Restoring n8n DB..."

docker exec n8n-lab-postgres-1 psql -U n8n -d postgres -c "DROP DATABASE IF EXISTS n8n;"
docker exec n8n-lab-postgres-1 psql -U n8n -d postgres -c "CREATE DATABASE n8n;"

gunzip -c "$LATEST_N8N" | docker exec -i n8n-lab-postgres-1 psql -U n8n -d n8n

# Verify n8n restore
ROWS=$(docker exec n8n-lab-postgres-1 psql -U n8n -d n8n -t -c "SELECT COUNT(*) FROM workflow_entity;" | xargs)

if [ "$ROWS" -lt 1 ]; then
  die "n8n restore failed (no workflows)"
fi

log "✅ n8n restored ($ROWS workflows)"

# Step 6 — Restore CRM DB
if [ -n "$LATEST_CRM" ]; then
  log "🛠 Restoring CRM DB..."

  docker exec n8n-lab-postgres-1 psql -U n8n -d postgres -c "DROP DATABASE IF EXISTS crm;"
  docker exec n8n-lab-postgres-1 psql -U n8n -d postgres -c "CREATE DATABASE crm;"

  gunzip -c "$LATEST_CRM" | docker exec -i n8n-lab-postgres-1 psql -U n8n -d crm

  log "✅ CRM restored"
fi

# Step 7 — Start full stack
log "🚀 Starting full stack..."
docker compose up -d

sleep 10

# Step 8 — Final verification
log "🔍 Verifying services..."

docker ps | grep -q n8n-lab-n8n-1 || die "n8n not running"
docker ps | grep -q n8n-lab-postgres-1 || die "Postgres not running"

log "🎉 SYSTEM REBUILD COMPLETE"
