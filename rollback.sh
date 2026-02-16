#!/bin/bash
set -Eeuo pipefail

# =========================
# Configuration
# =========================
EXPECTED_DIR="/mnt/d/n8n/docker"
BACKUP_ROOT="/mnt/d/n8n/backups/daily"
LOG_FILE="/mnt/d/n8n/backups/rollback.log"

# =========================
# Helper functions
# =========================
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG_FILE"
}

die() {
  log "❌ ERROR: $1"
  exit 1
}

# =========================
# Safety confirmation
# =========================
read -p "⚠️ TYPE ROLLBACK to restore n8n from the latest backup: " CONFIRM
if [ "$CONFIRM" != "ROLLBACK" ]; then
  log "❌ Rollback aborted by user"
  exit 1
fi

# =========================
# Environment sanity checks
# =========================
cd "$EXPECTED_DIR" || die "Cannot change directory to $EXPECTED_DIR"

LATEST_BACKUP=$(ls -t "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | head -n 1)
[ -n "$LATEST_BACKUP" ] || die "No backup archive found in $BACKUP_ROOT"

log "🧯 Starting rollback using backup:"
log "   $LATEST_BACKUP"

# =========================
# Extract backup
# =========================
TEMP_DIR="/tmp/n8n-rollback"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR" || die "Failed to create temp directory"

log "🔹 Extracting backup archive"
tar -xzf "$LATEST_BACKUP" -C "$TEMP_DIR" || die "Failed to extract backup"

# =========================
# Stop stack
# =========================
log "🔹 Stopping all containers"
docker compose down || die "Failed to stop containers"

# =========================
# Restore configuration
# =========================
log "🔹 Restoring configuration files"
cp "$TEMP_DIR/.env" . || die "Missing .env in backup"
cp "$TEMP_DIR/docker-compose.yml" . || die "Missing docker-compose.yml in backup"
cp "$TEMP_DIR/config.yml" . || die "Missing config.yml in backup"
cp "$TEMP_DIR/cloudflared-config.yml" . 2>/dev/null || log "ℹ️ cloudflared config not present (ok)"

# =========================
# Start base services
# =========================
log "🔹 Starting Postgres and Redis"
docker compose up -d postgres redis || die "Failed to start Postgres/Redis"

sleep 10

# =========================
# Restore Postgres
# =========================
log "🔹 Restoring Postgres database"
docker exec -i docker-postgres-1 psql -U n8n n8n < "$TEMP_DIR/postgres.sql" \
  || die "Postgres restore failed"

# =========================
# Restore Redis
# =========================
log "🔹 Restoring Redis data"
docker cp "$TEMP_DIR/redis.rdb" docker-redis-1:/data/dump.rdb \
  || die "Failed to copy Redis dump"

docker restart docker-redis-1 || die "Failed to restart Redis"

# =========================
# Start full stack
# =========================
log "🔹 Starting full n8n stack"
docker compose up -d || die "Failed to start full stack"

# =========================
# Cleanup
# =========================
rm -rf "$TEMP_DIR" || log "⚠️ Failed to clean temp directory (manual cleanup may be required)"

log "✅ Rollback completed successfully"
