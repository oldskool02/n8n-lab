#!/bin/bash
set -Eeuo pipefail

LOG="/mnt/d/backups/logs/restore-test.log"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" >> "$LOG"
}

LATEST=$(ls -t /mnt/d/backups/daily/postgres-*.sql.gz | head -n1)

if [ -z "$LATEST" ]; then
  log "ERROR: No backup found"
  exit 1
fi

log "Testing restore from $LATEST"

# Decompress temporarily
gunzip -c "$LATEST" > /tmp/test-restore.sql

# Create test DB
docker exec -i n8n-lab-postgres-1 psql -U n8n -d postgres -c "DROP DATABASE IF EXISTS restore_test;"
docker exec -i n8n-lab-postgres-1 psql -U n8n -d postgres -c "CREATE DATABASE restore_test;"

# Restore
if docker exec -i n8n-lab-postgres-1 psql -U n8n -d restore_test < /tmp/test-restore.sql; then
  log "Restore test SUCCESS"
else
  log "ERROR: Restore test FAILED"
  /app/scripts/alert-telegram.sh "🚨 Restore test FAILED on $(hostname)"
  exit 1
fi

rm /tmp/test-restore.sql
