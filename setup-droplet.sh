#!/bin/bash

# Digital Ocean Droplet Setup Script for Auto-Ops-AI
# Run this on your newly created Ubuntu 22.04 droplet
# Usage: bash setup-droplet.sh

set -e

echo "=========================================="
echo "Auto-Ops-AI Digital Ocean Setup"
echo "=========================================="

# Update system
echo "[1/6] Updating system packages..."
apt update && apt upgrade -y

# Install Docker
echo "[2/6] Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker root

# Install Docker Compose
echo "[3/6] Installing Docker Compose..."
apt install -y docker-compose-plugin
ln -s /usr/libexec/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose || true

# Install Git
echo "[4/6] Installing Git..."
apt install -y git

# Install Nginx (for reverse proxy and SSL)
echo "[5/6] Installing Nginx and SSL support..."
apt install -y nginx certbot python3-certbot-nginx

# Create app directory
echo "[6/6] Setting up application directory..."
mkdir -p /app
cd /app

# Clone repository
echo "Cloning repository..."
if [ -d ".git" ]; then
  git pull origin main
else
  git clone https://github.com/gimhanadeshan/auto-ops-ai.git .
fi

# Create environment file template
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create backend/.env file:"
echo "   nano backend/.env"
echo ""
echo "2. Add required environment variables:"
echo "   GOOGLE_API_KEY=your_key_here"
echo "   DATABASE_URL=sqlite:///./data/app.db"
echo "   SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "   ENVIRONMENT=production"
echo ""
echo "3. Initialize database:"
echo "   docker-compose -f docker-compose.prod.yml --profile init up"
echo ""
echo "4. Start application:"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "5. Setup SSL certificate (optional):"
echo "   certbot certonly --standalone -d your-domain.com"
echo ""
echo "6. Configure Nginx:"
echo "   nano /etc/nginx/sites-available/default"
echo ""
echo "For full guide, see: docs/DEPLOYMENT_GUIDE.md"
echo ""
