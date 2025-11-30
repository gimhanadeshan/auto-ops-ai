#  Auto-Ops-AI - Intelligent IT Support & Troubleshooting System

> **Hackathon Project**: AI-powered system for automated IT support ticket handling, troubleshooting, and resolution

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-orange.svg)](https://langchain.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

##  Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Safety & Security](#safety--security)
- [Docker Deployment](#docker-deployment)
- [Development](#development)

##  Overview

Auto-Ops-AI is an intelligent IT support system that automates the handling of both **user-reported complaints** and **system-generated issues**. It uses AI agents powered by **Google Gemini** (default) or **OpenAI** to:

-  Automatically triage and classify support tickets
-  Provide intelligent troubleshooting steps
-  Offer an interactive AI chatbot for user support
-  Run safe diagnostic operations
-  Generate analytics and insights
-  Maintain complete audit logs

### Problem Statement

Modern organizations handle two types of IT issues:

**User-Reported Issues:**
- "My laptop is very slow"
- "Can''t connect to VPN"
- "Android Studio keeps crashing"
- "Printer not working"

**System-Generated Issues** (Optional):
- Server down alerts
- High CPU/RAM usage
- Service not responding
- Backup failures
- Network connectivity errors

Auto-Ops-AI automates the diagnosis, troubleshooting, and resolution of these issues while maintaining strict **privacy, security, and safety** controls.

##  Features

### Core Features
-  **AI-Powered Triage Agent** - Automatically classifies issues as User Error vs System Issue
-  **Intelligent Troubleshooter** - Generates step-by-step diagnostic procedures
-  **Interactive Chat Support** - AI chatbot for real-time user assistance
-  **Analytics Dashboard** - Comprehensive metrics and insights
-  **Safe Mode Operations** - All system actions are simulated/mocked
-  **RAG Knowledge Base** - Semantic search through historical tickets
-  **Priority Assignment** - Automatic priority levels (Low/Medium/High/Critical)
-  **Audit Logging** - Complete trail of all actions

### AI Capabilities
- Multi-provider LLM support (Google Gemini / OpenAI)
- Context-aware responses using RAG
- Confidence scoring for classifications
- Smart escalation logic
- Pattern recognition from historical data

### Safety & Security
-  No destructive OS commands
-  Sandboxed/simulated operations
-  User confirmation for sensitive actions
-  Anonymized logs
-  No credential storage
-  Complete audit trail

##  Quick Start

### Prerequisites
- **Python 3.11+** (3.12 recommended - 3.14 has limited package support)
- Google Gemini API key (or OpenAI API key)
- 4GB RAM minimum

### 1️⃣ Setup (One-time)

#### Windows (PowerShell)
```powershell
.\setup.ps1
```

#### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

**What the setup does:**
- Creates Python virtual environment
- Installs all dependencies
- Creates necessary directories
- Sets up database

### 2️⃣ Configure API Keys

Edit `backend\.env` and add your API key:

**Option A: Google Gemini (Recommended)**
```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-key-here
```

**Option B: OpenAI**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here
```

Get free API keys:
- 🔗 [Google Gemini](https://makersuite.google.com/app/apikey)
- 🔗 [OpenAI](https://platform.openai.com/api-keys)

### 3️⃣ Start the Server

#### Windows (Easiest)
```powershell
.\run.ps1
```

#### Windows (Command Prompt)
```cmd
run.bat
```

#### Linux/Mac
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### ✅ Access the Application

Server will start at **http://127.0.0.1:8000**

- 📖 **Interactive API Docs**: http://127.0.0.1:8000/docs
- 📚 **Alternative Docs**: http://127.0.0.1:8000/redoc
- 🏥 **Health Check**: http://127.0.0.1:8000/health

### 4️⃣ Run the Frontend (React + Vite)

The repository includes a lightweight React + Vite frontend in the `frontend/` folder. During local development point the frontend to the backend API at `http://127.0.0.1:8000/api/v1` (this is the default used by the example `.env` file in `frontend/`).

Windows (PowerShell):
```powershell
cd frontend
npm install
npm run dev
```

Linux / Mac:
```bash
cd frontend
npm install
npm run dev
```

After Vite starts, open the URL printed by the dev server (commonly `http://localhost:5173`). The frontend will call the backend at the base URL configured in `frontend/.env` (variable `VITE_API_BASE_URL`).

If the browser blocks requests with a CORS error ("No 'Access-Control-Allow-Origin' header"), make sure the backend `ALLOWED_ORIGINS` setting includes your Vite origin (for example `http://localhost:5173`). See the `Configuration` section below for details.

Notes:
- The frontend's dev server supports HMR (hot module replacement) — changes to `src/` files will update in the browser automatically.
- The frontend reads API base URL from `frontend/.env` (`VITE_API_BASE_URL`). Example:
   ```env

##  API Documentation

### Chat Endpoints
```http
POST /api/v1/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "My laptop is slow"}
  ],
  "user_email": "user@example.com"
}
```

### Create Ticket (Auto-Triage)
```http
POST /api/v1/tickets
Content-Type: application/json

