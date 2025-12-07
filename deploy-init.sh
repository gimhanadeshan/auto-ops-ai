#!/bin/bash

# Auto-Ops-AI Deployment Initialization Script
# Run on the droplet after docker-compose up -d

set -e

echo "======================================"
echo "Auto-Ops-AI Deployment Initialization"
echo "======================================"

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 20

# Initialize database
echo "📦 Initializing database..."
docker-compose -f docker-compose.deploy.yml exec -T backend python backend/init_db.py

# Load seed data / run ingestion
echo "🌱 Loading seed data..."
docker-compose -f docker-compose.deploy.yml exec -T backend python backend/ingestion_script.py || true

# Train model (if needed)
echo "🤖 Training ML model..."
docker-compose -f docker-compose.deploy.yml exec -T backend python backend/train_model.py || true

echo ""
echo "======================================"
echo "✅ Initialization Complete!"
echo "======================================"
echo ""
echo "Your application is ready at:"
echo "  Frontend: http://$(hostname -I | awk '{print $1}'):80"
echo "  Backend:  http://$(hostname -I | awk '{print $1}'):8000"
echo ""
