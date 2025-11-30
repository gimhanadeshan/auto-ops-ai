"""
LLM Factory - Provides unified interface for different LLM providers.
Supports OpenAI and Google Gemini.
"""
import logging
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.schema import BaseLanguageModel
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMFactory:
    """Factory for creating LLM instances based on configuration."""
    
    @staticmethod
    def get_chat_model(
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> BaseLanguageModel:
        """
        Get configured chat model (OpenAI or Gemini).
        
        Args:
            temperature: Override default temperature
            model: Override default model name
            
        Returns:
            Configured chat model instance
        """
        provider = settings.llm_provider
        temp = temperature if temperature is not None else (
            settings.openai_temperature if provider == "openai" else settings.gemini_temperature
        )
        
        try:
            if provider == "openai":
                model_name = model or settings.openai_model
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                
                logger.info(f"Initializing OpenAI model: {model_name}")
                return ChatOpenAI(
                    model=model_name,
                    temperature=temp,
                    openai_api_key=settings.openai_api_key
                )
            
            elif provider == "gemini":
                model_name = model or settings.gemini_model
                if not settings.google_api_key:
                    raise ValueError("Google API key not configured")
                
                logger.info(f"Initializing Gemini model: {model_name}")
                return ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=temp,
                    google_api_key=settings.google_api_key,
                    convert_system_message_to_human=True  # Gemini requires this
                )
            
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise
    
    @staticmethod
    def get_embeddings():
        """
        Get configured embeddings model.
        
        Returns:
            Configured embeddings instance
        """
        provider = settings.embedding_provider
        
        try:
            if provider == "openai":
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                
                logger.info(f"Initializing OpenAI embeddings: {settings.embedding_model}")
                return OpenAIEmbeddings(
                    openai_api_key=settings.openai_api_key,
                    model=settings.embedding_model
                )
            
            elif provider == "gemini":
                if not settings.google_api_key:
                    raise ValueError("Google API key not configured")
                
                logger.info(f"Initializing Gemini embeddings: {settings.embedding_model}")
                return GoogleGenerativeAIEmbeddings(
                    google_api_key=settings.google_api_key,
                    model=settings.embedding_model
                )
            
            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            raise


# Convenience functions
def get_chat_model(temperature: Optional[float] = None, model: Optional[str] = None) -> BaseLanguageModel:
    """Get chat model instance."""
    return LLMFactory.get_chat_model(temperature=temperature, model=model)


def get_embeddings():
    """Get embeddings instance."""
    return LLMFactory.get_embeddings()
