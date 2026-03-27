#!/bin/bash
set -Eeuo pipefail

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
PROJECT_DIR="/home/ianw/docker/n8n-lab"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG"
}

log "🚨 Starting FULL RECOVERY"

# Step 1 — Ensure backup folder exists
mkdir -p "$BACKUP_DIR"

# Step 2 — Pull latest backups from OneDrive
log "⬇️ Pulling backups from OneDrive..."
if rclone copy onedrive-crypt:daily "$BACKUP_DIR"; then
  log "✅ Backup download complete"
else
  log "❌ Failed to download backups"
  exit 1
fi

# Step 3 — Find latest backup
LATEST=$(ls -t "$BACKUP_DIR"/postgres-*.sql.gz 2>/dev/null | head -n1)

if [ -z "$LATEST" ]; then
  log "❌ No backup file found"
  exit 1
fi

log "📦 Latest backup: $LATEST"

# Step 4 — Start Docker services
log "🐳 Starting Docker services..."
cd "$PROJECT_DIR"
docker compose up -d

sleep 10

# Step 5 — Restore database
log "🛠 Restoring database..."

gunzip -c "$LATEST" > /tmp/restore.sql

docker exec -i n8n-lab-postgres-1 psql -U n8n < /tmp/restore.sql

log "✅ Database restored"

# Step 6 — Cleanup
rm /tmp/restore.sql

# Step 7 — Final check
log "🔍 Verifying services..."

if docker ps | grep -q n8n-lab-n8n-1; then
  log "✅ n8n container running"
else
  log "⚠️ n8n container not detected"
fi

log "🎉 FULL RECOVERY COMPLETE"
