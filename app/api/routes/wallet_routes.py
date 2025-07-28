
"""
Wallet API Routes for Nomadly3 - Financial Management
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from fresh_database import get_db_session
from app.schemas.wallet_schemas import (
    WalletBalanceResponse,
    TransactionRequest,
    TransactionResponse,
    TransactionHistoryResponse,
    AddFundsRequest,
    AddFundsResponse,
    WalletStatusResponse
)
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/api/v1/wallet", tags=["wallet"])

def get_db():
    """Get database session"""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/add", response_model=AddFundsResponse)
async def add_funds(
    request: AddFundsRequest,
    db: Session = Depends(get_db)
):
    """Add funds to wallet via cryptocurrency payment"""
    wallet_service = WalletService(db)
    
    try:
        payment_request = await wallet_service.create_payment_request(
            telegram_id=request.telegram_id,
            amount_usd=request.amount_usd,
            cryptocurrency=request.cryptocurrency,
            payment_method=request.payment_method
        )
        
        return AddFundsResponse(
            success=True,
            payment_id=payment_request["payment_id"],
            payment_address=payment_request["address"],
            amount_crypto=payment_request["amount_crypto"],
            qr_code_data=payment_request["qr_code"],
            expires_at=payment_request["expires_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{telegram_id}", response_model=WalletStatusResponse)
async def get_wallet_status(
    telegram_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive wallet status including balance and recent activity"""
    wallet_service = WalletService(db)
    
    try:
        status = await wallet_service.get_wallet_status(telegram_id)
        return WalletStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/transactions/{telegram_id}", response_model=List[TransactionResponse])
async def get_transactions(
    telegram_id: int,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get transaction history for user"""
    wallet_service = WalletService(db)
    
    try:
        transactions = await wallet_service.get_transaction_history(
            telegram_id=telegram_id,
            limit=limit,
            offset=offset
        )
        return [TransactionResponse(**tx) for tx in transactions]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/balance/{telegram_id}", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    telegram_id: int,
    db: Session = Depends(get_db)
):
    """Get wallet balance for user"""
    wallet_service = WalletService(db)
    balance = await wallet_service.get_balance(telegram_id)
    
    if balance is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return WalletBalanceResponse(
        telegram_id=telegram_id,
        balance_usd=balance,
        available_balance=balance
    )

# Export router for import compatibility
wallet_router = router
