from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
# ✅ WE USE TicketDB HERE because that is your class name
from app.models.ticket import TicketDB 
from app.services.sla_service import sla_service

# Define the router
router = APIRouter(tags=["Analytics"])

@router.get("/sla-risk")
async def get_sla_risk_report(db: Session = Depends(get_db)):
    """
    Fetches all OPEN tickets and uses AI to predict if they will breach SLA.
    """
    # 1. Get only active tickets (Open or In Progress)
    # We use TicketDB here
    open_tickets = db.query(TicketDB).filter(TicketDB.status.in_(['open', 'in_progress'])).all()
    
    report_data = []
    
    for t in open_tickets:
        # 2. Ask AI to predict hours
        # We handle cases where description might be None (empty)
        predicted_hours = sla_service.predict_resolution_time(
            category=t.title, 
            priority_str=t.priority, 
            description=t.description or ""
        )
        
        # 3. Define SLA Limit (Simplified logic for demo)
        # High priority = 24h limit, others = 48h limit
        sla_limit = 24 if t.priority == 'high' else 48
        
        report_data.append({
            "id": t.id,
            "title": t.title,
            "category": t.title, 
            "priority": t.priority,
            "predicted_hours": predicted_hours,
            "sla_limit": sla_limit
        })
        
    # 4. Sort by "Most Risky" first (highest predicted time)
    report_data.sort(key=lambda x: x['predicted_hours'], reverse=True)
    
    return report_data

@router.get("/weekly-trends")
async def get_weekly_trends(db: Session = Depends(get_db)):
    """
    Returns ticket counts for the last 4 weeks.
    """
    today = datetime.now()
    trends = []

    # Loop back 4 weeks
    for i in range(4):
        start_of_week = today - timedelta(weeks=i+1)
        end_of_week = today - timedelta(weeks=i)
        
        # Count tickets created in this range
        count = db.query(Ticket).filter(
            Ticket.created_at >= start_of_week,
            Ticket.created_at < end_of_week
        ).count()
        
        trends.append({
            "week_label": f"Week {4-i}", # Week 4, Week 3...
            "count": count
        })
    
    # Reverse so Week 1 comes first
    return trends[::-1]