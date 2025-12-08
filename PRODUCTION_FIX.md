# Production Analytics Endpoint 404 Fix

## Problem
The `/api/v1/analytics/sla-risk` endpoint returns **404 in production** but **200 OK locally**.

## Root Cause
The production Docker images were built **before** the ML models were moved to their correct location (`backend/app/models/ml/`). The old images either:
1. Don't have the ML models in the correct path
2. Have outdated Python dependencies (scikit-learn version mismatch)
3. Weren't rebuilt after the file structure changes

## Solution Steps

### Step 1: Verify Local Setup (Already Done ✅)
```bash
# All ML models are in correct location
backend/app/models/ml/
  ├── sla_model.joblib
  ├── category_encoder.joblib
  └── system_health_model.joblib

backend/app/data/ml/
  └── sla_training_data.csv
```

### Step 2: Verify Git Repository
```bash
# Check files are committed
git ls-files | grep "backend/app/models/ml"
git ls-files | grep "backend/app/data/ml"

# Check latest commits
git log --oneline -5
```

**Expected:** Latest commit `e2db2ec` includes ML model updates.

### Step 3: Push Changes to GitHub
```bash
# If there are uncommitted changes
git add .
git commit -m "Fix: Ensure ML models in production-ready structure"
git push origin integration-v4
```

### Step 4: SSH into Production Server
```bash
ssh root@138.68.228.105
```

### Step 5: Navigate to App Directory
```bash
cd /app
```

### Step 6: Pull Latest Code
```bash
git fetch origin integration-v4
git reset --hard origin/integration-v4
```

### Step 7: Verify ML Models Exist
```bash
# Check if models are in the repo
ls -la backend/app/models/ml/
ls -la backend/app/data/ml/

# Should show:
# backend/app/models/ml/category_encoder.joblib
# backend/app/models/ml/sla_model.joblib
# backend/app/data/ml/sla_training_data.csv
```

### Step 8: Stop Running Containers
```bash
docker-compose -f docker-compose.deploy.yml down
```

### Step 9: Remove Old Images (Force Rebuild)
```bash
# Remove old backend image
docker rmi ${DOCKER_HUB_USERNAME}/auto-ops-ai-backend:latest

# Or remove all unused images
docker image prune -a -f
```

### Step 10: Rebuild and Start Services
```bash
# Option A: Use deploy script (recommended)
./deploy.sh

# Option B: Manual rebuild
docker-compose -f docker-compose.deploy.yml build --no-cache backend
docker-compose -f docker-compose.deploy.yml up -d
```

### Step 11: Verify Container Has Models
```bash
# Check if models are inside the running container
docker exec auto-ops-ai-backend ls -la /app/app/models/ml/

# Should output:
# category_encoder.joblib
# sla_model.joblib
```

### Step 12: Check Container Logs
```bash
docker logs auto-ops-ai-backend --tail 100

# Look for:
# ✅ "Auto-Ops-AI Backend is ready!"
# ❌ Any errors loading ML models
# ❌ Any warnings about missing analytics endpoint
```

### Step 13: Run Verification Script Inside Container
```bash
# Copy verification script into container
docker cp verify_ml_models.py auto-ops-ai-backend:/app/

# Run it inside the container
docker exec auto-ops-ai-backend python verify_ml_models.py
```

### Step 14: Test Analytics Endpoint
```bash
# From production server
curl http://localhost:8000/api/v1/analytics/sla-risk

# From your local machine
curl http://138.68.228.105:8000/api/v1/analytics/sla-risk

# Should return JSON array of tickets with SLA predictions
```

### Step 15: Check Frontend
Open browser to: `http://138.68.228.105`
- Navigate to Reports → SLA Risk Analysis
- Should display table of tickets with SLA breach predictions

## Troubleshooting

### Issue: Models Not Found in Container
**Symptoms:** Verification script shows "ML models directory NOT found"

**Solution:**
```bash
# Check Dockerfile includes COPY command
cat Dockerfile | grep "COPY backend/app"

# Should see:
# COPY --chown=appuser:appuser backend/app /app/app

# Rebuild with verbose output
docker-compose -f docker-compose.deploy.yml build --no-cache --progress=plain backend
```

### Issue: scikit-learn Version Mismatch
**Symptoms:** Warnings about "InconsistentVersionWarning" in logs

**Solution:**
```bash
# Check requirements.txt has correct version
cat requirements.txt | grep scikit-learn

# Should show: scikit-learn==1.7.2

# If different, update requirements.txt and rebuild
echo "scikit-learn==1.7.2" >> requirements.txt
docker-compose -f docker-compose.deploy.yml build --no-cache backend
```

### Issue: Analytics Router Not Loading
**Symptoms:** 404 on analytics endpoint, logs show "Could not include analytics endpoint"

**Solution:**
```bash
# Check analytics endpoint imports
docker exec auto-ops-ai-backend python -c "from app.api.endpoints import analytics; print('Analytics OK')"

# Check SLA service imports
docker exec auto-ops-ai-backend python -c "from app.services.sla_service import sla_service; print('SLA Service OK')"

# If import fails, check error message for missing dependencies
docker exec auto-ops-ai-backend python -c "import joblib; import pandas; import sklearn; print('All deps OK')"
```

### Issue: Docker Hub Image Cache
**Symptoms:** Changes not reflected after rebuild

**Solution:**
```bash
# Login to Docker Hub
docker login

# Tag and push new image
docker tag auto-ops-ai-backend:latest ${DOCKER_HUB_USERNAME}/auto-ops-ai-backend:latest
docker push ${DOCKER_HUB_USERNAME}/auto-ops-ai-backend:latest

# Pull fresh image on production
docker pull ${DOCKER_HUB_USERNAME}/auto-ops-ai-backend:latest
docker-compose -f docker-compose.deploy.yml up -d
```

## Quick Fix Command
If you want to do everything in one go:
```bash
cd /app && \
git fetch origin integration-v4 && \
git reset --hard origin/integration-v4 && \
docker-compose -f docker-compose.deploy.yml down && \
docker rmi ${DOCKER_HUB_USERNAME}/auto-ops-ai-backend:latest || true && \
docker-compose -f docker-compose.deploy.yml build --no-cache backend && \
docker-compose -f docker-compose.deploy.yml up -d && \
sleep 10 && \
curl http://localhost:8000/api/v1/analytics/sla-risk
```

## Expected Result
After successful deployment:
- ✅ `curl http://138.68.228.105:8000/api/v1/analytics/sla-risk` returns JSON array
- ✅ Frontend SLA report displays table of tickets
- ✅ No 404 errors in browser console
- ✅ Container logs show "Auto-Ops-AI Backend is ready!"

## Files Changed
- `backend/app/models/ml/sla_model.joblib` - Moved from `app/models/ml/`
- `backend/app/models/ml/category_encoder.joblib` - Moved from `app/models/ml/`
- `backend/app/data/ml/sla_training_data.csv` - Moved from `app/data/ml/`
- `backend/app/services/sla_service.py` - Updated to use Path() for absolute paths
- `backend/app/api/endpoints/analytics.py` - Added error handling and fallback predictions
- `backend/app/main.py` - Added analytics to dynamic loading loop
- `Dockerfile` - Simplified to copy entire backend/app structure

## Contact
If issues persist, check:
1. GitHub Actions CI/CD logs
2. Docker Hub image build timestamps
3. Production server disk space: `df -h`
4. Docker system resources: `docker system df`
