#!/bin/bash

USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$USAGE" -gt 85 ]; then
  /home/ianw/docker/n8n-lab/scripts/alert-telegram.sh "⚠️ Disk usage high: ${USAGE}%"
fi
