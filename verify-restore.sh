#!/bin/bash
set -Eeuo pipefail

LOG_FILE="/mnt/d/n8n/backups/verify-restore.log"
BACKUP_ROOT="/mnt/d/n8n/backups/daily"

cleanup() {
  log "🧹 Cleaning up verification environment"

  docker rm -f verify-n8n verify-postgres verify-redis 2>/dev/null || true
  docker network rm "$VERIFY_NET" 2>/dev/null || true
  rm -rf "$VERIFY_TMP" || true
}

trap cleanup EXIT INT TERM

if ! docker ps --format '{{.Names}}' | grep -q '^n8n-lab-n8n-1$'; then
  die "Production n8n container not running — aborting verification"
fi

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG_FILE"
}

die() {
  log "❌ ERROR: $1"
  /mnt/d/n8n/n8n-lab/alert-telegram.sh "❌ Backup restore verification FAILED on $(hostname): $1"
  exit 1
}

log "🔹 Starting backup restore verification"

LATEST_BACKUP=$(ls -t "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | head -n 1)
[ -n "$LATEST_BACKUP" ] || die "No backup archive found"

log "🔹 Using backup: $LATEST_BACKUP"

VERIFY_TMP="/tmp/n8n-verify"

rm -rf "$VERIFY_TMP"
mkdir -p "$VERIFY_TMP" || die "Failed to create temp dir"

log "🔹 Extracting backup"
tar -xzf "$LATEST_BACKUP" -C "$VERIFY_TMP" || die "Failed to extract backup"

VERIFY_NET="n8n_verify"

if ! docker network ls --format '{{.Name}}' | grep -q "^${VERIFY_NET}$"; then
  log "🔹 Creating verification network"
  docker network create "$VERIFY_NET" || die "Failed to create network"
fi

# Clean up any previous verification containers
for c in verify-postgres verify-redis verify-n8n; do
  if docker ps -a --format '{{.Names}}' | grep -q "^${c}$"; then
    log "🧹 Removing existing container: $c"
    docker rm -f "$c" || die "Failed to remove container $c"
  fi
done

log "🔹 Starting temporary Postgres"
docker run -d \
  --name verify-postgres \
  --network "$VERIFY_NET" \
  -e POSTGRES_DB=n8n \
  -e POSTGRES_USER=n8n \
  -e POSTGRES_PASSWORD=verifypass \
  postgres:16 || die "Failed to start verify-postgres"

log "🔹 Starting temporary Redis"
docker run -d \
  --name verify-redis \
  --network "$VERIFY_NET" \
  redis:7-alpine || die "Failed to start verify-redis"

sleep 10

log "🔹 Restoring Postgres into temporary database"

docker exec -i verify-postgres psql -U n8n n8n < "$VERIFY_TMP/postgres.sql" \
  || die "Postgres restore failed"

log "🔹 Restoring Redis data"

docker cp "$VERIFY_TMP/redis.rdb" verify-redis:/data/dump.rdb \
  || die "Failed to copy Redis dump"

docker restart verify-redis \
  || die "Failed to restart Redis with restored data"

sleep 5

log "🔹 Starting temporary n8n instance"

docker run -d \
  --name verify-n8n \
  --network "$VERIFY_NET" \
  -p 5679:5678 \
  -e DB_TYPE=postgresdb \
  -e DB_POSTGRESDB_HOST=verify-postgres \
  -e DB_POSTGRESDB_PORT=5432 \
  -e DB_POSTGRESDB_DATABASE=n8n \
  -e DB_POSTGRESDB_USER=n8n \
  -e DB_POSTGRESDB_PASSWORD=verifypass \
  -e EXECUTIONS_MODE=queue \
  -e QUEUE_BULL_REDIS_HOST=verify-redis \
  -e QUEUE_BULL_REDIS_PORT=6379 \
  -e N8N_DIAGNOSTICS_ENABLED=false \
  -e N8N_PERSONALIZATION_ENABLED=false \
  -e N8N_VERSION_NOTIFICATIONS_ENABLED=false \
  -e N8N_COMMUNITY_PACKAGES_ENABLED=true \
  n8nio/n8n:stable \
  || die "Failed to start verify-n8n"

sleep 20

log "✅ Restore verification PASSED"
exit 0
