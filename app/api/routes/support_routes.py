"""
Support API Routes for Nomadly3 - Customer Support
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from fresh_database import get_db_session
from app.schemas.support_schemas import (
    SupportTicketRequest,
    SupportTicketResponse,
    FAQResponse,
    ContactInfoResponse
)
from app.services.support_service import SupportService

router = APIRouter(prefix="/api/v1/support", tags=["support"])

def get_db():
    """Get database session"""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

@router.get("/faq", response_model=List[FAQResponse])
async def get_faq(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get FAQ entries"""
    support_service = SupportService(db)
    
    try:
        faqs = await support_service.get_faq_by_category(category)
        return [FAQResponse(**faq) for faq in faqs]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tickets", response_model=SupportTicketResponse)
async def create_support_ticket(
    request: SupportTicketRequest,
    db: Session = Depends(get_db)
):
    """Create a new support ticket"""
    support_service = SupportService(db)
    
    try:
        ticket = await support_service.create_support_ticket(
            telegram_id=request.telegram_id,
            subject=request.subject,
            message=request.message,
            category=request.category
        )
        return SupportTicketResponse(**ticket)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/contact", response_model=ContactInfoResponse)
async def get_contact_info():
    """Get contact information"""
    return ContactInfoResponse(
        telegram_support="@nomadly_support",
        email_support="support@nomadly.offshore",
        response_time="24 hours",
        available_languages=["English", "French"]
    )

# Export router for import compatibility
support_router = router