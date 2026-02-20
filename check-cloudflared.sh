if ! docker ps --format '{{.Names}}' | grep -q n8n-lab-cloudflared-1; then
  /mnt/d/n8n/n8n-lab/alert-telegram.sh "🚨 Cloudflare tunnel container is DOWN on $(hostname)"
fi
