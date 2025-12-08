# 🚀 Quick Start Guide - Auto-Ops-AI

## For New Users (First Time Setup)

### 1. Clone Repository
```bash
git clone <repository-url>
cd auto-ops-ai
```

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install all packages
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy template
copy backend\.env.example backend\.env

# Edit backend\.env and add:
# GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Setup Backend (ONE COMMAND)
```bash
cd backend
python setup_backend.py
```

This will automatically:
- ✅ Check dependencies
- ✅ Initialize database
- ✅ Run all migrations
- ✅ Create test users
- ✅ Ingest knowledge base

### 5. Start Backend
```bash
# From backend directory
uvicorn app.main:app --reload
```

### 6. Start Frontend (New Terminal)
```bash
# From project root
cd frontend
npm install
npm run dev
```

### 7. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs
- **Login**: admin@acme.com / admin123

---

## For Existing Users (Already Setup)

### Just Run Servers

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

---

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Backend won't start
```bash
cd backend
python setup_backend.py
```

### Frontend errors
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Database issues
```bash
cd backend
rm data/processed/auto_ops.db
python setup_backend.py
```

---

## What's Included After Setup

✅ **Database with Test Data:**
- Admin user (admin@acme.com / admin123)
- 3 Support agents (john, alex, priya)
- Sample tickets and history

✅ **Knowledge Base (RAG):**
- 6 pre-configured KB articles
- Vector database ready for similarity search

✅ **Smart Features:**
- LLM-powered ticket assignment
- Specialization-based routing
- Multi-agent conversation system
- Role-based access control

---

## Project Structure

```
auto-ops-ai/
├── backend/
│   ├── setup_backend.py  ← 🌟 RUN THIS FIRST
│   ├── app/              ← FastAPI application
│   ├── data/             ← Database & RAG
│   └── ...
├── frontend/
│   ├── src/              ← React components
│   └── package.json
├── requirements.txt      ← Python packages
└── README.md
```

---

## Next Steps

1. Explore the API: http://localhost:8000/docs
2. Try creating a ticket via chat
3. Check smart assignment in action
4. Review admin panel features

For detailed documentation, see:
- [BACKEND_SETUP.md](BACKEND_SETUP.md) - Complete backend guide
- [README.md](README.md) - Full project documentation
