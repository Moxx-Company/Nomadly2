"""
Support Tickets API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from app.core.dependencies import get_support_service
from app.core.auth import get_current_user
from app.services.support_service import SupportService

logger = logging.getLogger(__name__)

support_tickets_router = APIRouter(prefix="/support", tags=["support"])

@support_tickets_router.get("/tickets/{ticket_id}")
async def get_support_ticket_details(
    ticket_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
) -> Dict[str, Any]:
    """Get detailed support ticket information"""
    try:
        logger.info(f"Getting ticket details for ticket: {ticket_id}")
        
        ticket = await support_service.get_ticket_details(
            ticket_id=ticket_id,
            telegram_id=current_user["telegram_id"]
        )
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Support ticket not found or access denied"
            )
        
        return {
            "success": True,
            "ticket": ticket,
            "message": "Ticket details retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ticket details error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ticket details"
        )

# Export router for import compatibility
router = support_tickets_router