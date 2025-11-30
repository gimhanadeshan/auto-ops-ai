# Auto-Ops-AI - Architecture Documentation

## System Overview

Auto-Ops-AI is an intelligent IT support system that automates ticket triage, troubleshooting, and resolution using AI agents powered by Google Gemini or OpenAI.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                             │
│  (Web UI / CLI / Chat Interface / Email / Voice)            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────┴──────────────────────────────────────┐
│                  FastAPI Application                         │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Chat      │  │   Tickets    │  │  Dashboard   │     │
│  │  Endpoint   │  │   Endpoint   │  │   Endpoint   │     │
│  └─────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│        │                  │                  │              │
│  ┌─────┴──────────────────┴──────────────────┴───────┐    │
│  │            Business Logic Layer                     │    │
│  │                                                      │    │
│  │  ┌────────────────┐      ┌────────────────┐       │    │
│  │  │  Triage Agent  │      │ Troubleshooter │       │    │
│  │  │                │      │     Agent      │       │    │
│  │  │ - Classify     │      │ - Diagnostics  │       │    │
│  │  │ - Prioritize   │      │ - Steps        │       │    │
│  │  │ - Assign       │      │ - Resolution   │       │    │
│  │  └────────┬───────┘      └────────┬───────┘       │    │
│  │           │                       │                │    │
│  │           └───────┬───────────────┘                │    │
│  │                   │                                │    │
│  │        ┌──────────┴──────────┐                    │    │
│  │        │    LLM Factory      │                    │    │
│  │        │                     │                    │    │
│  │        │ ┌─────────────────┐ │                    │    │
│  │        │ │ Google Gemini   │ │                    │    │
│  │        │ │   or OpenAI     │ │                    │    │
│  │        │ └─────────────────┘ │                    │    │
│  │        └─────────────────────┘                    │    │
│  │                                                     │    │
│  │  ┌────────────────┐      ┌────────────────┐      │    │
│  │  │   RAG Engine   │      │  Safe Tools    │      │    │
│  │  │                │      │                │      │    │
│  │  │ - ChromaDB     │      │ - Mock Ops     │      │    │
│  │  │ - Embeddings   │      │ - Diagnostics  │      │    │
│  │  │ - Search       │      │ - Audit Log    │      │    │
│  │  └────────┬───────┘      └────────────────┘      │    │
│  └───────────┼──────────────────────────────────────┘    │
└──────────────┼───────────────────────────────────────────┘
               │
┌──────────────┴───────────────────────────────────────────┐
│                   Data Layer                              │
│                                                           │
│  ┌───────────────┐   ┌──────────────┐   ┌────────────┐ │
│  │   SQLite DB   │   │  ChromaDB    │   │  Logs      │ │
│  │               │   │  Vector      │   │            │ │
│  │ - Tickets     │   │  Store       │   │ - Audit    │ │
│  │ - Users       │   │              │   │ - Actions  │ │
│  │ - History     │   │ - Embeddings │   │ - Errors   │ │
│  └───────────────┘   └──────────────┘   └────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Components

### 1. API Layer (`app/api/`)
- **chat.py**: AI chatbot endpoints
- **tickets.py**: Ticket CRUD operations
- **dashboard.py**: Analytics and metrics
- **deps.py**: Authentication and dependencies

### 2. Core Layer (`app/core/`)
- **database.py**: SQLAlchemy configuration
- **security.py**: JWT authentication
- **llm_factory.py**: LLM provider abstraction
- **logging_config.py**: Centralized logging

### 3. Models (`app/models/`)
- **ticket.py**: Ticket schemas and enums
- **user.py**: User authentication models

