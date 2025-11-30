"""
RAG (Retrieval Augmented Generation) Engine for knowledge base search.
Uses ChromaDB for vector storage with configurable embeddings.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from app.config import get_settings
from app.core.llm_factory import get_embeddings

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGEngine:
    """RAG Engine for knowledge base retrieval."""
    
    def __init__(self):
        """Initialize RAG engine with ChromaDB."""
        self.settings = settings
        try:
            self.embeddings = get_embeddings()
            logger.info(f"Initialized embeddings with provider: {settings.embedding_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
        
        self.persist_directory = settings.chroma_persist_directory
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load existing vector store."""
        try:
            # Try to load existing vectorstore
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="tickets_kb"
            )
            logger.info(f"Loaded existing vector store from {self.persist_directory}")
        except Exception as e:
            logger.warning(f"No existing vector store found or error loading: {e}")
            logger.info("Will create new vector store when documents are added.")
    
    def load_ticketing_data(self, json_path: str = "./data/raw/ticketing_system_data_new.json"):
        """Load and index ticketing data from JSON file."""
        try:
            # Load JSON data
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to documents
            documents = []
            for item in data:
                # Create a comprehensive text representation
                content = f"""
Ticket ID: {item.get('id', 'N/A')}
Title: {item.get('title', 'N/A')}
Description: {item.get('description', 'N/A')}
Status: {item.get('status', 'N/A')}
Priority: {item.get('priority', 'N/A')}
Category: {item.get('category', 'N/A')}
Resolution: {item.get('resolution', 'N/A')}
                """.strip()
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "ticket_id": item.get('id', ''),
                        "category": item.get('category', ''),
                        "priority": item.get('priority', ''),
                        "status": item.get('status', '')
                    }
                )
                documents.append(doc)
            
            # Split documents if they're too long
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Create vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name="tickets_kb"
            )
            
            logger.info(f"Successfully loaded {len(documents)} tickets into vector store")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error loading ticketing data: {e}")
            raise
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar tickets in the knowledge base."""
        if not self.vectorstore:
            return []
        
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """Get relevant context as a formatted string."""
        results = self.search(query, k=k)
        
        if not results:
            return "No relevant information found in knowledge base."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"--- Reference {i} ---\n{result['content']}")
        
        return "\n\n".join(context_parts)


# Global RAG engine instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or create RAG engine instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine


def initialize_knowledge_base():
    """Initialize knowledge base with ticketing data."""
    engine = get_rag_engine()
    try:
        engine.load_ticketing_data()
        logger.info("Knowledge base initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize knowledge base: {e}")
