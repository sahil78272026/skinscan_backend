#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# SkinScan — Deploy / Update Script
# Run from the backend/ directory.
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

echo "=== Pulling latest code ==="
git pull origin master

echo "=== Building and starting containers ==="
docker compose up -d --build

echo "=== Waiting for API to become healthy... ==="
for i in {1..30}; do
    if curl -sf http://localhost:8000/healthz > /dev/null 2>&1; then
        echo "✓ API is healthy!"
        curl -s http://localhost:8000/healthz | python3 -m json.tool
        exit 0
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

echo "✗ API did not become healthy within 60 seconds."
echo "  Check logs: docker compose logs api"
exit 1
