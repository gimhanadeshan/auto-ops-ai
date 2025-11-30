"""
Main FastAPI application entry point.
Auto-Ops-AI Backend Server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.core.database import init_db
from app.core.logging_config import setup_logging, get_logger
import importlib
# Importing API endpoint modules lazily later so missing optional packages
# (e.g. langchain) won't prevent the app from starting during development.

# Setup logging
setup_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Auto-Ops-AI Backend...")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Embedding Provider: {settings.embedding_provider}")
    
    # Initialize database
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Initialize knowledge base
    logger.info("Initializing knowledge base...")
    try:
        # Import the RAG initializer lazily to avoid hard dependency on
        # optional packages (e.g. chromadb) during application import.
        from app.services.rag_engine import initialize_knowledge_base
        initialize_knowledge_base()
    except Exception as e:
        logger.warning(f"Could not initialize knowledge base: {e}")
        logger.info("You can initialize it later by loading ticketing data.")
    
    logger.info("Auto-Ops-AI Backend is ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Auto-Ops-AI Backend...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered IT Operations and Support System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Auto-Ops-AI Backend is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "auto-ops-ai-backend"
    }


# Include routers (imported lazily below)

# Always try to include lightweight endpoints first (so health/status remain available)
try:
    from app.api.endpoints import status
    app.include_router(
        status.router,
        prefix=f"{settings.api_prefix}",
        tags=["Status"]
    )
except Exception as e:
    logger.warning(f"Could not include status endpoint at startup: {e}")

# Import other endpoints individually so optional heavy dependencies don't break startup
for _name, _tag in (("chat", "Chat"), ("tickets", "Tickets"), ("dashboard", "Dashboard")):
    try:
        mod = importlib.import_module(f"app.api.endpoints.{_name}")
        app.include_router(
            mod.router,
            prefix=f"{settings.api_prefix}",
            tags=[_tag]
        )
    except Exception as e:
        logger.warning(f"Could not include {_name} endpoint at startup: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
