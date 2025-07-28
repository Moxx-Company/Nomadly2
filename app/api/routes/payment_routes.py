"""
Payment Processing Routes for Nomadly3 API
FastAPI router for payment operations (initiate, confirm, webhook)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Dict, Any, List, Optional
import logging

from ...schemas.wallet_schemas import (
    PaymentInitiationRequest, PaymentResponse, PaymentConfirmationRequest,
    WalletBalanceResponse, PaymentHistoryResponse
)
from ...services.payment_service import PaymentService
from ...services.wallet_service import WalletService
from ...repositories.transaction_repo import TransactionRepository
from ...repositories.user_repo import UserRepository
from ...core.database import get_db_session
from .auth_routes import get_current_user

logger = logging.getLogger(__name__)

# Create router
payment_router = APIRouter(
    prefix="/payments",
    tags=["Payment Processing"],
    responses={404: {"description": "Not found"}}
)

def get_payment_service() -> PaymentService:
    """Dependency injection for PaymentService"""
    db_session = get_db_session()
    transaction_repo = TransactionRepository(db_session)
    user_repo = UserRepository(db_session)
    return PaymentService(transaction_repo, user_repo)

def get_wallet_service() -> WalletService:
    """Dependency injection for WalletService"""
    db_session = get_db_session()
    user_repo = UserRepository(db_session)
    transaction_repo = TransactionRepository(db_session)
    return WalletService(user_repo, transaction_repo)

@payment_router.post("/initiate", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def initiate_payment(
    payment_request: PaymentInitiationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
) -> Dict[str, Any]:
    """
    Initiate cryptocurrency payment
    
    Creates payment address and order for domain registration or wallet funding
    """
    try:
        logger.info(f"Initiating payment for user: {current_user['telegram_id']}, amount: ${payment_request.amount_usd}")
        
        result = payment_service.create_cryptocurrency_payment(
            telegram_id=current_user["telegram_id"],
            amount_usd=payment_request.amount_usd,
            cryptocurrency=payment_request.cryptocurrency,
            purpose=payment_request.purpose,
            domain_name=payment_request.domain_name,
            metadata=payment_request.metadata or {}
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Payment initiation failed")
            )
        
        return {
            "success": True,
            "payment": result["payment"],
            "message": f"{payment_request.cryptocurrency} payment initiated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment initiation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment initiation failed"
        )

@payment_router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment_status(
    payment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
) -> Dict[str, Any]:
    """
    Get payment status and details
    
    Returns current payment status with transaction information
    """
    try:
        logger.info(f"Getting payment status: {payment_id} for user: {current_user['telegram_id']}")
        
        result = payment_service.get_payment_status(
            payment_id=payment_id,
            telegram_id=current_user["telegram_id"]
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Payment not found")
            )
        
        return {
            "success": True,
            "payment": result["payment"],
            "message": "Payment status retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment status"
        )

@payment_router.post("/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: str,
    confirmation_request: PaymentConfirmationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
) -> Dict[str, Any]:
    """
    Manually confirm payment
    
    Allows manual confirmation of payment with transaction hash
    """
    try:
        logger.info(f"Confirming payment: {payment_id} for user: {current_user['telegram_id']}")
        
        result = payment_service.confirm_payment_manually(
            payment_id=payment_id,
            telegram_id=current_user["telegram_id"],
            transaction_hash=confirmation_request.transaction_hash,
            amount_received=confirmation_request.amount_received
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Payment confirmation failed")
            )
        
        return {
            "success": True,
            "payment": result["payment"],
            "message": "Payment confirmed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment confirmation failed"
        )

@payment_router.get("/", response_model=PaymentHistoryResponse)
async def get_payment_history(
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Payments per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, completed, failed"),
    purpose_filter: Optional[str] = Query(None, description="Filter by purpose: domain_registration, wallet_funding")
) -> Dict[str, Any]:
    """
    Get user payment history
    
    Returns paginated list of user's payment transactions
    """
    try:
        logger.info(f"Getting payment history for user: {current_user['telegram_id']}")
        
        result = payment_service.get_user_payment_history(
            telegram_id=current_user["telegram_id"],
            page=page,
            limit=limit,
            status_filter=status_filter,
            purpose_filter=purpose_filter
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to retrieve payment history")
            )
        
        return {
            "success": True,
            "payments": result["payments"],
            "pagination": result["pagination"],
            "message": f"Retrieved {len(result['payments'])} payments"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment history"
        )

@payment_router.get("/wallet/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    current_user: Dict[str, Any] = Depends(get_current_user),
    wallet_service: WalletService = Depends(get_wallet_service)
) -> Dict[str, Any]:
    """
    Get current wallet balance
    
    Returns user's current USD wallet balance and recent transactions
    """
    try:
        logger.info(f"Getting wallet balance for user: {current_user['telegram_id']}")
        
        result = wallet_service.get_user_balance_details(
            telegram_id=current_user["telegram_id"]
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "User not found")
            )
        
        return {
            "success": True,
            "balance": result["balance"],
            "message": "Wallet balance retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wallet balance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wallet balance"
        )

@payment_router.post("/wallet/deduct", response_model=WalletBalanceResponse)
async def deduct_from_wallet(
    current_user: Dict[str, Any] = Depends(get_current_user),
    wallet_service: WalletService = Depends(get_wallet_service),
    amount: float = Query(..., gt=0, description="Amount to deduct from wallet"),
    description: str = Query(..., description="Description for the transaction")
) -> Dict[str, Any]:
    """
    Deduct amount from wallet balance
    
    Used for domain registrations paid with wallet balance
    """
    try:
        logger.info(f"Deducting ${amount} from wallet for user: {current_user['telegram_id']}")
        
        result = wallet_service.deduct_balance(
            telegram_id=current_user["telegram_id"],
            amount=amount,
            description=description
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Wallet deduction failed")
            )
        
        return {
            "success": True,
            "balance": result["balance"],
            "message": f"${amount} deducted from wallet successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wallet deduction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wallet deduction failed"
        )

@payment_router.get("/supported-currencies")
async def get_supported_currencies(
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
) -> Dict[str, Any]:
    """
    Get supported cryptocurrencies
    
    Returns list of available payment methods with details
    """
    try:
        currencies = payment_service.get_supported_cryptocurrencies()
        
        return {
            "success": True,
            "currencies": currencies,
            "message": f"Retrieved {len(currencies)} supported currencies"
        }
        
    except Exception as e:
        logger.error(f"Supported currencies error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supported currencies"
        )

@payment_router.post("/webhook/blockbee", status_code=status.HTTP_200_OK)
async def handle_blockbee_webhook(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service)
) -> Dict[str, Any]:
    """
    Handle BlockBee payment webhook
    
    Processes payment confirmations from BlockBee service
    """
    try:
        # Get raw request body
        body = await request.body()
        headers = dict(request.headers)
        
        logger.info("Received BlockBee webhook")
        
        result = payment_service.process_blockbee_webhook(
            webhook_data=body,
            headers=headers
        )
        
        if not result.get("success"):
            logger.warning(f"Webhook processing failed: {result.get('error')}")
            return {"success": False, "error": result.get("error", "Webhook processing failed")}
        
        return {
            "success": True,
            "message": "Webhook processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return {
            "success": False,
            "error": "Webhook processing failed"
        }

@payment_router.post("/{payment_id}/cancel", response_model=PaymentResponse)
async def cancel_payment(
    payment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
) -> Dict[str, Any]:
    """
    Cancel pending payment
    
    Cancels payment order if still pending
    """
    try:
        logger.info(f"Canceling payment: {payment_id} for user: {current_user['telegram_id']}")
        
        result = payment_service.cancel_payment(
            payment_id=payment_id,
            telegram_id=current_user["telegram_id"]
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Payment cancellation failed")
            )
        
        return {
            "success": True,
            "payment": result["payment"],
            "message": "Payment canceled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment cancellation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment cancellation failed"
        )

@payment_router.get("/stats/summary")
async def get_payment_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
) -> Dict[str, Any]:
    """
    Get payment statistics summary
    
    Returns user's payment statistics and spending summary
    """
    try:
        logger.info(f"Getting payment statistics for user: {current_user['telegram_id']}")
        
        result = payment_service.get_user_payment_statistics(
            telegram_id=current_user["telegram_id"]
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to retrieve payment statistics")
            )
        
        return {
            "success": True,
            "statistics": result["statistics"],
            "message": "Payment statistics retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment statistics"
        )
# Export router for import compatibility
router = payment_router
