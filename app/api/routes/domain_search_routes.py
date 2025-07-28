"""
Domain Search API Routes for Nomadly3 - Domain Availability
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fresh_database import get_db_session
from app.schemas.domain_schemas import DomainSearchResponse
from app.services.domain_service import DomainService

router = APIRouter(prefix="/api/v1/domains", tags=["domains"])

def get_db():
    """Get database session"""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

@router.get("/search", response_model=List[DomainSearchResponse])
async def search_domains(
    query: str = Query(..., description="Domain name to search"),
    telegram_id: int = Query(..., description="User telegram ID"),
    db: Session = Depends(get_db)
):
    """Search for domain availability"""
    domain_service = DomainService(db)
    
    try:
        results = await domain_service.check_domain_availability(query, telegram_id)
        return [DomainSearchResponse(**results)]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my/{telegram_id}", response_model=List[DomainSearchResponse])  
async def get_my_domains(
    telegram_id: int,
    db: Session = Depends(get_db)
):
    """Get user's registered domains"""
    domain_service = DomainService(db)
    
    try:
        domains = await domain_service.get_user_domain_portfolio(telegram_id)
        return [DomainSearchResponse(**domain) for domain in domains]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Export router for import compatibility  
domain_search_router = router