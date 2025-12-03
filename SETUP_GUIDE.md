# Setup Guide - Auto-Ops-AI 🚀

## Prerequisites

Before setting up Auto-Ops-AI, ensure you have:

- **Python 3.11** or higher ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and npm ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Google Gemini API Key** ([Get one free](https://makersuite.google.com/app/apikey))

---

## Quick Setup (5 Minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/gimhanadeshan/auto-ops-ai.git
cd auto-ops-ai
```

### Step 2: Backend Setup

```bash
# Navigate to project root
cd auto-ops-ai

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Windows CMD:
.\venv\Scripts\activate.bat

# On Linux/Mac:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the `backend` folder:

```bash
cd backend
# Create .env file
```

**backend/.env** content:
```env
# Google Gemini API Key (REQUIRED)
GOOGLE_API_KEY=your_gemini_api_key_here

# JWT Secret Key (Change in production!)
SECRET_KEY=your-super-secret-jwt-key-change-in-production-min-32-chars

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings (Frontend URL)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-1.5-pro
EMBEDDING_PROVIDER=gemini
```

**⚠️ IMPORTANT**: Replace `your_gemini_api_key_here` with your actual API key!

### Step 4: Initialize Database

The database will be created automatically on first run, but you can verify the directory exists:

```bash
# From backend folder
mkdir -p data/processed
mkdir -p data/raw
```

### Step 5: Start Backend Server

```bash
# From backend folder
python -m uvicorn app.main:app --reload

# Or use the convenience script:
# Windows PowerShell:
.\run.ps1

# Linux/Mac:
./run.sh
```

**Backend will be available at**: http://127.0.0.1:8000

**Verify**: Visit http://127.0.0.1:8000/docs to see API documentation

### Step 6: Frontend Setup

Open a **new terminal** (keep backend running):

```bash
# Navigate to frontend folder
cd frontend

# Install npm dependencies
npm install

# Start development server
npm start
```

**Frontend will be available at**: http://localhost:5173

---

## Detailed Configuration

### Google Gemini API Key Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **"Get API Key"** or **"Create API Key"**
3. Select or create a Google Cloud project
4. Copy the generated API key
5. Paste it in `backend/.env` as `GOOGLE_API_KEY=`

**Note**: The free tier includes:
- 60 requests per minute
- 1,500 requests per day
- Sufficient for development and demos

### Database Configuration

**Default**: SQLite database stored at `backend/data/processed/auto_ops.db`

**For Production**: Replace SQLite with PostgreSQL:

```env
# backend/.env (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/auto_ops_db
```

Update `backend/app/core/database.py`:
```python
# Change from SQLite to PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/processed/auto_ops.db"
)
```

### Dataset Configuration

The historical ticket dataset is located at:
```
backend/data/raw/ticketing_system_data_new.json
```

**Contains**:
- 2,083 historical tickets
- 84 users with tiers (staff, manager, contractor)
- 50+ knowledge base articles with resolution steps

**No configuration needed** - the system auto-loads this on startup.

### CORS Configuration

If running frontend on a different port, update `backend/.env`:

```env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://your-domain.com
```

### Port Configuration

**Backend Port** (default 8000):
```bash
# To change port, edit run.ps1 or run command:
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

**Frontend Port** (default 5173):
```bash
# Edit frontend/vite.config.js:
export default defineConfig({
  server: {
    port: 3000  // Change to desired port
  }
})
```

---

## Verification Steps

### 1. Check Backend is Running

```bash
# Test health endpoint
curl http://127.0.0.1:8000/health

# Expected response:
# {"status":"healthy","service":"auto-ops-ai-backend"}
```

### 2. Check API Documentation

Visit: http://127.0.0.1:8000/docs

You should see:
- 📗 Authentication endpoints (/register, /login)
- 💬 Chat endpoint (/chat)
- 🎫 Ticket endpoints (/tickets)
- 📊 Dashboard endpoints

### 3. Check Frontend is Running

Visit: http://localhost:5173

You should see:
- Login page (if not authenticated)
- Beautiful purple gradient theme
- "Auto-Ops-AI" branding

### 4. Test Registration

1. Go to http://localhost:5173/register
2. Fill in:
   - Name: Test User
   - Email: test@example.com
   - Password: test123
   - Tier: Staff
3. Click "Register"
4. Should redirect to login page

### 5. Test Login

1. Login with test@example.com / test123
2. Should redirect to chat interface
3. User badge should show "Test User (staff)"

### 6. Test Chat Flow

1. Type: `Hi`
2. Bot should greet you
3. Type: `My VPN is not connecting`
4. Bot should ask diagnostic questions
5. Answer the questions
6. Bot should provide troubleshooting steps

---

## Common Setup Issues

### Issue 1: "ModuleNotFoundError: No module named 'app'"

**Solution**: Run commands from the `backend` folder:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Issue 2: "google.api_core.exceptions.PermissionDenied: API key not valid"

**Solution**: 
1. Check your Google API key is correct in `.env`
2. Enable Gemini API in Google Cloud Console
3. Verify the key has permissions for Generative AI

### Issue 3: "Could not include auth endpoint at startup: email-validator is not installed"

**Solution**:
```bash
pip install email-validator
```

### Issue 4: "passlib.exc.UnknownHashError" or bcrypt errors

**Solution**:
```bash
pip uninstall bcrypt passlib -y
pip install bcrypt==4.0.1 passlib[bcrypt]
```

### Issue 5: Frontend shows "Failed to fetch" or CORS errors

**Solution**:
1. Check backend is running at http://127.0.0.1:8000
2. Verify CORS settings in `backend/.env`:
   ```env
   ALLOWED_ORIGINS=http://localhost:5173
   ```
3. Restart backend after changing `.env`

### Issue 6: Database errors on startup

**Solution**:
```bash
# Delete existing database
rm backend/data/processed/auto_ops.db

# Restart backend (will recreate database)
cd backend
python -m uvicorn app.main:app --reload
```

### Issue 7: "npm: command not found"

**Solution**: Install Node.js from https://nodejs.org/ (LTS version recommended)

---

## Production Deployment

### Backend Deployment (Docker)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t auto-ops-ai-backend .
docker run -p 8000:8000 --env-file backend/.env auto-ops-ai-backend
```

### Frontend Deployment (Vercel/Netlify)

1. Build frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy `dist/` folder to:
   - **Vercel**: `vercel deploy`
   - **Netlify**: `netlify deploy --prod`

3. Update backend CORS to include production URL:
   ```env
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

### Environment Variables for Production

```env
# backend/.env (Production)
GOOGLE_API_KEY=your_production_api_key
SECRET_KEY=generate-strong-32-char-random-key-here
ALLOWED_ORIGINS=https://your-frontend-domain.com
DATABASE_URL=postgresql://user:pass@db-host:5432/dbname
```

**Generate strong secret key**:
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Architecture Overview

```
auto-ops-ai/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/endpoints/  # API routes (chat, auth, tickets)
│   │   ├── models/         # Database & Pydantic models
│   │   ├── services/       # Business logic
│   │   │   └── agents/     # AI conversation agents
│   │   ├── core/           # Database, logging, security
│   │   ├── config.py       # Configuration settings
│   │   └── main.py         # FastAPI app entry point
│   ├── data/
│   │   ├── raw/            # Dataset JSON file
│   │   └── processed/      # SQLite database
│   ├── .env                # Environment variables (create this!)
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components (Login, Register, TicketList)
│   │   ├── App.jsx         # Main app with routing
│   │   └── api.js          # Backend API calls
│   ├── package.json        # npm dependencies
│   └── vite.config.js      # Vite configuration
│
└── README.md               # Project overview
```

---

## Development Tips

### Enable Hot Reload

Backend auto-reloads when using `--reload` flag:
```bash
uvicorn app.main:app --reload
```

Frontend auto-reloads with Vite dev server (automatic).

### View Logs

**Backend logs**: Printed to console where uvicorn is running

**Frontend logs**: Browser console (F12 → Console tab)

### Debug API Requests

Use the interactive API docs:
- http://127.0.0.1:8000/docs (Swagger UI)
- http://127.0.0.1:8000/redoc (ReDoc)

### Test Embeddings

```bash
cd backend
python test_embeddings.py
```

### Access Database

```bash
# Install SQLite browser (optional)
# Or use Python:
cd backend
python

>>> from app.core.database import SessionLocal
>>> from app.models.user import UserDB
>>> db = SessionLocal()
>>> users = db.query(UserDB).all()
>>> for u in users:
...     print(f"{u.email} - {u.tier}")
```

---

## Next Steps

1. ✅ Complete setup using this guide
2. ✅ Test sample questions from `TESTING_GUIDE.md`
3. ✅ Customize for your use case (edit categories, KB articles, etc.)
4. ✅ Deploy to production
5. ✅ Monitor and improve based on user feedback

---

## Support & Resources

**Documentation**:
- README.md - Project overview
- TESTING_GUIDE.md - Test scenarios
- HACKATHON_DEMO.md - Feature showcase
- API Docs: http://127.0.0.1:8000/docs

**Troubleshooting**:
- Check backend logs for errors
- Verify `.env` file exists and has correct API key
- Ensure all dependencies installed (`pip list`, `npm list`)

**Tech Stack**:
- Backend: FastAPI, SQLAlchemy, Google Gemini API
- Frontend: React, Vite, React Router
- Database: SQLite (dev), PostgreSQL (prod)
- AI: Gemini 1.5 Pro + Text Embedding 004

---

## Quick Reference

```bash
# Start backend
cd backend
.\venv\Scripts\Activate.ps1  # Windows
python -m uvicorn app.main:app --reload

# Start frontend
cd frontend
npm start

# Run tests
cd backend
python test_embeddings.py

# Check health
curl http://127.0.0.1:8000/health
```

**URLs**:
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs
- Frontend: http://localhost:5173

---

**🎉 You're all set! Start the servers and begin testing!**
