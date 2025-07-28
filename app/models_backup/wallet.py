"""
Wallet and Transaction models for Nomadly3 Domain Registration Bot
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, BIGINT, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List

from ..core.database import Base

class WalletTransaction(Base):
    """Wallet transaction history and payment tracking"""

    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # deposit, withdrawal, payment, refund
    amount = Column(DECIMAL(10, 2), nullable=False)  # Amount in USD
    currency = Column(String(10), default="USD")  # USD, BTC, ETH, etc.
    
    # Transaction status
    status = Column(String(20), default="pending")  # pending, completed, failed, cancelled
    
    # Payment method details
    payment_method = Column(String(50))  # wallet, btc, eth, ltc, doge, etc.
    payment_address = Column(String(255))  # Cryptocurrency address if applicable
    payment_txid = Column(String(255))  # Blockchain transaction ID
    
    # Order/service connection
    order_id = Column(String(100))  # Associated order ID
    service_type = Column(String(50))  # domain_registration, dns_management, etc.
    service_details = Column(JSONB, default={})  # Additional service information
    
    # Financial details
    exchange_rate = Column(DECIMAL(15, 8))  # Exchange rate at time of transaction
    fee_amount = Column(DECIMAL(10, 2), default=0.00)  # Transaction fee
    net_amount = Column(DECIMAL(10, 2))  # Net amount after fees
    
    # External service integration
    blockbee_payment_id = Column(String(255))  # BlockBee payment ID
    external_reference = Column(String(255))  # External payment reference
    
    # Timestamps
    initiated_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)  # Payment expiration
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="wallet_transactions")

    def __repr__(self):
        return f"<WalletTransaction(type={self.transaction_type}, amount={self.amount}, status={self.status})>"

    @property
    def is_completed(self) -> bool:
        """Check if transaction is completed"""
        return self.status == "completed"

    @property
    def is_pending(self) -> bool:
        """Check if transaction is pending"""
        return self.status == "pending"

    @property
    def is_failed(self) -> bool:
        """Check if transaction failed"""
        return self.status == "failed"

    @property
    def is_expired(self) -> bool:
        """Check if transaction has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_deposit(self) -> bool:
        """Check if this is a deposit transaction"""
        return self.transaction_type == "deposit"

    @property
    def is_payment(self) -> bool:
        """Check if this is a payment transaction"""
        return self.transaction_type == "payment"

    @property
    def is_refund(self) -> bool:
        """Check if this is a refund transaction"""
        return self.transaction_type == "refund"

    @property
    def uses_cryptocurrency(self) -> bool:
        """Check if transaction uses cryptocurrency"""
        crypto_methods = ["btc", "eth", "ltc", "doge", "trx", "bch"]
        return self.payment_method in crypto_methods

    def mark_completed(self, txid: str = None, completed_at: datetime = None) -> None:
        """Mark transaction as completed"""
        self.status = "completed"
        self.completed_at = completed_at or datetime.utcnow()
        if txid:
            self.payment_txid = txid

    def mark_failed(self, reason: str = None) -> None:
        """Mark transaction as failed"""
        self.status = "failed"
        if reason:
            if not self.service_details:
                self.service_details = {}
            self.service_details["failure_reason"] = reason

    def mark_cancelled(self) -> None:
        """Mark transaction as cancelled"""
        self.status = "cancelled"

    def update_payment_info(self, address: str, payment_id: str = None, expires_at: datetime = None) -> None:
        """Update payment information for cryptocurrency transactions"""
        self.payment_address = address
        if payment_id:
            self.blockbee_payment_id = payment_id
        if expires_at:
            self.expires_at = expires_at

    def get_service_detail(self, key: str, default=None):
        """Get specific detail from service_details"""
        if not self.service_details:
            return default
        return self.service_details.get(key, default)

    def set_service_detail(self, key: str, value: Any) -> None:
        """Set specific detail in service_details"""
        if not self.service_details:
            self.service_details = {}
        self.service_details[key] = value

    def calculate_net_amount(self) -> Decimal:
        """Calculate net amount after fees"""
        if self.fee_amount:
            return self.amount - self.fee_amount
        return self.amount

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            "id": self.id,
            "transaction_type": self.transaction_type,
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status,
            "payment_method": self.payment_method,
            "payment_address": self.payment_address,
            "order_id": self.order_id,
            "service_type": self.service_type,
            "initiated_at": self.initiated_at.isoformat() if self.initiated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

    @classmethod
    def get_transaction_types(cls) -> List[str]:
        """Get list of supported transaction types"""
        return ["deposit", "withdrawal", "payment", "refund"]

    @classmethod
    def get_payment_methods(cls) -> List[str]:
        """Get list of supported payment methods"""
        return ["wallet", "btc", "eth", "ltc", "doge", "trx", "bch"]

    @classmethod
    def get_status_options(cls) -> List[str]:
        """Get list of possible transaction statuses"""
        return ["pending", "completed", "failed", "cancelled"]


class Order(Base):
    """Order management for domain registrations and services"""

    __tablename__ = "orders"

    id = Column(String(100), primary_key=True)  # UUID-style order ID
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    
    # Order details
    order_type = Column(String(50), nullable=False)  # domain_registration, dns_service, etc.
    status = Column(String(20), default="pending")  # pending, processing, completed, failed, cancelled
    
    # Financial information
    amount_usd = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(10), default="USD")
    payment_method = Column(String(50))
    payment_status = Column(String(20), default="pending")
    
    # Service details
    service_details = Column(JSONB, default={})  # Domain name, DNS records, etc.
    
    # Payment integration
    blockbee_payment_id = Column(String(255))
    payment_address = Column(String(255))
    payment_received = Column(DECIMAL(15, 8), default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)

    def __repr__(self):
        return f"<Order(id={self.id}, type={self.order_type}, status={self.status})>"

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def is_completed(self) -> bool:
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"

    def get_domain_name(self) -> Optional[str]:
        """Get domain name from service details"""
        return self.service_details.get("domain_name") if self.service_details else None

    def mark_completed(self) -> None:
        """Mark order as completed"""
        self.status = "completed"
        self.payment_status = "completed"
        self.completed_at = datetime.utcnow()

    def mark_failed(self, reason: str = None) -> None:
        """Mark order as failed"""
        self.status = "failed"
        self.payment_status = "failed"
        if reason and self.service_details:
            self.service_details["failure_reason"] = reason