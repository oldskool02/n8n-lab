#!/bin/bash

STATUS_FILE="/opt/n8n-lab/.health-status"

# Default to OK
STATUS="OK"

# Run checks (add/remove as needed)

/opt/n8n-lab/scripts/check-n8n.sh || STATUS="FAILED"
/opt/n8n-lab/scripts/check-cloudflared.sh || STATUS="FAILED"
/opt/n8n-lab/scripts/check-disk.sh || STATUS="FAILED"

# Write result
echo "$STATUS" > "$STATUS_FILE"