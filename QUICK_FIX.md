# Quick Fix for Production 404 Error

## The Problem
Your production server (138.68.228.105) is using OLD Docker images that don't have the ML models in the correct location.

## Why It Works Locally
Local development uses the files directly from your disk, which has the ML models in the right place.

## Why It Fails in Production
Production uses Docker containers built from old images that were created BEFORE you moved the ML models.

## The Fix (3 Steps)

### Step 1: SSH into Production Server
```bash
ssh root@138.68.228.105
```

### Step 2: Navigate to App Directory
```bash
cd /app
```

### Step 3: Run These Commands (Copy-Paste All Together)
```bash
git pull origin main && \
docker-compose -f docker-compose.deploy.yml down && \
docker rmi gimhanadeshan/auto-ops-ai-backend:latest && \
docker-compose -f docker-compose.deploy.yml build --no-cache backend && \
docker-compose -f docker-compose.deploy.yml up -d && \
sleep 10 && \
echo "Testing endpoint..." && \
curl http://localhost:8000/api/v1/analytics/sla-risk
```

### Expected Output
You should see JSON data with ticket information, not a 404 error.

## Verify It Works

### From Production Server:
```bash
curl http://localhost:8000/api/v1/analytics/sla-risk
```

### From Your Browser:
```
http://138.68.228.105:8000/api/v1/analytics/sla-risk
```

### In Frontend:
Open `http://138.68.228.105` → Go to Reports → Select "SLA Risk Analysis"

## If Still Getting 404

### Check Container Logs:
```bash
docker logs auto-ops-ai-backend --tail 50
```

Look for errors about:
- "Could not include analytics endpoint"
- "SLA service unavailable"
- Missing ML models

### Verify Models Inside Container:
```bash
docker exec auto-ops-ai-backend ls -la /app/app/models/ml/
```

You should see:
- sla_model.joblib
- category_encoder.joblib

### Check If Endpoint Is Registered:
```bash
curl http://localhost:8000/docs
```

Look for "/api/v1/analytics/sla-risk" in the API documentation.

## Why This Happens
Docker builds images as snapshots. When you change files on your disk, Docker doesn't automatically update the containers. You must:
1. Pull latest code
2. Rebuild the image
3. Restart the containers

That's what the commands above do!
