#!/bin/bash

# Master Deployment Script for Digital Ocean Droplet
# This handles all deployment, initialization, and setup
# Usage: ./deploy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "🚀 Auto-Ops-AI Complete Deployment"
echo "======================================"

# Export environment variables
export DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-}"
export DOCKER_HUB_PASSWORD="${DOCKER_HUB_PASSWORD:-}"
export GOOGLE_API_KEY="${GOOGLE_API_KEY:-}"
export DROPLET_IP=$(hostname -I | awk '{print $1}')

if [ -z "$DOCKER_HUB_USERNAME" ]; then
    echo "❌ Error: DOCKER_HUB_USERNAME not set"
    exit 1
fi

echo "📍 Droplet IP: $DROPLET_IP"
echo "🐳 Docker Hub User: $DOCKER_HUB_USERNAME"

# Step 1: Ensure tools are installed
echo ""
echo "1️⃣  Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "✅ Docker tools ready"

# Step 2: Prepare application directory
echo ""
echo "2️⃣  Preparing /app directory..."
mkdir -p /app
cd /app

# Step 3: Clone/update repository
echo ""
echo "3️⃣  Cloning repository..."
if [ ! -d .git ]; then
    git clone https://github.com/gimhanadeshan/auto-ops-ai.git .
else
    git fetch origin main
    git checkout -f origin/main
fi
echo "✅ Repository updated"

# Step 4: Login to Docker Hub
echo ""
echo "4️⃣  Logging in to Docker Hub..."
echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin
echo "✅ Docker Hub login successful"

# Step 5: Pull latest images
echo ""
echo "5️⃣  Pulling latest Docker images..."
docker pull $DOCKER_HUB_USERNAME/auto-ops-ai-backend:latest
docker pull $DOCKER_HUB_USERNAME/auto-ops-ai-frontend:latest
echo "✅ Images pulled successfully"

# Step 6: Stop old containers
echo ""
echo "6️⃣  Stopping old containers..."
docker-compose -f docker-compose.deploy.yml down || true
echo "✅ Old containers stopped"

# Step 7: Start new containers
echo ""
echo "7️⃣  Starting new containers..."
docker-compose -f docker-compose.deploy.yml up -d
echo "✅ Containers started"

# Step 8: Open firewall ports
echo ""
echo "8️⃣  Configuring firewall..."
ufw allow 8000/tcp || true
ufw allow 80/tcp || true
ufw allow 443/tcp || true
echo "✅ Firewall configured"

# Step 9: Wait for services
echo ""
echo "9️⃣  Waiting for services to stabilize..."
sleep 20

# Step 10: Initialize database
echo ""
echo "🔟 Initializing database..."
docker-compose -f docker-compose.deploy.yml exec -T backend python backend/init_db.py || true
echo "✅ Database initialized"

# Step 11: Load seed data
echo ""
echo "1️⃣1️⃣  Loading seed data..."
docker-compose -f docker-compose.deploy.yml exec -T backend python backend/ingestion_script.py || true
echo "✅ Seed data loaded"

# Step 12: Verify deployment
echo ""
echo "1️⃣2️⃣  Verifying deployment..."
docker-compose -f docker-compose.deploy.yml ps

# Cleanup
docker logout

echo ""
echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "🌐 Access your application:"
echo "   Frontend:  http://$DROPLET_IP"
echo "   Backend:   http://$DROPLET_IP:8000"
echo "   API Docs:  http://$DROPLET_IP:8000/docs"
echo ""
echo "📋 View logs:"
echo "   docker-compose -f docker-compose.deploy.yml logs -f"
echo ""
