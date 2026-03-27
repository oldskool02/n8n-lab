#!/bin/bash
set -Eeuo pipefail

cd /mnt/d/n8n/n8n-lab

echo "🔹 Pulling latest images..."
docker compose pull

echo "🔹 Restarting services gracefully..."
docker compose up -d --remove-orphans

echo "✅ Update complete"
