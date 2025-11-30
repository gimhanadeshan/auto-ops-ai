"""
Tickets endpoints - CRUD operations for support tickets.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.ticket import (
    Ticket, TicketCreate, TicketUpdate, TicketStatus,
    TicketPriority, TicketCategory
)
from app.services.ticket_service import ticket_service

router = APIRouter()


@router.post("/tickets", response_model=Ticket, status_code=201)
async def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket.
    AI triage and analysis will be performed automatically.
    """
    try:
        db_ticket = ticket_service.create_ticket(db, ticket)
        return db_ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")


@router.get("/tickets", response_model=List[Ticket])
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    category: Optional[TicketCategory] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of tickets with optional filtering.
    """
    try:
        tickets = ticket_service.get_tickets(
            db,
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            category=category
        )
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tickets: {str(e)}")


@router.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific ticket by ID.
    """
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a ticket.
    """
    try:
        updated_ticket = ticket_service.update_ticket(db, ticket_id, ticket_update)
        if not updated_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return updated_ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")


@router.delete("/tickets/{ticket_id}", status_code=204)
async def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a ticket.
    """
    success = ticket_service.delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return None


@router.post("/tickets/{ticket_id}/troubleshoot", response_model=Ticket)
async def run_troubleshooting(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Run AI troubleshooting for a ticket.
    This will generate diagnostic information and troubleshooting steps.
    """
    try:
        ticket = ticket_service.run_troubleshooting(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running troubleshooting: {str(e)}")


@router.get("/tickets/stats/summary")
async def get_ticket_stats(db: Session = Depends(get_db)):
    """
    Get statistics about tickets.
    """
    try:
        stats = ticket_service.get_ticket_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
