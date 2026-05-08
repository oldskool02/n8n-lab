#!/bin/bash
set -Eeuo pipefail

STATUS_FILE="/opt/n8n-lab/.update-status"

cd /opt/n8n-lab || exit

echo "=== $(date) ==="

# Default to failed unless we complete everything
echo "FAILED $(date '+%Y-%m-%d %H:%M:%S')" > "$STATUS_FILE"

echo "🔄 Pulling latest images..."
docker compose pull

echo "🔁 Restarting services..."
docker compose up -d --remove-orphans

echo "🧹 Cleaning old images..."
docker image prune -f

# If we reach here, it's a success
echo "OK $(date '+%Y-%m-%d %H:%M:%S')" > "$STATUS_FILE"

echo "✅ Update complete"