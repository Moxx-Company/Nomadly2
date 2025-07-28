"""
User Language API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from app.core.dependencies import get_user_service
from app.core.auth import get_current_user
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

user_language_router = APIRouter(prefix="/users", tags=["users"])

@user_language_router.put("/{telegram_id}/language")
async def update_user_language(
    telegram_id: int,
    language_code: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """Update user language preference"""
    try:
        logger.info(f"Updating language for user {telegram_id} to: {language_code}")
        
        # Verify user access
        if current_user["telegram_id"] != telegram_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        result = await user_service.update_language_preference(
            telegram_id=telegram_id,
            language_code=language_code
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Language update failed")
            )
        
        return {
            "success": True,
            "user": result["user"],
            "message": f"Language updated to {language_code}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Language update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Language update failed"
        )

# Export router for import compatibility
router = user_language_router