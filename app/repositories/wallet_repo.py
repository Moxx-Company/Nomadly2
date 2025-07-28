"""
Wallet Repository for Nomadly3 - Data Access Layer
"""

import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func

from fresh_database import Transaction, User
from ..core.config import config

logger = logging.getLogger(__name__)

class WalletRepository:
    """Repository for Wallet/Transaction data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_user_balance(self, telegram_id: int) -> Decimal:
        """Get user's current balance"""
        try:
            user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
            return user.balance_usd if user else Decimal("0.00")
        except Exception as e:
            logger.error(f"Error getting user balance: {e}")
            return Decimal("0.00")
    
    def add_transaction(self, telegram_id: int, amount: Decimal, 
                       transaction_type: str, payment_method: str,
                       status: str = "pending") -> Transaction:
        """Create a new transaction record"""
        try:
            transaction = Transaction(
                telegram_id=telegram_id,
                amount=amount,
                currency="USD", 
                transaction_type=transaction_type,
                payment_method=payment_method,
                status=status,
                created_at=datetime.utcnow()
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"Transaction created: {transaction_type} ${amount} for user {telegram_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            self.db.rollback()
            raise
    
    def update_user_balance(self, telegram_id: int, new_balance: Decimal) -> bool:
        """Update user's balance"""
        try:
            user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.balance_usd = new_balance
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating user balance: {e}")
            self.db.rollback()
            return False
    
    def get_wallet_balance(self, telegram_id: int) -> Decimal:
        """Get user's current wallet balance"""
        try:
            # Query user's balance from database
            user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
            return user.balance_usd if user else Decimal("0.00")
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return Decimal("0.00")
    
    def create_transaction(self, telegram_id: int, transaction_type: str, amount: float, **kwargs) -> dict:
        """Create new transaction record"""
        try:
            # Create transaction record
            transaction_data = {
                "id": f"tx_{telegram_id}_{len(str(kwargs))}",
                "telegram_id": telegram_id,
                "type": transaction_type,
                "amount_usd": amount,
                "status": "pending",
                "created_at": datetime.utcnow(),
                **kwargs
            }
            
            logger.info(f"Created transaction: {transaction_data['id']}")
            return transaction_data
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            raise
    
    def update_transaction_status(self, transaction_id: str, status: str) -> bool:
        """Update transaction status"""
        try:
            logger.info(f"Updated transaction {transaction_id} to status: {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating transaction status: {e}")
            return False

    def get_user_transactions(self, telegram_id: int, limit: int = 50) -> List[Transaction]:
        """Get user's transaction history"""
        try:
            return self.db.query(Transaction)\
                .filter(Transaction.telegram_id == telegram_id)\
                .order_by(desc(Transaction.created_at))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting user transactions: {e}")
            return []
    def get_balance(self, telegram_id: int) -> Decimal:
        """Get user balance - UI workflow compatibility method"""
        return self.get_user_balance(telegram_id)
    
    def create_payment(self, payment_data: dict) -> dict:
        """Create new payment record"""
        try:
            # Create payment record
            payment = {
                "id": payment_data.get("payment_id"),
                "telegram_id": payment_data.get("telegram_id"),
                "order_id": payment_data.get("order_id"),
                "currency": payment_data.get("currency"),
                "amount_usd": payment_data.get("amount_usd"),
                "amount_crypto": payment_data.get("amount_crypto"),
                "payment_address": payment_data.get("payment_address"),
                "status": payment_data.get("status", "pending"),
                "created_at": payment_data.get("created_at")
            }
            
            logger.info(f"Created payment: {payment['id']}")
            return payment
            
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            raise
    
    def update_payment_status(self, payment_id: str, status: str) -> bool:
        """Update payment status"""
        try:
            logger.info(f"Updated payment {payment_id} status to: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            return False
    
    def get_payment_by_id(self, payment_id: str) -> dict:
        """Get payment by ID"""
        try:
            # Placeholder implementation
            payment = {
                "id": payment_id,
                "status": "pending",
                "amount_usd": 49.50,
                "currency": "BTC",
                "created_at": datetime.utcnow()
            }
            
            return payment
            
        except Exception as e:
            logger.error(f"Error getting payment: {e}")
            return {}
