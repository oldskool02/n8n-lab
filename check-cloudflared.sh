if ! docker ps --format '{{.Names}}' | grep -q docker-cloudflared-1; then
  /mnt/d/n8n/docker/alert-telegram.sh "🚨 Cloudflare tunnel container is DOWN on $(hostname)"
fi
