"""
Authentication utilities for API routes
"""
from typing import Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer(auto_error=False)

async def get_current_user(token = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    # For now, return a mock user for development
    # In production, this would validate JWT tokens
    return {
        "telegram_id": 5590563715,
        "username": "test_user",
        "is_admin": False
    }