### 4. Services (`app/services/`)
- **rag_engine.py**: Vector search and retrieval
- **ticket_service.py**: Business logic for tickets
- **agents/**:
  - **triage_agent.py**: Classification and prioritization
  - **troubleshooter.py**: Diagnostic workflows
  - **tools.py**: Safe system operations

## Data Flow

### User Complaint Flow
```
User Input → Chat Endpoint → Triage Agent → RAG Search → 
→ LLM Analysis → Ticket Creation → Troubleshooter → 
→ Resolution Steps → User Response
```

### System Issue Flow (Optional)
```
System Logs → Issue Detection → Auto Ticket Creation → 
→ Triage Agent → Diagnostics → Safe Tools → 
→ Resolution/Escalation
```

## Safety & Security

### 1. Safe Mode Operations
- All system operations are mocked/simulated
- No destructive commands executed
- Actions logged in audit trail
- User confirmation required for sensitive ops

### 2. Data Privacy
- No personal data collected unnecessarily
- Logs anonymized
- Credentials never stored
- Environment variable management

### 3. Access Control
- JWT-based authentication
- Role-based permissions (admin/user)
- API rate limiting (future)
- Audit logging for all actions

## Supported Issue Types

### User-Reported Issues
- ✅ Application crashes
- ✅ Performance issues (slow PC)
- ✅ Connectivity problems (VPN, Wi-Fi)
- ✅ Software errors
- ✅ Login issues
- ✅ Printer problems

### System-Generated Issues (Optional)
- ⚠️ High CPU/RAM usage
- ⚠️ Low disk space
- ⚠️ Service failures
- ⚠️ Network errors
- ⚠️ Database connection issues
- ⚠️ Application crash logs

## AI Capabilities

### Triage Agent
- **Classification**: User Error vs System Issue
- **Priority Assignment**: Low/Medium/High/Critical
- **Team Routing**: Automatic assignment suggestions
- **Confidence Scoring**: Analysis reliability metrics

### Troubleshooter Agent
- **Diagnostic Steps**: Step-by-step instructions
- **Root Cause Analysis**: Pattern recognition
- **Resolution Suggestions**: Based on historical data
- **Automated Actions**: Safe operations only

### RAG Engine
- **Vector Search**: Semantic similarity search
- **Context Retrieval**: Relevant past tickets
- **Knowledge Base**: Historical resolution patterns
- **Embeddings**: Gemini or OpenAI

## Deployment

### Development
```bash
python setup.ps1  # Windows
./setup.sh        # Linux/Mac
cd backend
uvicorn app.main:app --reload
```

### Production (Docker)
```bash
docker-compose up --build -d
```

### Environment Configuration
- **LLM_PROVIDER**: `gemini` or `openai`
- **GOOGLE_API_KEY**: For Gemini
- **OPENAI_API_KEY**: For OpenAI
- **DATABASE_URL**: SQLite connection
- **LOG_LEVEL**: INFO/DEBUG/WARNING

## API Endpoints

### Health
- `GET /` - Root health check
- `GET /health` - Service status

### Chat
- `POST /api/v1/chat` - Interactive AI chat
- `POST /api/v1/chat/suggest-ticket` - Ticket suggestion

### Tickets
- `POST /api/v1/tickets` - Create ticket (auto-triage)
- `GET /api/v1/tickets` - List with filters
- `GET /api/v1/tickets/{id}` - Get ticket details
- `PUT /api/v1/tickets/{id}` - Update ticket
- `POST /api/v1/tickets/{id}/troubleshoot` - Run diagnostics
- `GET /api/v1/tickets/stats/summary` - Statistics

### Dashboard
- `GET /api/v1/dashboard/overview` - Metrics summary
- `GET /api/v1/dashboard/trends` - Time-series data
- `GET /api/v1/dashboard/category-breakdown` - Category stats
- `GET /api/v1/dashboard/priority-distribution` - Priority stats
- `GET /api/v1/dashboard/response-time` - Performance metrics

## Future Enhancements

- [ ] Real system integrations (with proper auth)
- [ ] Predictive issue detection
- [ ] Multi-tenancy support
- [ ] Slack/Teams integration
- [ ] Voice input processing
- [ ] Email ticket creation
- [ ] Advanced analytics dashboard
- [ ] Machine learning model training
- [ ] Cross-platform troubleshooting
- [ ] Automated escalation rules
