#!/bin/bash
set -Eeuo pipefail

LOG_FILE="/mnt/d/n8n/backups/backup.log"
BACKUP_ROOT="/mnt/d/n8n/backups/daily"
REMOTE="onedrive-crypt:daily"
RETENTION_DAYS=30

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG_FILE"
}

die() {
  log "❌ ERROR: $1"
  exit 1
}

log "🔹 Starting n8n backup"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M") || die "Failed to generate timestamp"
WORK_DIR="$BACKUP_ROOT/$TIMESTAMP"
ARCHIVE="$WORK_DIR.tar.gz"

mkdir -p "$WORK_DIR" || die "Failed to create backup directory"

# --------------------------------------------------
# Config files
# --------------------------------------------------

log "🔹 Backing up config files"

cp /mnt/d/n8n/n8n-lab/.env "$WORK_DIR/" || die ".env not found"
cp /mnt/d/n8n/n8n-lab/docker-compose.yml "$WORK_DIR/" || die "docker-compose.yml not found"
cp /mnt/d/n8n/n8n-lab/config.yml "$WORK_DIR/" || die "config.yml not found"
cp /mnt/d/n8n/n8n-lab/cloudflared-config.yml "$WORK_DIR/" 2>/dev/null || log "ℹ️ cloudflared config not present (ok)"

# --------------------------------------------------
# Postgres
# --------------------------------------------------

log "🔹 Backing up Postgres"

docker exec n8n-lab-postgres-1 \
  pg_dump -U n8n \
  -F c \
  -Z 9 \
  --no-owner \
  --no-privileges \
  n8n \
  > "$WORK_DIR/postgres.dump" \
  || die "Postgres dump failed"

[ -s "$WORK_DIR/postgres.dump" ] || die "Postgres dump empty"

# --------------------------------------------------
# Redis
# --------------------------------------------------

log "🔹 Backing up Redis"

docker exec n8n-lab-redis-1 redis-cli SAVE \
  || die "Redis SAVE failed"

docker cp n8n-lab-redis-1:/data/dump.rdb "$WORK_DIR/redis.rdb" \
  || die "Failed to copy Redis dump"

# --------------------------------------------------
# Compress
# --------------------------------------------------

log "🔹 Compressing backup"

tar -czf "$ARCHIVE" -C "$WORK_DIR" . \
  || die "Compression failed"

[ -s "$ARCHIVE" ] || die "Archive is empty"

# Generate checksum
sha256sum "$ARCHIVE" > "$ARCHIVE.sha256"

rm -rf "$WORK_DIR" || die "Failed to remove temp directory"

log "🔹 Uploading to encrypted offsite storage"

rclone copy "$ARCHIVE" "$REMOTE" || die "Upload failed"
rclone copy "$ARCHIVE.sha256" "$REMOTE" || die "Checksum upload failed"

log "🔹 Verifying remote integrity"

rclone check "$ARCHIVE" "$REMOTE" || die "Remote verification failed"

log "🔹 Applying retention policy (${RETENTION_DAYS} days)"

rclone delete --min-age ${RETENTION_DAYS}d "$REMOTE" \
  || die "Retention cleanup failed"

log "✅ Backup completed successfully"
