"""
Triage Agent - Classifies incoming tickets as User Error vs System Issue.
"""
import logging
from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from app.config import get_settings
from app.models.ticket import TicketCategory, TicketPriority
from app.services.rag_engine import get_rag_engine
from app.core.llm_factory import get_chat_model

logger = logging.getLogger(__name__)
settings = get_settings()


class TriageAgent:
    """Agent for triaging and classifying support tickets."""
    
    def __init__(self):
        """Initialize triage agent with LLM."""
        try:
            self.llm = get_chat_model(temperature=0.3)
            self.rag_engine = get_rag_engine()
            logger.info("Triage agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize triage agent: {e}")
            raise
    
    def analyze_ticket(self, title: str, description: str) -> Dict[str, Any]:
        """
        Analyze a ticket and determine its category, priority, and provide initial analysis.
        """
        # Get relevant context from knowledge base
        query = f"{title}\n{description}"
        context = self.rag_engine.get_relevant_context(query, k=3)
        
        # Create triage prompt
        triage_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert IT support triage agent. Your job is to analyze support tickets and classify them.

Based on the ticket information and similar past tickets, determine:
1. Category: user_error, system_issue, feature_request, or other
2. Priority: low, medium, high, or critical
3. A brief analysis of the issue
4. Your confidence level (0.0 to 1.0)

Guidelines:
- User Error: Issues caused by incorrect usage, misunderstanding, or user mistakes
- System Issue: Technical problems, bugs, outages, performance issues
- Feature Request: Requests for new functionality
- Priority based on: impact, urgency, number of affected users

Similar past tickets:
{context}

Respond in JSON format:
{{
    "category": "user_error|system_issue|feature_request|other",
    "priority": "low|medium|high|critical",
    "analysis": "Brief explanation of the issue",
    "confidence": 0.0-1.0,
    "reasoning": "Why this classification was chosen"
}}"""),
            ("user", "Title: {title}\n\nDescription: {description}")
        ])
        
        # Run analysis
        try:
            chain = triage_prompt | self.llm
            response = chain.invoke({
                "title": title,
                "description": description,
                "context": context
            })
            
            # Parse response
            import json
            result = json.loads(response.content)
            
            # Validate and convert to enums
            result["category"] = TicketCategory(result["category"])
            result["priority"] = TicketPriority(result["priority"])
            
            return result
            
        except Exception as e:
            logger.error(f"Error in triage analysis: {e}")
            # Fallback response
            return {
                "category": TicketCategory.OTHER,
                "priority": TicketPriority.MEDIUM,
                "analysis": f"Error during analysis: {str(e)}",
                "confidence": 0.0,
                "reasoning": "Automatic fallback due to error"
            }
    
    def suggest_assignment(self, category: TicketCategory, priority: TicketPriority) -> str:
        """Suggest which team or person should handle the ticket."""
        assignment_rules = {
            TicketCategory.USER_ERROR: "Support Team - Level 1",
            TicketCategory.SYSTEM_ISSUE: "Engineering Team - DevOps",
            TicketCategory.FEATURE_REQUEST: "Product Team",
            TicketCategory.OTHER: "Support Team - Level 2"
        }
        
        base_assignment = assignment_rules.get(category, "Support Team - General")
        
        # Escalate critical issues
        if priority == TicketPriority.CRITICAL:
            return f"{base_assignment} (ESCALATED - Critical Priority)"
        
        return base_assignment


# Global triage agent instance
_triage_agent = None


def get_triage_agent() -> TriageAgent:
    """Get or create triage agent instance."""
    global _triage_agent
    if _triage_agent is None:
        _triage_agent = TriageAgent()
    return _triage_agent
