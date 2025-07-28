"""
User API Routes for Nomadly3 - User Management
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from fresh_database import get_db_session
from app.schemas.user_schemas import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserProfileResponse,
    DashboardResponse
)
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])

def get_db():
    """Get database session"""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(
    request: UserRegistrationRequest,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    user_service = UserService(db)
    
    try:
        result = await user_service.create_user(
            telegram_id=request.telegram_id,
            username=request.username,
            language=request.language,
            initial_balance=request.initial_balance or 0.0
        )
        return UserRegistrationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profile/{telegram_id}", response_model=UserProfileResponse)
async def get_user_profile(
    telegram_id: int,
    db: Session = Depends(get_db)
):
    """Get user profile information"""
    user_service = UserService(db)
    
    try:
        profile = await user_service.get_user_profile(telegram_id)
        return UserProfileResponse(**profile)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/dashboard/{telegram_id}", response_model=DashboardResponse)
async def get_dashboard(
    telegram_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard data"""
    user_service = UserService(db)
    
    try:
        dashboard = await user_service.get_complete_dashboard_summary(telegram_id)
        return DashboardResponse(**dashboard)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Export router for import compatibility
user_router = router