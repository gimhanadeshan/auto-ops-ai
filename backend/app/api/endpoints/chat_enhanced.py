"""
Enhanced Chat Endpoint - LLM-First Architecture with Intelligent RAG Integration

Flow:
1. User Message → LLM Classifier (is this technical?)
2. If Technical → RAG Search (find similar issues in knowledge base)
3. If RAG Found → LLM + RAG Context (guided response with past solutions)
4. If RAG Not Found → LLM Only (general troubleshooting)
5. Ticket Intelligence Agent (create/update tickets)
6. Ticket Status Agent (manage lifecycle)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import logging

from app.services.agents.llm_conversation_agent import get_llm_conversation_agent
from app.services.dataset_analyzer import DatasetAnalyzer
from app.core.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Setup dedicated chat logger
chat_logger = logging.getLogger('chat_conversation')
if not chat_logger.handlers:
    chat_handler = logging.FileHandler('app/logs/chat.log')
    chat_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    chat_logger.addHandler(chat_handler)
    chat_logger.setLevel(logging.INFO)

router = APIRouter()


class ChatRequest(BaseModel):
    message: Optional[str] = None
    messages: Optional[list] = None
    ticket_id: Optional[int] = None
    user_email: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    is_technical: bool
    should_escalate: bool
    is_resolved: bool
    ticket_id: Optional[int] = None
    metadata: dict


class IntentClassification(BaseModel):
    """Result of LLM intent classification."""
    is_technical: bool
    category: str  # hardware, software, network, account, other
    urgency: str   # low, medium, high, critical
    confidence: float
    reasoning: str


def classify_intent_with_llm(
    llm_agent,
    user_message: str,
    conversation_history: List[Dict]
) -> IntentClassification:
    """
    STEP 1: Use LLM to classify if the message is technical.
    This is more accurate than keyword matching.
    """
    # Build context from recent conversation
    recent_context = ""
    if conversation_history:
        recent_msgs = conversation_history[-4:]  # Last 4 messages
        for msg in recent_msgs:
            role = "User" if msg.get('role') == 'user' else "Bot"
            recent_context += f"{role}: {msg.get('content', '')}\n"
    
    classification_prompt = f"""Analyze this IT support conversation and classify the user's intent.

Recent conversation:
{recent_context}

Current user message: "{user_message}"

