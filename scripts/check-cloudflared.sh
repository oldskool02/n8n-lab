if ! docker ps --format '{{.Names}}' | grep -q n8n-lab-cloudflared-1; then
  docker start n8n-lab-cloudflared-1

  sleep 5

  if ! docker ps --format '{{.Names}}' | grep -q n8n-lab-cloudflared-1; then
    /mnt/d/n8n/n8n-lab/alert-telegram.sh "🚨 Cloudflare tunnel FAILED to restart on $(hostname)"
  fi
fi