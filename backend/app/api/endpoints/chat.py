"""
Multi-Agent Chat Endpoint - IT Support with Conversational Troubleshooting
Works like a real IT technician: asks questions, debugs, provides solutions.
"""
import logging
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.config import get_settings
from app.services.agents.conversation_agent import get_conversation_agent
from app.services.agents.enhanced_conversation_agent import get_enhanced_conversation_agent
from app.services.dataset_analyzer import get_analyzer
from app.services.ticket_service import ticket_service
from app.models.ticket import TicketCreate
import os

CHAT_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'chat.log')

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class ChatMessage(BaseModel):
    """Chat message."""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Chat request - conversation history."""
    messages: List[ChatMessage]
    user_email: str = "demo@acme-soft.com"  # Default for testing
    ticket_id: Optional[int] = None  # Existing ticket if continuing conversation


class ChatResponse(BaseModel):
    """Chat response with agent actions."""
    message: str
    ticket_id: Optional[int] = None
    action: str  # "clarifying", "troubleshooting", "resolved", "escalated"
    needs_clarification: bool = False
    priority_info: Optional[Dict] = None
    similar_issues: Optional[List[Dict]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Multi-Agent Conversational IT Support
    
    Flow:
    1. Analyze if issue is clear
    2. Ask clarifying questions if needed
    3. Calculate priority using dataset
    4. Find similar past issues
    5. Provide troubleshooting steps
    6. Create/update ticket
    7. Decide on escalation
    """
    try:
        # Get enhanced conversation agent
        enhanced_agent = get_enhanced_conversation_agent()
        analyzer = get_analyzer()
        
        # Extract last user message
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        logger.info(f"Processing chat for user: {request.user_email}")
        logger.info(f"Message: {user_message[:100]}...")
        try:
            os.makedirs(os.path.dirname(CHAT_LOG_PATH), exist_ok=True)
            with open(CHAT_LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.utcnow().isoformat()} | IN | {request.user_email} | {user_message[:200].replace('\n',' ')}\n")
        except Exception:
            pass
        
        # STEP 1: Get or create conversation state
        conversation_state = enhanced_agent.get_or_create_conversation(request.user_email)
        
        # STEP 2: Get user context
        user_context = analyzer.get_user_context(request.user_email)
        user_name = user_context.get('name', 'there')
        user_tier = user_context.get('tier', 'staff')
        
        # STEP 3: Process user message through enhanced agent
        agent_response = enhanced_agent.process_user_response(user_message, conversation_state)
        
        logger.info(f"Agent action: {agent_response['action']}, Phase: {agent_response.get('phase')}")
        try:
            with open(CHAT_LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(
                    f"{datetime.utcnow().isoformat()} | OUT | {request.user_email} | "
                    f"action={agent_response['action']} phase={agent_response.get('phase')} "
                    f"llmFirst={settings.conversation_llm_first} category={conversation_state.context.category or 'unknown'} isTechnical={conversation_state.context.is_technical} | "
                    f"{agent_response['message'][:200].replace('\n',' ')}\n"
                )
        except Exception:
            pass
        
        # STEP 4: RAG Integration - Check for similar issues if technical and has description
        similar_issues = None
        rag_used = False
        
        if (conversation_state.context.is_technical and 
            conversation_state.context.issue_description and 
            len(conversation_state.context.issue_description) > 10):
            try:
                logger.info(f"[RAG] Searching for similar issues: {conversation_state.context.issue_description[:50]}")
                similar_issues = analyzer.find_similar_issues(
                    issue_description=conversation_state.context.issue_description,
                    category=conversation_state.context.category,
                    top_k=3,
                    threshold=0.75  # Higher threshold for quality matches
                )
                
                if similar_issues:
                    rag_used = True
                    logger.info(f"[RAG] Found {len(similar_issues)} similar issues")
                    
                    # Add RAG suggestions to agent response if in troubleshooting phase
                    if conversation_state.phase.value == "troubleshooting" and not agent_response.get("rag_added"):
                        rag_solutions = "\\n\\n".join([
                            f"📋 Similar issue resolved: {issue.get('description', 'N/A')[:100]}... → {issue.get('resolution', 'N/A')[:150]}"
                            for issue in similar_issues[:2]  # Top 2 most similar
                        ])
                        
                        # Prepend RAG suggestions to the agent message
                        if rag_solutions:
                            agent_response["message"] = (
                                f"I found similar issues that were resolved:\\n{rag_solutions}\\n\\n"
                                f"Does this help? If not, {agent_response['message']}"
                            )
                            agent_response["rag_added"] = True
                else:
                    logger.info("[RAG] No similar issues found above threshold, using LLM")
            except Exception as e:
                logger.error(f"[RAG] Error searching similar issues: {e}")
                similar_issues = None
        
        # STEP 5: Handle different action types
        ticket_id = request.ticket_id
        
        # If action requires ticket creation
        if agent_response.get("create_ticket") and not conversation_state.ticket_created:
            category = conversation_state.context.category or "other"
            urgency_map = {"critical": "critical", "high": "high", "medium": "medium", "low": "low"}
            urgency = urgency_map.get(conversation_state.context.urgency_indicators[0] if conversation_state.context.urgency_indicators else "medium", "medium")
            
            # Calculate smart priority
            priority, priority_reasoning = analyzer.calculate_priority(
                user_email=request.user_email,
                category=category,
                urgency=urgency,
                description=conversation_state.context.issue_description
            )
            
            # Adjust priority based on conversation context
            if conversation_state.context.has_upcoming_meeting and conversation_state.context.meeting_time_minutes:
                if conversation_state.context.meeting_time_minutes <= 30:
                    priority = "critical"
                elif priority == "low":
                    priority = "medium"
            
            if conversation_state.context.data_at_risk:
                priority = "critical"
            
            # Create ticket with full context
            issue_summary = conversation_state.context.issue_description[:100] if conversation_state.context.issue_description else user_message[:100]
            
            # Build detailed description
            full_description = f"**Issue:** {conversation_state.context.issue_description}\n\n"
            
            if conversation_state.context.time_of_occurrence:
                full_description += f"**Occurred:** {conversation_state.context.time_of_occurrence}\n"
            
            if conversation_state.context.frequency:
                full_description += f"**Frequency:** {conversation_state.context.frequency}\n"
            
            if conversation_state.context.error_messages:
                full_description += f"**Error Messages:** {', '.join(conversation_state.context.error_messages)}\n"
            
            if conversation_state.context.steps_already_taken:
                full_description += f"**Already Tried:** {', '.join(conversation_state.context.steps_already_taken)}\n"
            
            if conversation_state.context.attempted_solutions:
                full_description += f"\n**Troubleshooting Attempts:** {len(conversation_state.context.attempted_solutions)}\n"
                for sol in conversation_state.context.attempted_solutions:
                    full_description += f"- {sol['instruction'][:100]} (Status: {sol['status']})\n"
            
            if conversation_state.context.urgency_indicators:
                full_description += f"\n**Urgency Factors:** {', '.join(conversation_state.context.urgency_indicators)}\n"
            
            ticket_data = TicketCreate(
                title=issue_summary,
                description=full_description,
                user_email=request.user_email,
                priority=priority
            )
            
            ticket = ticket_service.create_ticket(db, ticket_data)
            ticket_id = ticket.id
            conversation_state.ticket_id = ticket_id
            conversation_state.ticket_created = True
            
            logger.info(f"Created ticket #{ticket_id} with priority {priority}")
            
            # Add ticket info to response
            agent_response["message"] += f"\n\n🎫 **Ticket #{ticket_id}** created with **{priority}** priority"
        
        # Add similar issues context if found
        if similar_issues and len(similar_issues) > 0:
            top_match = similar_issues[0]
            similarity_pct = int(top_match['similarity_score'] * 100)
            
            if similarity_pct >= 70:
                agent_response["message"] += f"\n\n💡 **Tip:** I found a very similar issue ({similarity_pct}% match) that was resolved before. The steps I'm suggesting are based on that successful resolution."
        
        # Return response based on action
        return ChatResponse(
            message=agent_response["message"],
            ticket_id=ticket_id or conversation_state.ticket_id,
            action=agent_response["action"],
            needs_clarification=agent_response.get("phase") == "issue_gathering",
            priority_info=None,
            similar_issues=similar_issues
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


def _categorize_issue(description: str) -> str:
    """Simple keyword-based categorization."""
    desc_lower = description.lower()
    
    if any(kw in desc_lower for kw in ['vpn', 'network', 'wifi', 'internet', 'connection', 'connect']):
        return 'network'
    elif any(kw in desc_lower for kw in ['bsod', 'blue screen', 'crash', 'restart', 'hardware', 'mouse', 'keyboard', 'monitor']):
        return 'hardware'
    elif any(kw in desc_lower for kw in ['slow', 'freeze', 'hang', 'performance', 'lag']):
        return 'performance'
    elif any(kw in desc_lower for kw in ['login', 'password', 'access', 'permission', 'locked']):
        return 'access'
    elif any(kw in desc_lower for kw in ['outlook', 'teams', 'chrome', 'vscode', 'software', 'app', 'program']):
        return 'software'
    else:
        return 'other'


def _determine_urgency(description: str) -> str:
    """Determine urgency from description."""
    desc_lower = description.lower()
    
    # Critical keywords
    if any(kw in desc_lower for kw in ['urgent', 'critical', 'asap', 'emergency', 'down', 'crash', 'bsod', 'meeting', 'client']):
        return 'critical'
    
    # High urgency keywords
    elif any(kw in desc_lower for kw in ['important', 'deadline', 'soon', 'needed', 'cannot']):
        return 'high'
    
    # Low urgency
    elif any(kw in desc_lower for kw in ['when possible', 'sometime', 'minor', 'small']):
        return 'low'
    
    # Default medium
    return 'medium'


def _is_greeting_or_general(message: str) -> bool:
    """Check if message is a greeting or general conversation, not an IT issue."""
    msg_lower = message.lower().strip()
    
    # Very short messages
    if len(msg_lower) < 15:
        # Pure greetings
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 
                     'greetings', 'hola', 'sup', 'whats up', "what's up", 'yo']
        if any(msg_lower == greeting or msg_lower.startswith(greeting + ' ') for greeting in greetings):
            return True
    
    # General questions without specific IT issue
    general_patterns = [
        'how are you', 'how r u', 'what can you do', 'who are you', 
        'what is this', 'help me', 'can you help', 'i need help',
        'thanks', 'thank you', 'ok', 'okay', 'yes', 'no', 'sure'
    ]
    
    if any(pattern in msg_lower for pattern in general_patterns):
        # But not if it mentions specific IT problems
        it_keywords = ['slow', 'crash', 'error', 'not working', 'broken', 'issue', 
                       'problem', 'vpn', 'network', 'wifi', 'password', 'login',
                       'email', 'outlook', 'computer', 'laptop', 'freeze', 'hang']
        if not any(keyword in msg_lower for keyword in it_keywords):
            return True
    
    return False


@router.post("/chat/quick-answer")
async def quick_answer(question: str):
    """
    Quick IT question without ticket creation.
    For simple "how-to" questions.
    """
    try:
        conversation_agent = get_conversation_agent()
        
        messages = [{"role": "user", "content": question}]
        response = conversation_agent.chat(messages, temperature=0.3)
        
        return {
            "question": question,
            "answer": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Quick answer error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