Classify as JSON:
{{
    "is_technical": true/false,  // Is this about a technical/IT issue?
    "category": "hardware|software|network|account|general|other",
    "urgency": "low|medium|high|critical",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Rules:
- "is_technical" = true for: computers, phones, printers, gaming consoles, software, apps, network issues, login problems
- "is_technical" = false for: greetings, small talk, non-IT questions
- "urgency" = critical if: system down, data loss risk, security issue, deadline mentioned
- "urgency" = high if: blocking work, multiple users affected
- "urgency" = medium if: inconvenience but has workaround
- "urgency" = low if: general question, feature request

Return ONLY the JSON, no other text."""

    try:
        import json
        response = llm_agent.model.generate_content(classification_prompt)
        
        if response and response.text:
            # Parse JSON from response
            text = response.text.strip()
            # Handle markdown code blocks
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            
            result = json.loads(text)
            
            return IntentClassification(
                is_technical=result.get('is_technical', False),
                category=result.get('category', 'other'),
                urgency=result.get('urgency', 'medium'),
                confidence=result.get('confidence', 0.5),
                reasoning=result.get('reasoning', 'Unable to determine')
            )
    except Exception as e:
        logger.warning(f"[CLASSIFIER] LLM classification failed: {e}, using fallback")
    
    # Fallback to keyword-based classification
    return fallback_keyword_classification(user_message)


def fallback_keyword_classification(user_message: str) -> IntentClassification:
    """Fallback keyword-based classification if LLM fails."""
    message_lower = user_message.lower()
    
    # Technical keywords by category
    categories = {
        'hardware': ['computer', 'laptop', 'desktop', 'pc', 'mac', 'phone', 'iphone', 'android',
                    'printer', 'monitor', 'keyboard', 'mouse', 'playstation', 'ps4', 'ps5', 
                    'xbox', 'nintendo', 'console', 'battery', 'charging', 'screen'],
        'software': ['app', 'application', 'software', 'program', 'install', 'update', 
                    'chrome', 'browser', 'outlook', 'teams', 'zoom', 'crash', 'freeze'],
        'network': ['wifi', 'network', 'internet', 'connection', 'vpn', 'router', 'ethernet', 'slow'],
        'account': ['login', 'password', 'account', 'access', 'locked', 'authentication']
    }
    
    # Issue keywords
    issue_keywords = ['not working', 'broken', 'error', 'problem', 'issue', 'help', 
                     'fix', 'crash', 'freeze', 'slow', 'cant', "can't", 'wont', "won't"]
    
    # Urgency keywords
    urgency_critical = ['urgent', 'emergency', 'critical', 'asap', 'down', 'security']
    urgency_high = ['meeting', 'deadline', 'important', 'blocking', 'cant work']
    
    # Detect category
    detected_category = 'other'
    for cat, keywords in categories.items():
        if any(kw in message_lower for kw in keywords):
            detected_category = cat
            break
    
    # Detect if technical
    has_issue = any(kw in message_lower for kw in issue_keywords)
    has_category = detected_category != 'other'
    is_technical = has_issue or has_category
    
    # Detect urgency
    urgency = 'medium'
    if any(kw in message_lower for kw in urgency_critical):
        urgency = 'critical'
    elif any(kw in message_lower for kw in urgency_high):
        urgency = 'high'
    elif not is_technical:
        urgency = 'low'
    
    return IntentClassification(
        is_technical=is_technical,
        category=detected_category,
        urgency=urgency,
        confidence=0.7 if is_technical else 0.5,
        reasoning="Keyword-based classification (fallback)"
    )


def search_rag_knowledge_base(
    analyzer: DatasetAnalyzer,
    user_message: str,
    category: str
) -> Optional[str]:
    """
    STEP 2: Search RAG knowledge base for similar issues.
    Returns formatted context for LLM if matches found.
    """
    try:
        similar_issues = analyzer.find_similar_issues(
            description=user_message,
            category=category if category != 'other' else None,
            limit=3
        )
        
        if not similar_issues:
            return None
        
        # Filter by minimum similarity threshold
        relevant_issues = [
            issue for issue in similar_issues 
            if issue.get('similarity_score', 0) >= 0.5  # 50% minimum
        ]
        
        if not relevant_issues:
            return None
        
        # Format for LLM
        rag_context = "\n\n".join([
            f"**Similar Issue {i+1}** (Match: {issue['similarity_score']*100:.0f}%)\n"
            f"Problem: {issue['title']}\n"
            f"Solution: {' -> '.join(issue['resolution_steps'])}"
            for i, issue in enumerate(relevant_issues)
        ])
        
        return rag_context
        
    except Exception as e:
        logger.error(f"[RAG] Search error: {e}")
        return None


@router.post("/chat", response_model=ChatResponse)
async def chat_enhanced(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Enhanced LLM-First Chat Endpoint.
    
    Flow:
    1. LLM classifies intent (technical vs general)
    2. If technical → Search RAG
    3. LLM generates response (with or without RAG context)
    4. Ticket agents manage tickets
    """
    try:
        # Get user email
        user_email = request.user_email or "anonymous@autoops.ai"
        
        # Extract message
        if request.message:
            user_message = request.message.strip()
        elif request.messages and len(request.messages) > 0:
            last_msg = request.messages[-1]
            user_message = last_msg.get('content', '').strip() if isinstance(last_msg, dict) else str(last_msg).strip()
        else:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"[CHAT] User: {user_email} | Message: {user_message[:100]}")
        chat_logger.info("=" * 80)
        chat_logger.info(f"USER: {user_email}")
        chat_logger.info(f"MESSAGE: {user_message}")
        
        # Initialize services
        llm_agent = get_llm_conversation_agent()
        analyzer = DatasetAnalyzer()
        
        # Get conversation history
        conversation_history = llm_agent.conversations.get(user_email, [])
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 1: LLM CLASSIFIER - Determine if technical
        # ═══════════════════════════════════════════════════════════════════
        intent = classify_intent_with_llm(llm_agent, user_message, conversation_history)
        
        chat_logger.info(f"CLASSIFIER: Technical={intent.is_technical}, Category={intent.category}, Urgency={intent.urgency}")
        chat_logger.info(f"  Confidence: {intent.confidence:.0%}")
        chat_logger.info(f"  Reasoning: {intent.reasoning}")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 2: RAG SEARCH - Find similar issues (if technical)
        # ═══════════════════════════════════════════════════════════════════
        rag_context = None
        rag_found = False
        
        if intent.is_technical:
            chat_logger.info("RAG SEARCH: Searching knowledge base...")
            rag_context = search_rag_knowledge_base(analyzer, user_message, intent.category)
            
            if rag_context:
                rag_found = True
                chat_logger.info("RAG: [FOUND] Similar issues in knowledge base")
                chat_logger.info(f"  Context preview: {rag_context[:200]}...")
            else:
                chat_logger.info("RAG: [NOT FOUND] No similar issues - LLM will troubleshoot from scratch")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 3: LLM RESPONSE - Generate response (with or without RAG)
        # ═══════════════════════════════════════════════════════════════════
        response = llm_agent.process_message(
            user_email=user_email,
            user_message=user_message,
            rag_context=rag_context
        )
        
        # Override is_technical with our classifier result (more accurate)
        response['is_technical'] = intent.is_technical
        
        chat_logger.info(f"LLM RESPONSE: {response['message'][:200]}...")
        chat_logger.info(f"METADATA: Technical={response['is_technical']}, RAG_Used={rag_found}, Escalate={response['should_escalate']}, Resolved={response['is_resolved']}")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 4: TICKET INTELLIGENCE - Create/update tickets
        # ═══════════════════════════════════════════════════════════════════
        ticket_id = request.ticket_id
        turn_count = len([m for m in conversation_history if m.get('role') == 'user'])
        
        # Create ticket for technical issues
        if intent.is_technical and not ticket_id:
            ticket_id = await _handle_ticket_creation(
                db, user_email, conversation_history, rag_context, 
                intent, turn_count, chat_logger
            )
        
        # Update priority if needed
        if ticket_id and turn_count >= 4:
            await _handle_priority_update(
                db, ticket_id, conversation_history, turn_count, chat_logger
            )
        
        # Handle escalation
        if ticket_id and response['should_escalate']:
            await _handle_escalation(db, ticket_id, chat_logger)
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 5: TICKET STATUS - Manage lifecycle
        # ═══════════════════════════════════════════════════════════════════
        if ticket_id:
            await _handle_status_management(
                db, ticket_id, conversation_history, 
                response['is_resolved'], chat_logger
            )
        
        chat_logger.info("=" * 80 + "\n")
        
        # Return response
        return ChatResponse(
            message=response['message'],
            is_technical=intent.is_technical,
            should_escalate=response['should_escalate'],
            is_resolved=response['is_resolved'],
            ticket_id=ticket_id,
            metadata={
                **response.get('metadata', {}),
                "category": intent.category,
                "urgency": intent.urgency,
                "rag_found": rag_found,
                "classifier_confidence": intent.confidence,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CHAT] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - Ticket Management
# ═══════════════════════════════════════════════════════════════════════════

async def _handle_ticket_creation(
    db, user_email, conversation_history, rag_context, 
    intent, turn_count, chat_logger
) -> Optional[int]:
    """Handle intelligent ticket creation."""
    try:
        from app.services.agents.ticket_intelligence_agent import get_ticket_intelligence_agent
        from app.services.ticket_service import TicketService
        from app.models.ticket import TicketCreate, TicketPriority
        
        ticket_agent = get_ticket_intelligence_agent()
        
        # Pass the LLM classification result to the ticket agent
        # This ensures tickets are created for technical issues even when
        # user's messages are short like "yes", "okay", "still no"
        create_decision = ticket_agent.should_create_ticket(
            conversation_history=conversation_history,
            turn_count=turn_count,
            is_technical_from_llm=intent.is_technical  # Trust LLM classification!
        )
        
        chat_logger.info(f"TICKET-AI: Create={create_decision['should_create']} ({create_decision['reason']})")
        
        if not create_decision['should_create']:
            return None
        
        # Generate metadata
        metadata = ticket_agent.generate_ticket_metadata(
            conversation_history=conversation_history,
            rag_context=rag_context
        )
        
        # Use classifier urgency to set priority
        priority_map = {
            'critical': TicketPriority.CRITICAL,
            'high': TicketPriority.HIGH,
            'medium': TicketPriority.MEDIUM,
            'low': TicketPriority.LOW
        }
        priority = priority_map.get(intent.urgency, TicketPriority.MEDIUM)
        
        # Create ticket
        ticket_data = TicketCreate(
            title=metadata['title'],
            description=metadata['description'],
            user_email=user_email,
            priority=priority
        )
        
        db_ticket = TicketService.create_ticket(db=db, ticket_data=ticket_data)
        
        chat_logger.info(f"TICKET CREATED: #{db_ticket.id}")
        chat_logger.info(f"  Title: {metadata['title']}")
        chat_logger.info(f"  Category: {intent.category}")
        chat_logger.info(f"  Priority: {priority.value}")
        
        return db_ticket.id
        
    except Exception as e:
        logger.error(f"[TICKET] Creation error: {e}", exc_info=True)
        return None


async def _handle_priority_update(
    db, ticket_id, conversation_history, turn_count, chat_logger
):
    """Handle priority updates based on conversation."""
    try:
        from app.services.agents.ticket_intelligence_agent import get_ticket_intelligence_agent
        from app.services.ticket_service import TicketService
        from app.models.ticket import TicketUpdate, TicketPriority
        
        ticket_agent = get_ticket_intelligence_agent()
        current_ticket = TicketService.get_ticket(db, ticket_id)
        
        if not current_ticket:
            return
        
        update_decision = ticket_agent.should_update_priority(
            conversation_history=conversation_history,
            current_priority=current_ticket.priority.value,
            turn_count=turn_count
        )
        
        if update_decision['should_update']:
            priority_map = {
                'critical': TicketPriority.CRITICAL,
                'high': TicketPriority.HIGH,
                'medium': TicketPriority.MEDIUM,
                'low': TicketPriority.LOW
            }
            new_priority = priority_map.get(update_decision['new_priority'])
            
            if new_priority:
                ticket_update = TicketUpdate(
                    priority=new_priority,
                    ai_analysis=f"Priority escalated: {update_decision['reason']}"
                )
                TicketService.update_ticket(db, ticket_id, ticket_update)
                
                chat_logger.info(f"PRIORITY ESCALATED: #{ticket_id}")
                chat_logger.info(f"  {current_ticket.priority.value} -> {new_priority.value}")
                chat_logger.info(f"  Reason: {update_decision['reason']}")
                
    except Exception as e:
        logger.error(f"[TICKET] Priority update error: {e}", exc_info=True)


async def _handle_escalation(db, ticket_id, chat_logger):
    """Handle escalation to human support."""
    try:
        from app.services.ticket_service import TicketService
        from app.models.ticket import TicketUpdate, TicketStatus, TicketPriority
        
        ticket_update = TicketUpdate(
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.HIGH,
            ai_analysis="Escalated to human support - bot unable to resolve"
        )
        TicketService.update_ticket(db, ticket_id, ticket_update)
        
        chat_logger.info(f"ESCALATED TO HUMAN: #{ticket_id}")
        
    except Exception as e:
        logger.error(f"[TICKET] Escalation error: {e}", exc_info=True)


async def _handle_status_management(
    db, ticket_id, conversation_history, is_resolved, chat_logger
):
    """Handle ticket status lifecycle."""
    try:
        from app.services.agents.ticket_status_agent import get_ticket_status_agent
        from app.services.ticket_service import TicketService
        from app.models.ticket import TicketUpdate, TicketStatus
        
        status_agent = get_ticket_status_agent()
        current_ticket = TicketService.get_ticket(db, ticket_id)
        
        if not current_ticket:
            return
        
        status_decision = status_agent.analyze_conversation_status(
            conversation_history=conversation_history,
            current_status=current_ticket.status.value,
            ticket_created_at=current_ticket.created_at,
            llm_resolved_flag=is_resolved
        )
        
        chat_logger.info(f"STATUS-AGENT: {current_ticket.status.value} -> {status_decision['recommended_status']}")
        chat_logger.info(f"  Should Update: {status_decision['should_update']}, Confidence: {status_decision['confidence']}/10")
        
        if status_decision['should_update']:
            status_map = {
                'open': TicketStatus.OPEN,
                'in_progress': TicketStatus.IN_PROGRESS,
                'resolved': TicketStatus.RESOLVED,
                'closed': TicketStatus.CLOSED
            }
            new_status = status_map.get(status_decision['recommended_status'])
            
            if new_status and new_status != current_ticket.status:
                ticket_update = TicketUpdate(
                    status=new_status,
                    resolution_notes=status_decision.get('resolution_summary')
                )
                TicketService.update_ticket(db, ticket_id, ticket_update)
                
                chat_logger.info(f"STATUS CHANGED: #{ticket_id}")
                chat_logger.info(f"  {current_ticket.status.value} -> {new_status.value}")
                chat_logger.info(f"  Reason: {status_decision['reason']}")
        
        if status_decision.get('sla_warning'):
            chat_logger.info(f"SLA WARNING: #{ticket_id} approaching breach!")
            
    except Exception as e:
        logger.error(f"[STATUS] Management error: {e}", exc_info=True)


class ResetRequest(BaseModel):
    user_email: Optional[str] = None


@router.post("/chat/reset")
async def reset_chat(request: ResetRequest):
    """Reset conversation history for user."""
    try:
        user_email = request.user_email or "anonymous@autoops.ai"
        
        llm_agent = get_llm_conversation_agent()
        llm_agent.reset_conversation(user_email)
        logger.info(f"[CHAT] Conversation reset for {user_email}")
        return {"message": "Conversation reset successfully", "user_email": user_email}
    except Exception as e:
        logger.error(f"[CHAT] Reset error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset conversation")
