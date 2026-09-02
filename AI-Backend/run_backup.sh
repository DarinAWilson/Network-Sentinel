#!/bin/bash

set -e

BACKUP_ROOT="/home/daw/network-sentinel-backups"
AI_BACKEND_DIR="/home/daw/Network-Sentinel/AI-Backend"

echo "Starting Network Sentinel backup..."

docker exec ai-backend python backup_network_sentinel.py

LATEST_BACKUP=$(find "$BACKUP_ROOT" \
    -mindepth 1 \
    -maxdepth 1 \
    -type d \
    -printf '%T@ %p\n' \
    | sort -nr \
    | head -n 1 \
    | cut -d' ' -f2-)

if [ -z "$LATEST_BACKUP" ]; then
    echo "ERROR: Backup directory could not be located."
    exit 1
fi

cp "$AI_BACKEND_DIR/.env" \
    "$LATEST_BACKUP/.env"

cp "$AI_BACKEND_DIR/docker-compose.yml" \
    "$LATEST_BACKUP/docker-compose.yml"

chmod 600 "$LATEST_BACKUP/.env"

echo "Runtime configuration copied."
echo "Backup complete: $LATEST_BACKUP"