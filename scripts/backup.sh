#!/bin/bash
set -Eeuo pipefail

### CONFIG ###
PROJECT_DIR="/opt/n8n-lab"
BACKUP_ROOT="/opt/n8n-lab/backups"
DAILY="$BACKUP_ROOT/daily"
LOG="$BACKUP_ROOT/logs/backup.log"

POSTGRES_CONTAINER="n8n-lab-postgres-1"
N8N_CONTAINER="n8n-lab-n8n-1"

DATE=$(date +%F-%H-%M)
TMP_DIR="/tmp/n8n-backup-$DATE"

ALERT_EMAIL="ian@oldskool.co.za"   # optional
WEBHOOK_URL=""                  # optional

### LOGGING ###
log() { echo "$(date '+%F %T') | $1" | tee -a "$LOG"; }
fail() {
  log "❌ ERROR: $1"
  [ -n "$WEBHOOK_URL" ] && curl -s -X POST "$WEBHOOK_URL" -d "backup failed: $1" || true
  exit 1
}

mkdir -p "$DAILY" "$TMP_DIR" "$(dirname "$LOG")"

log "🚀 Starting backup: $DATE"

### PRECHECK ###
docker ps | grep -q "$POSTGRES_CONTAINER" || fail "Postgres not running"
docker ps | grep -q "$N8N_CONTAINER" || fail "n8n not running"

### CONSISTENCY PAUSE ###
log "⏸ Pausing n8n"
docker pause "$N8N_CONTAINER" || fail "pause failed"

### DB BACKUP ###
log "📦 Dumping database"
docker exec "$POSTGRES_CONTAINER" pg_dump -U n8n -d n8n > "$TMP_DIR/n8n.sql" \
  || fail "DB dump failed"

### FILE BACKUP ###
log "📁 Backing up n8n data volume"
docker run --rm \
  -v n8n-lab-n8n_data:/data \
  -v "$TMP_DIR":/backup \
  alpine tar czf /backup/n8n-files.tar.gz -C /data . \
  || fail "Volume backup failed"

### RESUME ###
docker unpause "$N8N_CONTAINER"

### VALIDATION ###
log "🔍 Validating backup"

# Check DB size
[ $(stat -c%s "$TMP_DIR/n8n.sql") -gt 100000 ] || fail "DB too small"

# Check workflows exist
ROWS=$(grep -c "workflow_entity" "$TMP_DIR/n8n.sql" || true)
[ "$ROWS" -gt 0 ] || fail "No workflows in dump"

### COMPRESS ###
gzip "$TMP_DIR/n8n.sql"

### CHECKSUM ###
sha256sum "$TMP_DIR"/* > "$TMP_DIR/checksums.sha256"
sha256sum -c "$TMP_DIR/checksums.sha256" || fail "Checksum failed"

### MOVE TO FINAL ###
mv "$TMP_DIR"/* "$DAILY/"
rm -rf "$TMP_DIR"

### RETENTION ###
find "$DAILY" -type f -mtime +7 -delete

log "✅ Backup complete: $DATE"