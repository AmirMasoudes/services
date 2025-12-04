"""
Tickets endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.ticket import ticket_crud
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.dependencies import get_current_user, get_current_admin
from app.models.ticket import TicketStatus
from app.services.notification import NotificationService

router = APIRouter()


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new ticket
    """
    # Check if user is admin or creating for themselves
    if ticket_data.user_id and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create tickets for other users"
        )
    
    user_id = ticket_data.user_id if ticket_data.user_id else current_user["id"]
    
    # Create ticket
    ticket_dict = ticket_data.model_dump()
    ticket_dict["user_id"] = user_id
    ticket = await ticket_crud.create(db, ticket_dict)
    
    return ticket


@router.get("", response_model=PaginatedResponse[TicketListResponse])
async def get_tickets(
    pagination: PaginationParams = Depends(),
    user_id: Optional[int] = Query(None),
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of tickets with pagination
    """
    # Non-admins can only see their own tickets
    if current_user["role"] != "admin":
        user_id = current_user["id"]
    
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if status_filter:
        filters["status"] = status_filter
    
    tickets, total = await ticket_crud.get_multi(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters
    )
    
    # Add user info
    ticket_list = []
    for ticket in tickets:
        ticket_dict = {
            "id": ticket.id,
            "user_id": ticket.user_id,
            "message": ticket.message,
            "answer": ticket.answer,
            "status": ticket.status,
            "telegram_message_id": ticket.telegram_message_id,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "username": ticket.user.username if ticket.user else None,
        }
        ticket_list.append(TicketListResponse(**ticket_dict))
    
    return PaginatedResponse.create(ticket_list, total, pagination.page, pagination.page_size)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get ticket by ID
    """
    ticket = await ticket_crud.get_with_relations(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Non-admins can only see their own tickets
    if current_user["role"] != "admin" and ticket.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Update ticket (Admin only) - Answer ticket
    """
    ticket = await ticket_crud.get_with_relations(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    update_data = ticket_data.model_dump(exclude_unset=True)
    
    # If answer is provided, send to Telegram
    if "answer" in update_data and update_data["answer"]:
        updated_ticket = await ticket_crud.update(db, ticket, update_data)
        
        # Send answer to Telegram
        notification_service = NotificationService()
        if ticket.user.tg_id:
            await notification_service.send_ticket_answer(
                ticket.user.tg_id,
                ticket.telegram_message_id,
                update_data["answer"]
            )
        
        return updated_ticket
    
    updated_ticket = await ticket_crud.update(db, ticket, update_data)
    return updated_ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Delete ticket (Admin only)
    """
    deleted = await ticket_crud.delete(db, ticket_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

