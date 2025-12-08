#!/bin/bash
# Run this script on your production server (138.68.228.105)
# Usage: ssh root@138.68.228.105 'bash -s' < DEPLOY_TO_PRODUCTION.sh

set -e

echo "=================================="
echo "🚀 Deploying ML Model Updates"
echo "=================================="

cd /app

echo ""
echo "1️⃣ Pulling latest code from main branch..."
git pull origin main

echo ""
echo "2️⃣ Checking if ML models exist in repository..."
if [ -f "backend/app/models/ml/sla_model.joblib" ]; then
    echo "✅ sla_model.joblib found"
else
    echo "❌ ERROR: sla_model.joblib NOT found in repository!"
    exit 1
fi

if [ -f "backend/app/models/ml/category_encoder.joblib" ]; then
    echo "✅ category_encoder.joblib found"
else
    echo "❌ ERROR: category_encoder.joblib NOT found in repository!"
    exit 1
fi

echo ""
echo "3️⃣ Stopping running containers..."
docker-compose -f docker-compose.deploy.yml down

echo ""
echo "4️⃣ Removing old backend image to force rebuild..."
docker rmi ${DOCKER_HUB_USERNAME:-gimhanadeshan}/auto-ops-ai-backend:latest || echo "Image not found, continuing..."

echo ""
echo "5️⃣ Building new backend image with ML models..."
docker-compose -f docker-compose.deploy.yml build --no-cache backend

echo ""
echo "6️⃣ Starting services..."
docker-compose -f docker-compose.deploy.yml up -d

echo ""
echo "7️⃣ Waiting for services to start..."
sleep 10

echo ""
echo "8️⃣ Checking backend container logs..."
docker logs auto-ops-ai-backend --tail 20

echo ""
echo "9️⃣ Verifying ML models inside container..."
docker exec auto-ops-ai-backend ls -la /app/app/models/ml/ || echo "Could not list models directory"

echo ""
echo "🔟 Testing analytics endpoint..."
sleep 5
curl -s http://localhost:8000/api/v1/analytics/sla-risk | head -100

echo ""
echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
echo ""
echo "Test the endpoint from your browser:"
echo "http://138.68.228.105:8000/api/v1/analytics/sla-risk"
echo ""
echo "Check frontend SLA report:"
echo "http://138.68.228.105 → Reports → SLA Risk Analysis"
