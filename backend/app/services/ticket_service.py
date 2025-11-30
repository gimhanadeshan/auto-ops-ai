"""
Ticket service - CRUD operations and business logic for tickets.
"""
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.ticket import (
    TicketDB, TicketCreate, TicketUpdate, TicketStatus,
    TicketPriority, TicketCategory
)
from app.services.agents.triage_agent import get_triage_agent
from app.services.agents.troubleshooter import get_troubleshooter_agent

logger = logging.getLogger(__name__)


class TicketService:
    """Service for managing support tickets."""
    
    @staticmethod
    def create_ticket(db: Session, ticket_data: TicketCreate) -> TicketDB:
        """
        Create a new ticket with AI analysis.
        """
        # Create ticket in database
        db_ticket = TicketDB(
            title=ticket_data.title,
            description=ticket_data.description,
            user_email=ticket_data.user_email,
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM
        )
        
        # Run AI triage analysis
        try:
            triage_agent = get_triage_agent()
            analysis = triage_agent.analyze_ticket(
                ticket_data.title,
                ticket_data.description
            )
            
            # Update ticket with AI analysis
            db_ticket.category = analysis["category"]
            db_ticket.priority = analysis["priority"]
            db_ticket.ai_analysis = f"{analysis['analysis']}\n\nConfidence: {analysis['confidence']}\nReasoning: {analysis['reasoning']}"
            
            # Get suggested assignment
            db_ticket.assigned_to = triage_agent.suggest_assignment(
                analysis["category"],
                analysis["priority"]
            )
            
            # If it's a system issue, generate troubleshooting steps
            if analysis["category"] == TicketCategory.SYSTEM_ISSUE:
                troubleshooter = get_troubleshooter_agent()
                steps = troubleshooter.generate_troubleshooting_steps(
                    ticket_data.title,
                    ticket_data.description,
                    str(analysis["category"])
                )
                db_ticket.troubleshooting_steps = "\n".join(
                    f"{i+1}. {step}" for i, step in enumerate(steps)
                )
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            db_ticket.ai_analysis = f"Error during analysis: {str(e)}"
        
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        
        return db_ticket
    
    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Optional[TicketDB]:
        """Get a ticket by ID."""
        return db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
    
    @staticmethod
    def get_tickets(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        category: Optional[TicketCategory] = None
    ) -> List[TicketDB]:
        """Get tickets with optional filtering."""
        query = db.query(TicketDB)
        
        if status:
            query = query.filter(TicketDB.status == status)
        if priority:
            query = query.filter(TicketDB.priority == priority)
        if category:
            query = query.filter(TicketDB.category == category)
        
        return query.order_by(desc(TicketDB.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_ticket(
        db: Session,
        ticket_id: int,
        ticket_update: TicketUpdate
    ) -> Optional[TicketDB]:
        """Update a ticket."""
        db_ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
        
        if not db_ticket:
            return None
        
        # Update fields
        update_data = ticket_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ticket, field, value)
        
        # Update resolved_at if status changed to resolved or closed
        if ticket_update.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            if not db_ticket.resolved_at:
                db_ticket.resolved_at = datetime.utcnow()
        
        db_ticket.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_ticket)
        
        return db_ticket
    
    @staticmethod
    def delete_ticket(db: Session, ticket_id: int) -> bool:
        """Delete a ticket."""
        db_ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
        
        if not db_ticket:
            return False
        
        db.delete(db_ticket)
        db.commit()
        
        return True
    
    @staticmethod
    def get_ticket_stats(db: Session) -> dict:
        """Get statistics about tickets."""
        total = db.query(TicketDB).count()
        open_tickets = db.query(TicketDB).filter(TicketDB.status == TicketStatus.OPEN).count()
        in_progress = db.query(TicketDB).filter(TicketDB.status == TicketStatus.IN_PROGRESS).count()
        resolved = db.query(TicketDB).filter(TicketDB.status == TicketStatus.RESOLVED).count()
        closed = db.query(TicketDB).filter(TicketDB.status == TicketStatus.CLOSED).count()
        
        # Priority breakdown
        critical = db.query(TicketDB).filter(TicketDB.priority == TicketPriority.CRITICAL).count()
        high = db.query(TicketDB).filter(TicketDB.priority == TicketPriority.HIGH).count()
        medium = db.query(TicketDB).filter(TicketDB.priority == TicketPriority.MEDIUM).count()
        low = db.query(TicketDB).filter(TicketDB.priority == TicketPriority.LOW).count()
        
        # Category breakdown
        user_error = db.query(TicketDB).filter(TicketDB.category == TicketCategory.USER_ERROR).count()
        system_issue = db.query(TicketDB).filter(TicketDB.category == TicketCategory.SYSTEM_ISSUE).count()
        feature_request = db.query(TicketDB).filter(TicketDB.category == TicketCategory.FEATURE_REQUEST).count()
        
        return {
            "total": total,
            "by_status": {
                "open": open_tickets,
                "in_progress": in_progress,
                "resolved": resolved,
                "closed": closed
            },
            "by_priority": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low
            },
            "by_category": {
                "user_error": user_error,
                "system_issue": system_issue,
                "feature_request": feature_request
            }
        }
    
    @staticmethod
    def run_troubleshooting(db: Session, ticket_id: int) -> Optional[TicketDB]:
        """Run full troubleshooting workflow for a ticket."""
        db_ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
        
        if not db_ticket:
            return None
        
        try:
            troubleshooter = get_troubleshooter_agent()
            result = troubleshooter.handle_issue(
                db_ticket.title,
                db_ticket.description,
                str(db_ticket.category)
            )
            
            # Update ticket with results
            db_ticket.troubleshooting_steps = "\n".join(
                f"{i+1}. {step}" for i, step in enumerate(result["troubleshooting_steps"])
            )
            db_ticket.resolution = result["suggested_resolution"]
            db_ticket.ai_analysis = f"{db_ticket.ai_analysis}\n\nDiagnostics:\n{result['diagnostics']}"
            
            db.commit()
            db.refresh(db_ticket)
            
        except Exception as e:
            logger.error(f"Error running troubleshooting: {e}")
        
        return db_ticket


# Create global service instance
ticket_service = TicketService()
