# Auto-Ops-AI Backend Setup Guide

Complete setup guide for deploying the Auto-Ops-AI backend system.

## Prerequisites

- Python 3.8 or higher
- Virtual environment (venv)
- Git (for cloning the repository)

## Quick Setup (Recommended)

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd auto-ops-ai
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy environment template
cp backend\.env.example backend\.env

# Edit backend\.env and add your API keys
# Required: GOOGLE_API_KEY (for LLM and embeddings)
# Optional: SECRET_KEY (auto-generated if not provided)
```

### 5. Run Backend Setup (ONE COMMAND!)
```bash
cd backend
python setup_backend.py
```

This script will automatically:
- ✅ Initialize database schema
- ✅ Run all migrations (assignments, categories, etc.)
- ✅ Create test users and support agents
- ✅ Ingest knowledge base into RAG database
- ✅ Verify setup completion

### 6. Start the Server
```bash
# Option 1: Direct uvicorn
cd backend
uvicorn app.main:app --reload

# Option 2: Use run script
# Windows
.\run.ps1

# Linux/Mac
./run.sh
```

### 7. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

## Test Credentials

After setup, you can login with:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@acme.com | admin123 |
| Support L1 | john.hardware@company.com | support123 |
| Support L2 | alex.software@company.com | support123 |
| Support L3 | priya.network@company.com | support123 |

## Manual Setup (If Automatic Fails)

If the automatic setup script fails, run these commands manually:

```bash
cd backend

# 1. Initialize database
python init_db.py

# 2. Run migrations
python migrate_add_assignment.py

# 3. Create test users
python test_assignment_setup.py

# 4. Ingest knowledge base
python ingestion_script.py
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── api/
│   │   ├── endpoints/       # API route handlers
│   │   └── deps.py          # Dependencies
│   ├── core/
│   │   ├── database.py      # Database connection
│   │   ├── security.py      # Authentication
│   │   └── logging_config.py
│   ├── models/              # SQLAlchemy & Pydantic models
│   ├── services/            # Business logic
│   │   ├── agents/          # LLM agents
│   │   ├── assignment_service.py
│   │   ├── ticket_service.py
│   │   └── ...
│   └── data/
│       └── ml/              # ML models
├── data/
│   ├── processed/
│   │   ├── auto_ops.db      # SQLite database
│   │   └── chroma_db/       # Vector database
│   └── raw/
│       └── ticketing_system_data_new.json
├── logs/                    # Application logs
├── setup_backend.py         # 🌟 ONE-COMMAND SETUP SCRIPT
├── init_db.py               # Database initialization
├── migrate_*.py             # Migration scripts
├── ingestion_script.py      # RAG data ingestion
└── requirements.txt         # Python dependencies
```

## Configuration Files

### backend/.env
```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (has defaults)
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./data/processed/auto_ops.db
EMBEDDING_MODEL=models/text-embedding-004
USE_LOCAL_EMBEDDINGS=true
```

## Features Included

### Smart Ticket Assignment
- LLM-powered assignment based on agent specializations
- Fallback to specialization-aware round-robin
- Workload balancing

### Knowledge Base System
- RAG (Retrieval-Augmented Generation) for fast ticket resolution
- Automatic KB article suggestions from resolved tickets
- Admin panel for KB management

### Multi-Agent System
- Conversation Agent: Handles user interactions
- Status Agent: Manages ticket lifecycle
- Assignment Agent: Assigns tickets to appropriate agents

### Role-Based Access Control
- Staff, Contractor, Manager, Support L1/L2/L3, IT Admin, System Admin
- Granular permissions for tickets, KB, users, system

## Troubleshooting

### Database Not Found
```bash
# Ensure you're in backend directory
cd backend

# Run init_db.py manually
python init_db.py
```

### RAG Ingestion Fails
```bash
# Check GOOGLE_API_KEY is set
# Or use local embeddings (free)
# Set in .env: USE_LOCAL_EMBEDDINGS=true

python ingestion_script.py
```

### Migration Errors
```bash
# Delete database and start fresh
rm data/processed/auto_ops.db
python setup_backend.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Development Workflow

### Adding New Migrations
1. Create migration file: `migrate_add_<feature>.py`
2. Add to `setup_backend.py` migrations list
3. Test migration: `python migrate_add_<feature>.py`
4. Run full setup: `python setup_backend.py`

### Updating Knowledge Base
```bash
# Edit data/raw/ticketing_system_data_new.json
# Re-run ingestion
cd backend
python ingestion_script.py
```

### Testing
```bash
# Run specific test
python test_assignment_setup.py

# Check database contents
python -c "from app.core.database import SessionLocal; from app.models.user import UserDB; db = SessionLocal(); print(f'Users: {db.query(UserDB).count()}'); db.close()"
```

## API Endpoints

### Authentication
- `POST /api/v1/login` - User login
- `POST /api/v1/register` - User registration

### Tickets
- `GET /api/v1/tickets` - List all tickets
- `POST /api/v1/tickets` - Create ticket
- `GET /api/v1/tickets/{id}` - Get ticket details
- `PATCH /api/v1/tickets/{id}` - Update ticket

### Chat
- `POST /api/chat` - Send message (with auto-assignment)
- `GET /api/chat/history` - Get chat history

### Admin
- `GET /api/v1/users` - List users (admin)
- `POST /api/v1/users` - Create user (admin)
- `GET /api/v1/audit-logs` - View audit logs (admin)

## Support

For issues or questions:
1. Check logs in `backend/logs/`
2. Review API documentation at http://localhost:8000/docs
3. Ensure all migrations ran successfully
4. Verify .env configuration

## License

[Your License Here]
