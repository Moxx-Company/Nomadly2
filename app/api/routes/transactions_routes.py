"""
Transactions API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import logging
from app.core.dependencies import get_wallet_service
from app.core.auth import get_current_user
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])

@transactions_router.get("/{telegram_id}")
async def get_user_transactions(
    telegram_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    wallet_service: WalletService = Depends(get_wallet_service)
) -> Dict[str, Any]:
    """Get user transaction history"""
    try:
        logger.info(f"Getting transactions for user: {telegram_id}")
        
        # Verify user access
        if current_user["telegram_id"] != telegram_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        transactions = await wallet_service.get_transaction_history(
            telegram_id=telegram_id,
            limit=limit
        )
        
        return {
            "success": True,
            "transactions": transactions,
            "total_count": len(transactions),
            "message": "Transaction history retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transaction history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction history"
        )

# Export router for import compatibility
router = transactions_router