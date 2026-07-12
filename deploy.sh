#!/bin/bash

# ==============================================================================
# SkinScan EC2 Deployment Script
# Automatically pulls the latest code and rebuilds/restarts the Docker containers
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🚀 Starting deployment process..."

# 1. Pull the latest code from the current branch
echo "📦 Pulling latest code from git..."
git pull

# 2. Build and restart Docker containers in detached mode
echo "🐳 Rebuilding and restarting Docker containers..."
# Use docker compose if available (V2), fallback to docker-compose (V1)
if command -v docker compose &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

echo "🧹 Cleaning up dangling Docker images to save space..."
docker image prune -f

echo "✅ Deployment completed successfully!"
