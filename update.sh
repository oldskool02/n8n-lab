#!/bin/bash
set -Eeuo pipefail

BACKUP_ROOT="/mnt/d/n8n/backups/daily"
LATEST_BACKUP=$(ls -t $BACKUP_ROOT/*.tar.gz | head -n 1)

if [ -z "$LATEST_BACKUP" ]; then
  echo "❌ No backup found. Rollback aborted."
  exit 1
fi

echo "🧯 Rolling back using backup:"
echo "   $LATEST_BACKUP"

TEMP_DIR="/tmp/n8n-rollback"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo "🔹 Extracting backup..."
tar -xzf "$LATEST_BACKUP" -C "$TEMP_DIR"

echo "🔹 Stopping containers..."
cd /mnt/d/n8n/docker
docker compose down

echo "🔹 Restoring config files..."
cp "$TEMP_DIR/.env" .
cp "$TEMP_DIR/docker-compose.yml" .
cp "$TEMP_DIR/config.yml" .
cp "$TEMP_DIR/cloudflared-config.yml" . 2>/dev/null || true

echo "🔹 Starting base services..."
docker compose up -d postgres redis
sleep 10

echo "🔹 Restoring Postgres..."
docker exec -i docker-postgres-1 psql -U n8n n8n < "$TEMP_DIR/postgres.sql"

echo "🔹 Restoring Redis..."
docker cp "$TEMP_DIR/redis.rdb" docker-redis-1:/data/dump.rdb
docker restart docker-redis-1

echo "🔹 Starting full stack..."
docker compose up -d

echo "✅ Rollback completed successfully
