"""
Transaction Repository for Nomadly3 Domain Registration Bot
Handles wallet transactions and order data access operations
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from ..models.wallet import Transaction, Order
from ..models.user import User

class TransactionRepository:
    """Repository for transaction and order operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # Wallet Transaction Operations
    def get_user_transactions(
        self,
        telegram_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Transaction]:
        """Get user's transaction history"""
        return (
            self.db.query(Transaction)
            .filter(Transaction.telegram_id == telegram_id)
            .order_by(desc(Transaction.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_user_transactions_by_type(
        self,
        telegram_id: int,
        transaction_type: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Transaction]:
        """Get user transactions by type"""
        return (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.telegram_id == telegram_id,
                    Transaction.transaction_type == transaction_type
                )
            )
            .order_by(desc(Transaction.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        return (
            self.db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )
    
    def create_transaction(
        self,
        telegram_id: int,
        transaction_type: str,
        amount: Decimal,
        status: str = "pending",
        payment_method: Optional[str] = None,
        payment_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """Create new wallet transaction"""
        transaction = Transaction(
            telegram_id=telegram_id,
            transaction_type=transaction_type,
            amount=amount,
            status=status,
            payment_method=payment_method,
            payment_id=payment_id,
            metadata=metadata or {}
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def create(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create new transaction - Clean Architecture standard method"""
        transaction = Transaction(
            telegram_id=transaction_data.get("telegram_id"),
            transaction_type=transaction_data.get("transaction_type"),
            amount=transaction_data.get("amount"),
            status=transaction_data.get("status", "pending"),
            payment_method=transaction_data.get("payment_method"),
            payment_id=transaction_data.get("payment_id"),
            metadata=transaction_data.get("metadata", {})
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
        
    def get_by_telegram_id(self, telegram_id: int) -> List[Transaction]:
        """Get transactions by telegram ID - Clean Architecture standard method"""
        return self.get_user_transactions(telegram_id)

    def update_transaction_status(
        self,
        transaction_id: int,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Transaction]:
        """Update transaction status"""
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            return None
        
        transaction.status = status
        if metadata:
            transaction.metadata.update(metadata)
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def get_user_balance_summary(self, telegram_id: int) -> Dict[str, Any]:
        """Get user's balance summary from transactions"""
        # Calculate balance from transactions
        deposits = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.telegram_id == telegram_id,
                    Transaction.transaction_type == "deposit",
                    Transaction.status == "completed"
                )
            )
            .scalar() or Decimal('0')
        )
        
        withdrawals = (
            self.db.query(func.sum(WalletTransaction.amount))
            .filter(
                and_(
                    WalletTransaction.telegram_id == telegram_id,
                    WalletTransaction.transaction_type == "withdrawal",
                    WalletTransaction.status == "completed"
                )
            )
            .scalar() or Decimal('0')
        )
        
        return {
            'total_deposits': deposits,
            'total_withdrawals': withdrawals,
            'calculated_balance': deposits - withdrawals
        }
    
    # Order Operations
    def get_all_orders(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[Order]:
        """Get all orders"""
        return (
            self.db.query(Order)
            .order_by(desc(Order.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_user_orders(
        self,
        telegram_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Order]:
        """Get user's orders"""
        return (
            self.db.query(Order)
            .filter(Order.telegram_id == telegram_id)
            .order_by(desc(Order.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_orders_by_status(
        self,
        status: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Order]:
        """Get orders by status"""
        return (
            self.db.query(Order)
            .filter(Order.status == status)
            .order_by(desc(Order.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return (
            self.db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )
    
    def create_order(
        self,
        telegram_id: int,
        order_id: str,
        service: str,
        amount_usd: Decimal,
        status: str = "pending",
        payment_method: Optional[str] = None,
        service_details: Optional[Dict[str, Any]] = None
    ) -> Order:
        """Create new order"""
        order = Order(
            telegram_id=telegram_id,
            order_id=order_id,
            service=service,
            amount_usd=amount_usd,
            status=status,
            payment_method=payment_method,
            service_details=service_details or {}
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def update_order_status(
        self,
        order_id: str,
        status: str,
        service_details: Optional[Dict[str, Any]] = None
    ) -> Optional[Order]:
        """Update order status"""
        order = self.get_order_by_id(order_id)
        if not order:
            return None
        
        order.status = status
        if service_details:
            order.service_details.update(service_details)
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def get_pending_orders(self, hours_old: int = 24) -> List[Order]:
        """Get orders that are pending for too long"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)
        
        return (
            self.db.query(Order)
            .filter(
                and_(
                    Order.status == "pending",
                    Order.created_at < cutoff_time
                )
            )
            .order_by(Order.created_at)
            .all()
        )
    
    def get_revenue_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get revenue statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Completed orders revenue
        total_revenue = (
            self.db.query(func.sum(Order.amount_usd))
            .filter(
                and_(
                    Order.status == "completed",
                    Order.created_at >= cutoff_date
                )
            )
            .scalar() or Decimal('0')
        )
        
        # Order count
        order_count = (
            self.db.query(func.count(Order.id))
            .filter(
                and_(
                    Order.status == "completed",
                    Order.created_at >= cutoff_date
                )
            )
            .scalar() or 0
        )
        
        # Average order value
        avg_order_value = total_revenue / order_count if order_count > 0 else Decimal('0')
        
        return {
            'total_revenue': total_revenue,
            'order_count': order_count,
            'average_order_value': avg_order_value,
            'period_days': days
        }
    
    def get_payment_method_stats(self) -> List[Dict[str, Any]]:
        """Get payment method usage statistics"""
        stats = (
            self.db.query(
                Order.payment_method,
                func.count(Order.id).label('count'),
                func.sum(Order.amount_usd).label('total_amount')
            )
            .filter(Order.status == "completed")
            .group_by(Order.payment_method)
            .order_by(desc('count'))
            .all()
        )
        
        return [
            {
                'payment_method': stat.payment_method,
                'order_count': stat.count,
                'total_amount': stat.total_amount
            }
            for stat in stats
        ]
    
    def cleanup_old_pending_transactions(self, days_old: int = 7) -> int:
        """Clean up old pending transactions"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted_count = (
            self.db.query(WalletTransaction)
            .filter(
                and_(
                    WalletTransaction.status == "pending",
                    WalletTransaction.created_at < cutoff_date
                )
            )
            .delete()
        )
        
        self.db.commit()
        return deleted_count