# Deployment Guide - Auto-Ops-AI

## Quick Deployment Options

### Option 1: Local Development (Fastest)

```powershell
# Windows PowerShell
.\setup.ps1
notepad backend\.env  # Add your GOOGLE_API_KEY
cd backend
uvicorn app.main:app --reload
```

### Option 2: Docker Compose (Recommended for Production)

```bash
# 1. Configure environment
cp backend/.env.example backend/.env
nano backend/.env  # Add your API keys

# 2. Build and run
docker-compose up --build -d

# 3. View logs
docker-compose logs -f backend

# 4. Access
# API: http://localhost:8000/docs
```

### Option 3: Manual Docker Build

```bash
docker build -t auto-ops-ai:latest .
docker run -d \
  -p 8000:8000 \
  --env-file backend/.env \
  --name auto-ops-ai \
  auto-ops-ai:latest
```

## Configuration Checklist

### 1. Get API Keys

**Google Gemini (Recommended):**
- Visit: https://makersuite.google.com/app/apikey
- Create API key
- Free tier available

**OpenAI (Alternative):**
- Visit: https://platform.openai.com/api-keys
- Create API key
- Paid service

### 2. Configure Environment

Edit `backend/.env`:

```env
# Choose your provider
LLM_PROVIDER=gemini  # or 'openai'
EMBEDDING_PROVIDER=gemini

# Add your API key
GOOGLE_API_KEY=AIza...  # Your actual key

# Or for OpenAI
# OPENAI_API_KEY=sk-...

# Database (default is fine)
DATABASE_URL=sqlite:///./data/processed/auto_ops.db

# Logging
LOG_LEVEL=INFO
```

### 3. Prepare Data (Optional)

Place your ticketing data JSON in:
```
data/raw/ticketing_system_data_new.json
```

Format:
```json
[
  {
    "id": "TICKET-001",
    "title": "VPN Connection Failed",
    "description": "Cannot connect to VPN",
    "status": "resolved",
    "priority": "high",
    "category": "system_issue",
    "resolution": "Reset VPN client configuration"
  }
]
```

## Testing the Deployment

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "auto-ops-ai-backend"
}
```

### 2. Create a Test Ticket

```bash
curl -X POST http://localhost:8000/api/v1/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Laptop Running Slow",
    "description": "My laptop has been very slow for the past hour",
    "user_email": "test@example.com"
  }'
```

### 3. Chat with AI

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "My computer is slow"}
    ],
    "user_email": "test@example.com"
  }'
```

### 4. View Dashboard

```bash
curl http://localhost:8000/api/v1/dashboard/overview
```

## Troubleshooting

### Issue: "Failed to initialize embeddings"

**Solution:**
1. Check your API key in `.env`
2. Verify LLM_PROVIDER is set correctly
3. For Gemini: Ensure key starts with `AIza`
4. For OpenAI: Ensure key starts with `sk-`

### Issue: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Database locked"

**Solution:**
```bash
# Stop the server
# Delete the database
rm data/processed/auto_ops.db
# Restart - it will recreate
```

### Issue: Docker port already in use

**Solution:**
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Issue: Logs directory permission denied

**Solution:**
```bash
mkdir -p logs
chmod 777 logs
```

## Production Considerations

### 1. Environment Variables

```env
# Production settings
DEBUG=False
LOG_LEVEL=WARNING

# Strong secret key
SECRET_KEY=generate-a-strong-random-secret-key

# CORS - restrict origins
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. Database

Consider switching from SQLite to PostgreSQL:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/autoops
```

Update docker-compose.yml:
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: autoops
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### 3. Security

- Use HTTPS/TLS in production
- Enable authentication
- Rotate API keys regularly
- Limit API rate limiting
- Regular security audits

### 4. Monitoring

Add health check endpoint monitoring:
```bash
# Add to crontab
*/5 * * * * curl -f http://localhost:8000/health || alert
```

### 5. Backup

Backup database and vector store:
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz \
  data/processed/auto_ops.db \
  data/processed/chroma_db/
```

## Scaling

### Horizontal Scaling

Use load balancer with multiple instances:

```yaml
# docker-compose.yml
services:
  backend1:
    build: .
    ports: ["8001:8000"]
  
  backend2:
    build: .
    ports: ["8002:8000"]
  
  nginx:
    image: nginx
    ports: ["80:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Caching

Add Redis for caching:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

## Monitoring & Logs

### View Logs

```bash
# Docker
docker-compose logs -f backend

# Local
tail -f logs/auto_ops_ai.log
```

### Log Rotation

Logs automatically rotate at 10MB with 5 backups.

### Metrics

Access metrics:
```bash
curl http://localhost:8000/api/v1/dashboard/overview
```

## Update & Maintenance

### Update Code

```bash
git pull
docker-compose down
docker-compose up --build -d
```

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Database Migrations

```bash
# Future: When using Alembic
alembic upgrade head
```

## Support

For issues:
1. Check logs: `logs/auto_ops_ai.log`
2. Verify configuration: `backend/.env`
3. Test health endpoint: `/health`
4. Review API docs: `/docs`

## Rollback

If deployment fails:

```bash
# Docker
docker-compose down
git checkout previous-version
docker-compose up --build -d

# Local
git checkout previous-version
cd backend
uvicorn app.main:app --reload
```
