"""
Wallet API Routes for Nomadly3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from decimal import Decimal

from ...repositories.transaction_repo import TransactionRepository
from ...services.wallet_service import WalletService
from ...schemas.wallet_schemas import (
    WalletTransactionResponse, WalletTransactionCreate,
    OrderResponse, OrderCreate, WalletBalanceResponse,
    PaymentMethodResponse, CryptocurrencyResponse
)

router = APIRouter(prefix="/api/wallet", tags=["wallet"])

def get_transaction_repository() -> TransactionRepository:
    return None

def get_wallet_service() -> WalletService:
    return None

@router.get("/users/{telegram_id}/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    telegram_id: int,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get user's wallet balance"""
    try:
        balance_data = await wallet_service.get_wallet_balance(telegram_id)
        return WalletBalanceResponse(**balance_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching wallet balance: {str(e)}"
        )

@router.get("/users/{telegram_id}/transactions", response_model=List[WalletTransactionResponse])
async def get_user_transactions(
    telegram_id: int,
    limit: int = 50,
    offset: int = 0,
    transaction_type: Optional[str] = None,
    transaction_repo: TransactionRepository = Depends(get_transaction_repository)
):
    """Get user's transaction history"""
    try:
        if transaction_type:
            transactions = transaction_repo.get_user_transactions_by_type(
                telegram_id, transaction_type, limit=limit, offset=offset
            )
        else:
            transactions = transaction_repo.get_user_transactions(
                telegram_id, limit=limit, offset=offset
            )
        
        return [WalletTransactionResponse.from_orm(tx) for tx in transactions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching transactions: {str(e)}"
        )

@router.post("/users/{telegram_id}/transactions", response_model=WalletTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    telegram_id: int,
    transaction_data: WalletTransactionCreate,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Create new wallet transaction"""
    try:
        transaction = await wallet_service.create_transaction(
            telegram_id=telegram_id,
            **transaction_data.dict()
        )
        return WalletTransactionResponse.from_orm(transaction)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating transaction: {str(e)}"
        )

@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    transaction_repo: TransactionRepository = Depends(get_transaction_repository)
):
    """Get orders with optional filtering"""
    try:
        if user_id:
            orders = transaction_repo.get_user_orders(user_id, limit=limit, offset=offset)
        elif status:
            orders = transaction_repo.get_orders_by_status(status, limit=limit, offset=offset)
        else:
            orders = transaction_repo.get_all_orders(limit=limit, offset=offset)
        
        return [OrderResponse.from_orm(order) for order in orders]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching orders: {str(e)}"
        )

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    transaction_repo: TransactionRepository = Depends(get_transaction_repository)
):
    """Get specific order"""
    order = transaction_repo.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return OrderResponse.from_orm(order)

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Create new order"""
    try:
        order = await wallet_service.create_order(**order_data.dict())
        return OrderResponse.from_orm(order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )

@router.post("/users/{telegram_id}/deposit", response_model=WalletTransactionResponse)
async def create_deposit(
    telegram_id: int,
    amount: Decimal,
    cryptocurrency: str,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Create cryptocurrency deposit"""
    try:
        transaction = await wallet_service.create_crypto_deposit(
            telegram_id=telegram_id,
            amount=amount,
            cryptocurrency=cryptocurrency
        )
        return WalletTransactionResponse.from_orm(transaction)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating deposit: {str(e)}"
        )

@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get available payment methods"""
    try:
        payment_methods = await wallet_service.get_payment_methods()
        return [PaymentMethodResponse(**method) for method in payment_methods]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching payment methods: {str(e)}"
        )

@router.get("/cryptocurrencies", response_model=List[CryptocurrencyResponse])
async def get_supported_cryptocurrencies(
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get supported cryptocurrencies"""
    try:
        cryptocurrencies = await wallet_service.get_supported_cryptocurrencies()
        return [CryptocurrencyResponse(**crypto) for crypto in cryptocurrencies]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cryptocurrencies: {str(e)}"
        )

@router.post("/orders/{order_id}/payment", response_model=OrderResponse)
async def process_payment(
    order_id: str,
    payment_method: str,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Process payment for order"""
    try:
        order = await wallet_service.process_payment(order_id, payment_method)
        return OrderResponse.from_orm(order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing payment: {str(e)}"
        )