{
  "title": "VPN Connection Failed",
  "description": "Cannot connect to company VPN",
  "user_email": "user@example.com"
}
```

### Get Dashboard Metrics
```http
GET /api/v1/dashboard/overview
```

For complete API documentation, visit `/docs` when server is running.

##  Configuration

### Environment Variables

Edit `backend/.env`:

```env
# LLM Provider (gemini or openai)
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini

# Google Gemini (Default - Recommended)
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
EMBEDDING_MODEL=models/text-embedding-004

# OpenAI (Alternative)
OPENAI_API_KEY=your-openai-key-here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Database
DATABASE_URL=sqlite:///./data/processed/auto_ops.db
CHROMA_PERSIST_DIRECTORY=./data/processed/chroma_db

# Logging
LOG_LEVEL=INFO
DEBUG=True
```

### Getting API Keys

**Google Gemini (Recommended - Free Tier Available):**
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add to `.env` as `GOOGLE_API_KEY`

**OpenAI (Alternative):**
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env` as `OPENAI_API_KEY`

##  Safety & Security

### Safe Mode Operations

All system operations are **mocked/simulated**:
-  System status checks (simulated)
-  Log file reading (simulated)
-  Service restarts (simulated)
-  Disk space checks (simulated)
-  Network diagnostics (simulated)

### Data Privacy
- No personal data collected unnecessarily
- Logs are anonymized
- Credentials never stored
- Synthetic/mock data for testing

### Access Control
- JWT-based authentication
- Role-based permissions
- Complete audit trail
- User confirmation for actions

##  Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t auto-ops-ai .

# Run container
docker run -p 8000:8000 --env-file backend/.env auto-ops-ai
```

##  Development

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Running Tests

```bash
cd backend
pytest
```

### Code Style

```bash
# Format code
black backend/

# Lint
flake8 backend/
```

### Project Structure Best Practices

-  Modular architecture with clear separation of concerns
-  Dependency injection for testability
-  Environment-based configuration
-  Centralized logging
-  Type hints throughout
-  Comprehensive error handling
-  Docker-ready deployment

##  Supported Issue Types

### User-Reported Issues 
- Application crashes
- Performance issues
- Connectivity problems
- Software errors
- Login/authentication issues
- Hardware problems

### System-Generated Issues  (Optional - Higher Marks)
- High resource usage
- Service failures
- Network errors
- Database issues
- Application crash logs
- Backup failures

##  Hackathon Evaluation Criteria

| Criteria | Implementation |
|----------|---------------|
| **Innovation** |  Multi-provider LLM, RAG-based context |
| **Technical Depth** |  Clean architecture, modular design |
| **Accuracy** |  AI-powered classification with confidence |
| **Safety** |  Complete safe mode, audit logging |
| **User Experience** |  Interactive chat, clear API docs |
| **Completeness** |  Full ticket lifecycle, analytics |
| **Documentation** |  Comprehensive docs, architecture diagrams |

##  Deliverables

-  Working prototype (FastAPI backend)
-  Architecture diagram (see ARCHITECTURE.md)
-  List of supported issues
-  Sample logs and data
-  Complete documentation
-  Docker deployment
-  Safety rules implementation
-  Audit logging

##  Bonus Features Implemented

-  Multi-provider LLM support (Gemini + OpenAI)
-  RAG-based knowledge retrieval
-  Smart escalation logic
-  Comprehensive audit logging
-  Docker deployment
-  API documentation (Swagger/ReDoc)
-  Modular, production-ready code

##  Future Roadmap

- [ ] Frontend UI (React/Next.js)
- [ ] Slack/Teams integration
- [ ] Voice input support
- [ ] Email ticket creation
- [ ] Real system integrations (with proper auth)
- [ ] Predictive issue detection
- [ ] Multi-tenancy support
- [ ] Advanced ML models

##  License

MIT License - See LICENSE file for details

##  Contributing

Contributions welcome! Please open an issue or PR.

##  Authors

Auto-Ops-AI Hackathon Team

##  Support

For issues or questions:
- Check `/docs` for API documentation
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Review logs in `logs/` directory

---
