"""
Configuration settings for the Auto-Ops-AI backend.
Environment variables and application settings.
"""
from typing import List, Literal
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API Configuration
    app_name: str = "Auto-Ops-AI"
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    # LLM Provider Configuration
    llm_provider: Literal["openai", "gemini"] = "gemini"  # Default to Gemini
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    
    # Google Gemini Configuration
    google_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"
    gemini_temperature: float = 0.7
    
    # Embedding Configuration
    embedding_provider: Literal["openai", "gemini"] = "gemini"
    embedding_model: str = "models/text-embedding-004"  # Gemini embedding
    
    # Database Configuration
    database_url: str = "sqlite:///./data/processed/auto_ops.db"
    
    # Vector Database Configuration
    chroma_persist_directory: str = "./data/processed/chroma_db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000", "http://localhost:5173"]
    
    # Logging
    log_level: str = "INFO"
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS which may be provided as:
        - a Python/JSON-like list string: ["http://...","http://..."]
        - a comma-separated string: http://...,http://...
        - an actual list (passed in programmatically)
        """
        if isinstance(v, str):
            s = v.strip()
            # strip surrounding brackets if present
            if s.startswith("[") and s.endswith("]"):
                s = s[1:-1]
            # remove any surrounding quotes from each item and split by comma
            parts = [p.strip().strip("'\"") for p in s.split(",") if p.strip()]
            return parts
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
