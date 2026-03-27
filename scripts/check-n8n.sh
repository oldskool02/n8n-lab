if ! curl -fs --max-time 5 --retry 2 https://oldskooln8n.xyz/healthz > /dev/null; then
  if ! curl -fs --max-time 3 http://localhost:5678/healthz > /dev/null; then
    /mnt/d/n8n/n8n-lab/alert-telegram.sh "❌ n8n DOWN (external + local failed) on $(hostname)"
  fi
fi

status=$(docker inspect --format='{{.State.Health.Status}}' n8n-lab-n8n-1 2>/dev/null)

if [ "$status" != "healthy" ]; then
  docker restart n8n-lab-n8n-1
  /mnt/d/n8n/n8n-lab/alert-telegram.sh "⚠️ n8n container unhealthy: $status on $(hostname)"
fi
