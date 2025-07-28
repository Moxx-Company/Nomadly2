"""
Payment Repository - Data Access Layer for Payment Operations
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PaymentRepository:
    """Repository for payment data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new payment record"""
        try:
            from database import WalletTransaction
            
            payment = WalletTransaction(
                telegram_id=payment_data['telegram_id'],
                amount_usd=payment_data.get('amount_usd', 0.0),
                cryptocurrency=payment_data.get('cryptocurrency'),
                crypto_amount=payment_data.get('crypto_amount'),
                crypto_address=payment_data.get('crypto_address'),
                transaction_type=payment_data.get('transaction_type', 'payment'),
                status=payment_data.get('status', 'pending'),
                order_id=payment_data.get('order_id'),
                created_at=datetime.now()
            )
            
            self.db.add(payment)
            self.db.commit()
            
            logger.info(f"Created payment: {payment.id}")
            return self._payment_to_dict(payment)
            
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            self.db.rollback()
            return None
    
    def update_payment_status(self, payment_id: int, status: str, **kwargs) -> bool:
        """Update payment status and additional fields"""
        try:
            from database import WalletTransaction
            
            payment = self.db.query(WalletTransaction).filter(
                WalletTransaction.id == payment_id
            ).first()
            
            if not payment:
                logger.warning(f"Payment not found: {payment_id}")
                return False
            
            # Update status
            payment.status = status
            payment.updated_at = datetime.now()
            
            # Update additional fields
            for key, value in kwargs.items():
                if hasattr(payment, key):
                    setattr(payment, key, value)
            
            self.db.commit()
            logger.info(f"Updated payment {payment_id} status to: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            self.db.rollback()
            return False
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Dict[str, Any]]:
        """Get payment by ID"""
        try:
            from database import WalletTransaction
            
            payment = self.db.query(WalletTransaction).filter(
                WalletTransaction.id == payment_id
            ).first()
            
            if payment:
                return self._payment_to_dict(payment)
            return None
            
        except Exception as e:
            logger.error(f"Error getting payment by ID: {e}")
            return None
    
    def get_payment_by_order_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get payment by order ID"""
        try:
            from database import WalletTransaction
            
            payment = self.db.query(WalletTransaction).filter(
                WalletTransaction.order_id == order_id
            ).first()
            
            if payment:
                return self._payment_to_dict(payment)
            return None
            
        except Exception as e:
            logger.error(f"Error getting payment by order ID: {e}")
            return None
    
    def get_user_payments(self, telegram_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user's payment history"""
        try:
            from database import WalletTransaction
            
            payments = self.db.query(WalletTransaction).filter(
                WalletTransaction.telegram_id == telegram_id
            ).order_by(desc(WalletTransaction.created_at)).limit(limit).offset(offset).all()
            
            return [self._payment_to_dict(payment) for payment in payments]
            
        except Exception as e:
            logger.error(f"Error getting user payments: {e}")
            return []
    
    def get_pending_payments(self, older_than_minutes: int = 5) -> List[Dict[str, Any]]:
        """Get pending payments older than specified minutes"""
        try:
            from database import WalletTransaction
            
            cutoff_time = datetime.now() - timedelta(minutes=older_than_minutes)
            
            payments = self.db.query(WalletTransaction).filter(
                and_(
                    WalletTransaction.status == 'pending',
                    WalletTransaction.created_at < cutoff_time
                )
            ).all()
            
            return [self._payment_to_dict(payment) for payment in payments]
            
        except Exception as e:
            logger.error(f"Error getting pending payments: {e}")
            return []
    
    def get_payments_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get payments by status"""
        try:
            from database import WalletTransaction
            
            payments = self.db.query(WalletTransaction).filter(
                WalletTransaction.status == status
            ).order_by(desc(WalletTransaction.created_at)).limit(limit).all()
            
            return [self._payment_to_dict(payment) for payment in payments]
            
        except Exception as e:
            logger.error(f"Error getting payments by status: {e}")
            return []
    
    def update_payment_confirmation(self, order_id: str, tx_hash: str, confirmations: int) -> bool:
        """Update payment with transaction confirmation details"""
        try:
            from database import WalletTransaction
            
            payment = self.db.query(WalletTransaction).filter(
                WalletTransaction.order_id == order_id
            ).first()
            
            if not payment:
                return False
            
            # Update confirmation details
            payment.tx_hash = tx_hash
            payment.confirmations = confirmations
            payment.updated_at = datetime.now()
            
            # Update status based on confirmations
            if confirmations > 0:
                payment.status = 'confirmed'
            
            self.db.commit()
            logger.info(f"Updated payment confirmation: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating payment confirmation: {e}")
            self.db.rollback()
            return False
    
    def get_payment_statistics(self, telegram_id: Optional[int] = None) -> Dict[str, Any]:
        """Get payment statistics"""
        try:
            from database import WalletTransaction
            from sqlalchemy import func
            
            query = self.db.query(WalletTransaction)
            if telegram_id:
                query = query.filter(WalletTransaction.telegram_id == telegram_id)
            
            # Basic counts
            total_payments = query.count()
            confirmed_payments = query.filter(WalletTransaction.status == 'confirmed').count()
            pending_payments = query.filter(WalletTransaction.status == 'pending').count()
            
            # Amount statistics
            total_amount = query.with_entities(
                func.sum(WalletTransaction.amount_usd)
            ).scalar() or 0.0
            
            confirmed_amount = query.filter(
                WalletTransaction.status == 'confirmed'
            ).with_entities(
                func.sum(WalletTransaction.amount_usd)
            ).scalar() or 0.0
            
            return {
                'total_payments': total_payments,
                'confirmed_payments': confirmed_payments,
                'pending_payments': pending_payments,
                'total_amount_usd': float(total_amount),
                'confirmed_amount_usd': float(confirmed_amount),
                'success_rate': (confirmed_payments / total_payments * 100) if total_payments > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting payment statistics: {e}")
            return {}
    
    def cleanup_expired_payments(self, hours_old: int = 24) -> int:
        """Clean up expired pending payments"""
        try:
            from database import WalletTransaction
            
            cutoff_time = datetime.now() - timedelta(hours=hours_old)
            
            expired_count = self.db.query(WalletTransaction).filter(
                and_(
                    WalletTransaction.status == 'pending',
                    WalletTransaction.created_at < cutoff_time
                )
            ).update({'status': 'expired'})
            
            self.db.commit()
            logger.info(f"Cleaned up {expired_count} expired payments")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired payments: {e}")
            self.db.rollback()
            return 0
    
    def _payment_to_dict(self, payment) -> Dict[str, Any]:
        """Convert payment model to dictionary"""
        return {
            'id': payment.id,
            'telegram_id': payment.telegram_id,
            'amount_usd': float(payment.amount_usd),
            'cryptocurrency': payment.cryptocurrency,
            'crypto_amount': float(payment.crypto_amount) if payment.crypto_amount else None,
            'crypto_address': payment.crypto_address,
            'transaction_type': payment.transaction_type,
            'status': payment.status,
            'order_id': payment.order_id,
            'tx_hash': getattr(payment, 'tx_hash', None),
            'confirmations': getattr(payment, 'confirmations', 0),
            'created_at': payment.created_at.isoformat() if payment.created_at else None,
            'updated_at': getattr(payment, 'updated_at', None)
        }