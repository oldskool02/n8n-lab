#!/bin/bash
set -Eeuo pipefail

EXPECTED_DIR="/mnt/d/n8n/n8n-lab"
BACKUP_ROOT="/mnt/d/n8n/backups/daily"
LOG_FILE="/mnt/d/n8n/backups/rollback.log"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG_FILE"
}

die() {
  log "❌ ERROR: $1"
  exit 1
}

read -p "⚠️ TYPE ROLLBACK to restore n8n from latest backup: " CONFIRM
[ "$CONFIRM" = "ROLLBACK" ] || { log "❌ Aborted"; exit 1; }

cd "$EXPECTED_DIR" || die "Cannot cd to $EXPECTED_DIR"

LATEST_BACKUP=$(ls -t "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | head -n 1)
[ -n "$LATEST_BACKUP" ] || die "No backup archive found"

log "🧯 Rolling back using: $LATEST_BACKUP"

TEMP_DIR="/tmp/n8n-rollback"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

log "🔹 Extracting archive"
tar -xzf "$LATEST_BACKUP" -C "$TEMP_DIR" || die "Extraction failed"

[ -f "$TEMP_DIR/postgres.dump" ] || die "postgres.dump missing in backup"

log "🔹 Stopping full stack"
docker compose down || die "Failed to stop stack"

log "🔹 Restoring configuration files"
cp "$TEMP_DIR/.env" . || die ".env missing"
cp "$TEMP_DIR/docker-compose.yml" . || die "docker-compose.yml missing"
cp "$TEMP_DIR/config.yml" . || die "config.yml missing"
cp "$TEMP_DIR/cloudflared-config.yml" . 2>/dev/null || log "ℹ️ No cloudflared config"

log "🔹 Starting Postgres only"
docker compose up -d postgres || die "Failed to start Postgres"

POSTGRES_CONTAINER=$(docker compose ps -q postgres)

log "🔹 Waiting for Postgres readiness"
until docker exec "$POSTGRES_CONTAINER" pg_isready -U n8n > /dev/null 2>&1; do
  sleep 2
done

log "🔹 Restoring Postgres database"
docker exec -i "$POSTGRES_CONTAINER" \
  pg_restore -U n8n -d n8n \
  --clean --if-exists \
  < "$TEMP_DIR/postgres.dump" \
  || die "Postgres restore failed"

log "🔹 Starting Redis only"
docker compose up -d redis || die "Failed to start Redis"

REDIS_CONTAINER=$(docker compose ps -q redis)

log "🔹 Stopping Redis before restore"
docker stop "$REDIS_CONTAINER"

docker cp "$TEMP_DIR/redis.rdb" "$REDIS_CONTAINER":/data/dump.rdb \
  || die "Failed to copy Redis dump"

docker start "$REDIS_CONTAINER" || die "Failed to restart Redis"

log "🔹 Starting full stack"
docker compose up -d || die "Failed to start full stack"

rm -rf "$TEMP_DIR"

log "✅ Rollback completed successfully"
