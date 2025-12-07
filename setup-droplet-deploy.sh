#!/bin/bash

# Setup script for Digital Ocean droplet deployment
# Run this ONCE before any automated deployments

set -e

echo "======================================"
echo "Setting up Digital Ocean droplet..."
echo "======================================"

# Update system
echo "Step 1: Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Docker
echo "Step 2: Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Add current user to docker group (if not root)
if [ "$USER" != "root" ]; then
  usermod -aG docker $USER
fi

# Install Docker Compose
echo "Step 3: Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
echo "Step 4: Installing Git..."
apt-get install -y git

# Create app directory
echo "Step 5: Creating /app directory..."
mkdir -p /app
cd /app

# Verify installations
echo ""
echo "======================================"
echo "Verifying installations..."
echo "======================================"
docker --version
docker-compose --version
git --version

echo ""
echo "======================================"
echo "Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Clone the repository: git clone https://github.com/gimhanadeshan/auto-ops-ai.git /app"
echo "2. Or configure git to use SSH key authentication"
echo "3. Run: docker-compose -f docker-compose.prod.yml up -d"
echo ""
