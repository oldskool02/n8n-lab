set -u

if ! curl -fs https://oldskooln8n.xyz/healthz > /dev/null; then
  if ! curl -fs http://localhost:5678/healthz > /dev/null; then
    /mnt/d/n8n/docker/alert-telegram.sh "❌ n8n DOWN (external + local failed) on $(hostname)"
  fi
fi