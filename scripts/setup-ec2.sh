#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# SkinScan — EC2 First-Time Setup Script (Ubuntu 24.04 ARM)
# Run as root or with sudo on a fresh t4g.small instance.
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

echo "=== [1/5] System update ==="
apt-get update && apt-get upgrade -y

echo "=== [2/5] Install Docker ==="
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

echo "=== [3/5] Install Docker Compose plugin ==="
apt-get install -y docker-compose-plugin

echo "=== [4/5] Create app user ==="
useradd -m -s /bin/bash -G docker skinscan || true

echo "=== [5/5] Clone repo and prepare ==="
su - skinscan -c "
  git clone https://github.com/YOUR_USERNAME/skincare.git ~/skincare || true
  cd ~/skincare/backend
  cp .env.example .env
  echo '>>> Edit ~/skincare/backend/.env with your production values, then run deploy.sh'
"

echo ""
echo "═══════════════════════════════════════════════"
echo "  Setup complete!"
echo "  1. Switch to the skinscan user:  su - skinscan"
echo "  2. Edit the env file:            nano ~/skincare/backend/.env"
echo "  3. Deploy:                       cd ~/skincare/backend && bash deploy.sh"
echo "═══════════════════════════════════════════════"
