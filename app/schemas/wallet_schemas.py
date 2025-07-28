"""
Wallet Pydantic schemas for Nomadly3 API
"""

from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

class WalletTransactionBase(BaseModel):
    """Base wallet transaction schema"""
    transaction_type: str
    amount: Decimal
    payment_method: Optional[str] = None
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v):
        valid_types = ['deposit', 'withdrawal', 'payment', 'refund', 'bonus']
        if v not in valid_types:
            raise ValueError(f'Transaction type must be one of: {valid_types}')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class WalletTransactionCreate(WalletTransactionBase):
    """Schema for creating wallet transaction"""
    payment_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class WalletTransactionResponse(WalletTransactionBase):
    """Schema for wallet transaction responses"""
    id: int
    telegram_id: int
    status: str
    payment_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    """Base order schema"""
    service: str
    amount_usd: Decimal
    payment_method: Optional[str] = None
    
    @field_validator('service')
    @classmethod
    def validate_service(cls, v):
        valid_services = ['domain_registration', 'domain_renewal', 'dns_management', 'wallet_deposit']
        if v not in valid_services:
            raise ValueError(f'Service must be one of: {valid_services}')
        return v
    
    @field_validator('amount_usd')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class OrderCreate(OrderBase):
    """Schema for creating order"""
    telegram_id: int
    order_id: str
    service_details: Optional[Dict[str, Any]] = None

class OrderResponse(OrderBase):
    """Schema for order responses"""
    id: int
    telegram_id: int
    order_id: str
    status: str
    service_details: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WalletBalanceResponse(BaseModel):
    """Schema for wallet balance response"""
    telegram_id: int
    balance_usd: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    pending_transactions: int
    last_transaction_date: Optional[datetime] = None

class PaymentMethodResponse(BaseModel):
    """Schema for payment method information"""
    method_id: str
    name: str
    type: str  # 'cryptocurrency', 'wallet'
    is_active: bool
    fees: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, Any]] = None

class CryptocurrencyResponse(BaseModel):
    """Schema for cryptocurrency information"""
    symbol: str
    name: str
    network: str
    is_active: bool
    min_deposit: Optional[Decimal] = None
    confirmation_blocks: Optional[int] = None
    estimated_time: Optional[str] = None

class DepositRequest(BaseModel):
    """Schema for deposit request"""
    amount: Decimal
    cryptocurrency: str
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Deposit amount must be positive')
        return v
    
    @field_validator('cryptocurrency')
    @classmethod
    def validate_cryptocurrency(cls, v):
        valid_cryptos = ['btc', 'eth', 'ltc', 'doge']
        if v.lower() not in valid_cryptos:
            raise ValueError(f'Cryptocurrency must be one of: {valid_cryptos}')
        return v.lower()

class PaymentStatusResponse(BaseModel):
    """Schema for payment status response"""
    order_id: str
    status: str
    amount_expected: Decimal
    amount_received: Optional[Decimal] = None
    payment_address: Optional[str] = None
    confirmations: Optional[int] = None
    estimated_completion: Optional[datetime] = None
    transaction_hash: Optional[str] = None

class PaymentInitiationRequest(BaseModel):
    """Schema for payment initiation request"""
    amount: Decimal
    currency: str
    service: str
    service_details: Optional[Dict[str, Any]] = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Payment amount must be positive')
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        valid_currencies = ['btc', 'eth', 'ltc', 'doge', 'usd']
        if v.lower() not in valid_currencies:
            raise ValueError(f'Currency must be one of: {valid_currencies}')
        return v.lower()
    
    @field_validator('service')
    @classmethod
    def validate_service(cls, v):
        valid_services = ['domain_registration', 'domain_renewal', 'wallet_deposit', 'dns_management']
        if v not in valid_services:
            raise ValueError(f'Service must be one of: {valid_services}')
        return v

class PaymentResponse(BaseModel):
    """Schema for payment response"""
    payment_id: str
    order_id: str
    amount: Decimal
    currency: str
    payment_address: str
    qr_code_data: Optional[str] = None
    status: str
    expires_at: Optional[datetime] = None
    created_at: datetime

class PaymentConfirmationRequest(BaseModel):
    """Schema for payment confirmation request"""
    payment_id: str
    transaction_hash: Optional[str] = None
    
    @field_validator('payment_id')
    @classmethod
    def validate_payment_id(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Invalid payment ID')
        return v

class PaymentHistoryResponse(BaseModel):
    """Schema for payment history response"""
    payments: list[PaymentResponse]
    total: int
    page: int = 1
    per_page: int = 50
    total_pages: int
    
    @classmethod
    def create(cls, payments: list[PaymentResponse], total: int, page: int = 1, per_page: int = 50):
        """Create a payment history response with pagination info"""
        total_pages = (total + per_page - 1) // per_page
        return cls(
            payments=payments,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )