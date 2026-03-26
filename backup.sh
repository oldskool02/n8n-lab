#!/bin/bash
DATE=$(date +%F-%H-%M)

docker exec n8n-lab-postgres-1 pg_dump -U n8n n8n > backups/n8n-$DATE.sql
