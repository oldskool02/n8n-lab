#!/bin/bash
set -Eeuo pipefail

### CONFIG ###
BACKUP_DIR="/opt/n8n-lab/backups/daily"
POSTGRES_CONTAINER="n8n-lab-postgres-1"
N8N_CONTAINER="n8n-lab-n8n-1"

LATEST_DB=$(ls -t $BACKUP_DIR/n8n.sql.gz | head -n1)
LATEST_FILES=$(ls -t $BACKUP_DIR/n8n-files*.tar.gz | head -n1)

log() { echo "$(date '+%F %T') | $1"; }
fail() { log "❌ $1"; exit 1; }

log "🚨 FULL RESTORE STARTING"

### STOP SERVICES ###
docker compose stop n8n n8n-worker || true

### ENSURE POSTGRES RUNNING ###
docker compose up -d postgres
sleep 5

### KILL CONNECTIONS ###
docker exec $POSTGRES_CONTAINER psql -U n8n -d postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'n8n';
"

### DROP + RECREATE ###
docker exec $POSTGRES_CONTAINER psql -U n8n -d postgres -c "DROP DATABASE IF EXISTS n8n;"
docker exec $POSTGRES_CONTAINER psql -U n8n -d postgres -c "CREATE DATABASE n8n;"

### RESTORE DB ###
log "📦 Restoring database"
gunzip -c "$LATEST_DB" | docker exec -i $POSTGRES_CONTAINER psql -U n8n -d n8n \
  || fail "DB restore failed"

### RESTORE FILES ###
log "📁 Restoring n8n files"
docker run --rm \
  -v n8n-lab-n8n_data:/data \
  -v "$BACKUP_DIR":/backup \
  alpine sh -c "rm -rf /data/* && tar xzf /backup/$(basename $LATEST_FILES) -C /data" \
  || fail "File restore failed"

### START SYSTEM ###
docker compose up -d

### VERIFY ###
sleep 5

COUNT=$(docker exec $POSTGRES_CONTAINER psql -U n8n -d n8n -t -c "SELECT COUNT(*) FROM workflow_entity;" | xargs)

[ "$COUNT" -gt 0 ] || fail "Restore verification failed"

log "✅ RESTORE COMPLETE ($COUNT workflows)"