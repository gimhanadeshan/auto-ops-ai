"""
Chat endpoint - AI chatbot for user support.
"""
import logging
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from app.core.database import get_db
from app.config import get_settings
from app.services.rag_engine import get_rag_engine
from app.core.llm_factory import get_chat_model

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[ChatMessage]
    user_email: str = None


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    relevant_docs: List[Dict] = []


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat endpoint for AI-powered support.
    """
    try:
        # Get the last user message
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Get relevant context from knowledge base
        rag_engine = get_rag_engine()
        relevant_docs = rag_engine.search(user_message, k=3)
        context = rag_engine.get_relevant_context(user_message, k=3)
        
        # Initialize LLM
        llm = get_chat_model(temperature=0.7)
        
        # Create chat prompt
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful IT support assistant. Help users with their technical issues.

Use the following context from the knowledge base to provide accurate answers:

{context}

Guidelines:
- Be friendly and professional
- Provide clear, step-by-step instructions
- If you're not sure, suggest creating a support ticket
- Reference similar past issues when relevant
- Keep responses concise but complete"""),
            ("user", "{user_message}")
        ])
        
        # Convert message history to LangChain format
        history = []
        for msg in request.messages[:-1]:  # Exclude the last user message
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                history.append(AIMessage(content=msg.content))
        
        # Generate response
        chain = chat_prompt | llm
        response = chain.invoke({
            "context": context,
            "user_message": user_message,
            "history": history
        })
        
        return ChatResponse(
            message=response.content,
            relevant_docs=relevant_docs
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/chat/suggest-ticket")
async def suggest_ticket_creation(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze conversation and suggest if a ticket should be created.
    """
    try:
        # Analyze the conversation
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in request.messages
        ])
        
        llm = get_chat_model(temperature=0.3)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze this support conversation and determine if a ticket should be created.

Respond in JSON format:
{{
    "should_create_ticket": true/false,
    "reason": "explanation",
    "suggested_title": "ticket title if applicable",
    "suggested_description": "ticket description if applicable",
    "urgency": "low|medium|high"
}}

Create a ticket if:
- Issue cannot be resolved through chat
- Requires technical investigation
- Affects system functionality
- User explicitly requests escalation"""),
            ("user", "{conversation}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"conversation": conversation_text})
        
        import json
        result = json.loads(response.content)
        
        return result
        
    except Exception as e:
        logger.error(f"Error suggesting ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
