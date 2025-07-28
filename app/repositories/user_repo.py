"""
User Repository for Nomadly3 - Data Access Layer
"""

import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, desc, func

from ..models.user import User
from ..models.user_state import UserState
from ..core.config import config

logger = logging.getLogger(__name__)

class UserRepository:
    """Repository for User data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        try:
            return self.db.query(User).filter(User.telegram_id == telegram_id).first()
        except Exception as e:
            logger.error(f"Error getting user by telegram_id {telegram_id}: {e}")
            return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return self.db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    def create(self, user_data: Dict[str, Any]) -> User:
        """Create a new user - Clean Architecture standard method"""
        try:
            user = User(
                telegram_id=user_data.get("telegram_id"),
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                language_code=user_data.get("language_code", "en"),
                balance_usd=user_data.get("balance_usd", Decimal("0.00")),
                is_admin=user_data.get("is_admin", False)
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created new user: {user.telegram_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            self.db.rollback()
            raise

    def create_user(self, telegram_id: int, username: Optional[str] = None, 
                   first_name: Optional[str] = None, last_name: Optional[str] = None,
                   language_code: str = "en") -> User:
        """Create a new user - Legacy method for backward compatibility"""
        return self.create({
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "language_code": language_code,
            "balance_usd": Decimal("0.00")
        })
    
    def update(self, telegram_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user data - Clean Architecture standard method"""
        try:
            user = self.get_by_telegram_id(telegram_id)
            if not user:
                return None
            
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user {telegram_id}: {list(update_data.keys())}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user {telegram_id}: {e}")
            self.db.rollback()
            return None
    
    def get_dashboard_data(self, telegram_id: int) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for Main Menu Hub UI
        Joins users + domains + transactions for complete summary
        """
        try:
            from ..models.domain import Domain
            from ..models.transaction import Transaction
            
            # Main dashboard query with joins
            dashboard_query = self.db.query(
                User.telegram_id,
                User.username,
                User.first_name,
                User.language_code,
                User.created_at,
                func.count(Domain.id.distinct()).label('domain_count'),
                func.sum(
                    func.case(
                        [(Transaction.transaction_type.in_(['payment', 'domain_purchase']), Transaction.amount)],
                        else_=0
                    )
                ).label('total_spent'),
                func.count(
                    func.case(
                        [(Domain.status == 'active', 1)],
                        else_=None
                    )
                ).label('active_domains'),
                func.count(
                    func.case(
                        [(Domain.status == 'expired', 1)],
                        else_=None
                    )
                ).label('expired_domains'),
                func.count(
                    func.case(
                        [(func.extract('day', Domain.expires_at - func.now()) <= 30, 1)],
                        else_=None
                    )
                ).label('expiring_domains'),
                func.count(
                    func.case(
                        [(Transaction.status == 'pending', 1)],
                        else_=None
                    )
                ).label('pending_transactions'),
                func.max(Transaction.created_at).label('last_transaction_date')
            ).outerjoin(
                Domain, User.telegram_id == Domain.telegram_id
            ).outerjoin(
                Transaction, User.telegram_id == Transaction.telegram_id
            ).filter(
                User.telegram_id == telegram_id
            ).group_by(
                User.telegram_id, User.username, User.first_name, 
                User.language_code, User.created_at
            ).first()
            
            if not dashboard_query:
                return {}
            
            # Get recent domains (last 3)
            recent_domains = self.db.query(Domain).filter(
                Domain.telegram_id == telegram_id
            ).order_by(desc(Domain.created_at)).limit(3).all()
            
            # Get recent transactions (last 5)
            recent_transactions = self.db.query(Transaction).filter(
                Transaction.telegram_id == telegram_id
            ).order_by(desc(Transaction.created_at)).limit(5).all()
            
            # Build comprehensive dashboard data
            dashboard_data = {
                'domain_count': dashboard_query.domain_count or 0,
                'total_spent': float(dashboard_query.total_spent or 0),
                'active_domains': dashboard_query.active_domains or 0,
                'expired_domains': dashboard_query.expired_domains or 0,
                'expiring_domains': dashboard_query.expiring_domains or 0,
                'pending_transactions': dashboard_query.pending_transactions or 0,
                'last_transaction_date': dashboard_query.last_transaction_date,
                'recent_domains': [
                    {
                        'domain_name': domain.domain_name,
                        'status': domain.status,
                        'expires_at': domain.expires_at.isoformat() if domain.expires_at else None,
                        'created_at': domain.created_at.isoformat() if domain.created_at else None
                    } for domain in recent_domains
                ],
                'recent_transactions': [
                    {
                        'transaction_type': trans.transaction_type,
                        'amount': float(trans.amount),
                        'status': trans.status,
                        'created_at': trans.created_at.isoformat() if trans.created_at else None
                    } for trans in recent_transactions
                ],
                'open_tickets': 0  # TODO: Implement support ticket system
            }
            
            logger.info(f"📊 Dashboard data retrieved for user {telegram_id}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data for {telegram_id}: {e}")
            return {}

    def update(self, telegram_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update existing user - Clean Architecture standard method"""
        try:
            user = self.get_by_telegram_id(telegram_id)
            if not user:
                return None
                
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user: {telegram_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            self.db.rollback()
            raise
    
    def update_user(self, user: User) -> User:
        """Update existing user"""
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error updating user {user.telegram_id}: {e}")
            self.db.rollback()
            raise
    
    def update_balance(self, telegram_id: int, new_balance: Decimal) -> bool:
        """Update user's balance"""
        try:
            user = self.get_by_telegram_id(telegram_id)
            if user:
                user.balance_usd = new_balance
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating balance for user {telegram_id}: {e}")
            self.db.rollback()
            return False
    
    def add_balance(self, telegram_id: int, amount: Decimal) -> bool:
        """Add amount to user's balance"""
        try:
            user = self.get_by_telegram_id(telegram_id)
            if user:
                user.add_balance(amount)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding balance for user {telegram_id}: {e}")
            self.db.rollback()
            return False
    
    def deduct_balance(self, telegram_id: int, amount: Decimal) -> bool:
        """Deduct amount from user's balance if sufficient"""
        try:
            user = self.get_by_telegram_id(telegram_id)
            if user and user.deduct_balance(amount):
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deducting balance for user {telegram_id}: {e}")
            self.db.rollback()
            return False
    
    def set_language(self, telegram_id: int, language_code: str) -> bool:
        """Set user's language preference"""
        try:
            user = self.get_by_telegram_id(telegram_id)
            if user:
                user.language_code = language_code
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting language for user {telegram_id}: {e}")
            self.db.rollback()
            return False
    
    def set_technical_email(self, telegram_id: int, email: str) -> bool:
        """Set user's technical email"""
        try:
            user = self.get_by_telegram_id(telegram_id)
            if user:
                user.technical_email = email
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting email for user {telegram_id}: {e}")
            self.db.rollback()
            return False
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Get all users with pagination"""
        try:
            return self.db.query(User)\
                .offset(offset)\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def get_admin_users(self) -> List[User]:
        """Get all admin users"""
        try:
            return self.db.query(User).filter(User.is_admin == True).all()
        except Exception as e:
            logger.error(f"Error getting admin users: {e}")
            return []
    
    def set_admin_status(self, telegram_id: int, is_admin: bool) -> bool:
        """Set user's admin status"""
        try:
            user = self.get_by_telegram_id(telegram_id)
            if user:
                user.is_admin = is_admin
                user.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting admin status for user {telegram_id}: {e}")
            self.db.rollback()
            return False
    
    # Advanced Query Methods with Joins & Relations
    
    def get_user_with_domains(self, telegram_id: int) -> Optional[User]:
        """Get user with all their domains eagerly loaded"""
        try:
            return self.db.query(User)\
                .options(joinedload(User.domains))\
                .filter(User.telegram_id == telegram_id)\
                .first()
        except Exception as e:
            logger.error(f"Error getting user with domains {telegram_id}: {e}")
            return None
    
    def get_user_with_full_data(self, telegram_id: int) -> Optional[User]:
        """Get user with domains, DNS records, and wallet transactions"""
        try:
            return self.db.query(User)\
                .options(
                    joinedload(User.domains).joinedload("dns_records"),
                    selectinload(User.wallet_transactions),
                    selectinload(User.user_states)
                )\
                .filter(User.telegram_id == telegram_id)\
                .first()
        except Exception as e:
            logger.error(f"Error getting user with full data {telegram_id}: {e}")
            return None
    
    def get_users_with_active_domains(self) -> List[User]:
        """Get all users who have active domains"""
        try:
            from ..models.domain import RegisteredDomain
            return self.db.query(User)\
                .join(RegisteredDomain)\
                .filter(RegisteredDomain.status == "active")\
                .distinct()\
                .all()
        except Exception as e:
            logger.error(f"Error getting users with active domains: {e}")
            return []
    
    def get_premium_users(self) -> List[User]:
        """Get users with 3+ domains or $100+ spent"""
        try:
            from ..models.domain import RegisteredDomain
            
            # Users with 3+ domains
            domain_count_users = self.db.query(User)\
                .join(RegisteredDomain)\
                .group_by(User.telegram_id)\
                .having(func.count(RegisteredDomain.id) >= 3)\
                .all()
            
            # Users with $100+ spent
            spending_users = self.db.query(User)\
                .join(RegisteredDomain)\
                .group_by(User.telegram_id)\
                .having(func.sum(RegisteredDomain.price_paid) >= 100.00)\
                .all()
            
            # Combine and deduplicate
            all_premium = list(set(domain_count_users + spending_users))
            return all_premium
            
        except Exception as e:
            logger.error(f"Error getting premium users: {e}")
            return []
    
    def search_users(self, query: str) -> List[User]:
        """Search users by username, first name, or last name"""
        try:
            search_term = f"%{query}%"
            return self.db.query(User)\
                .filter(
                    or_(
                        User.username.ilike(search_term),
                        User.first_name.ilike(search_term),
                        User.last_name.ilike(search_term)
                    )
                )\
                .order_by(User.username)\
                .all()
        except Exception as e:
            logger.error(f"Error searching users with query '{query}': {e}")
            return []
    
    def get_users_by_language(self, language_code: str) -> List[User]:
        """Get all users with specific language preference"""
        try:
            return self.db.query(User)\
                .filter(User.language_code == language_code)\
                .order_by(desc(User.created_at))\
                .all()
        except Exception as e:
            logger.error(f"Error getting users by language {language_code}: {e}")
            return []
    
    def get_users_with_balance_above(self, minimum_balance: Decimal) -> List[User]:
        """Get users with wallet balance above specified amount"""
        try:
            return self.db.query(User)\
                .filter(User.balance_usd >= minimum_balance)\
                .order_by(desc(User.balance_usd))\
                .all()
        except Exception as e:
            logger.error(f"Error getting users with balance above ${minimum_balance}: {e}")
            return []
    
    def get_user_statistics(self, telegram_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            user = self.get_user_with_full_data(telegram_id)
            if not user:
                return {}
            
            return {
                "user_id": user.telegram_id,
                "username": user.username,
                "total_domains": len(user.domains),
                "active_domains": len([d for d in user.domains if d.is_active]),
                "expired_domains": len([d for d in user.domains if d.is_expired]),
                "total_spent": user.get_total_spent(),
                "current_balance": user.balance_usd,
                "is_premium": user.is_premium_user(),
                "registration_date": user.created_at,
                "language": user.language_code,
                "has_email": bool(user.technical_email)
            }
        except Exception as e:
            logger.error(f"Error getting user statistics for {telegram_id}: {e}")
            return {}
    
    def get_users_by_balance_range(self, min_balance: Decimal, max_balance: Decimal) -> List[User]:
        """Get users within balance range"""
        try:
            return self.db.query(User)\
                .filter(and_(User.balance_usd >= min_balance, User.balance_usd <= max_balance))\
                .all()
        except Exception as e:
            logger.error(f"Error getting users by balance range: {e}")
            return []
    
    def search_users(self, query: str) -> List[User]:
        """Search users by username or name"""
        try:
            search_term = f"%{query}%"
            return self.db.query(User)\
                .filter(or_(
                    User.username.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                ))\
                .limit(50)\
                .all()
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    def get_user_count(self) -> int:
        """Get total user count"""
        try:
            return self.db.query(User).count()
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    def delete_user(self, telegram_id: int) -> bool:
        """Delete user and all related data"""
        try:
            user = self.get_by_telegram_id(telegram_id)
            if user:
                self.db.delete(user)
                self.db.commit()
                logger.info(f"Deleted user: {telegram_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting user {telegram_id}: {e}")
            self.db.rollback()
            return False


class UserStateRepository:
    """Repository for UserState data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_user_state(self, telegram_id: int) -> Optional[UserState]:
        """Get current user state"""
        try:
            return self.db.query(UserState)\
                .filter(UserState.telegram_id == telegram_id)\
                .first()
        except Exception as e:
            logger.error(f"Error getting user state for {telegram_id}: {e}")
            return None
    
    def set_user_state(self, telegram_id: int, state: str, data: dict = None) -> UserState:
        """Set user state"""
        try:
            user_state = self.get_user_state(telegram_id)
            
            if user_state:
                user_state.set_state(state, data)
                user_state.updated_at = datetime.utcnow()
            else:
                user_state = UserState(
                    telegram_id=telegram_id,
                    current_state=state,
                    state_data=data or {}
                )
                self.db.add(user_state)
            
            self.db.commit()
            self.db.refresh(user_state)
            return user_state
            
        except Exception as e:
            logger.error(f"Error setting user state: {e}")
            self.db.rollback()
            raise
    
    def update_state_data(self, telegram_id: int, key: str, value) -> bool:
        """Update specific key in user's state data"""
        try:
            user_state = self.get_user_state(telegram_id)
            if user_state:
                user_state.update_state_data(key, value)
                user_state.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating state data: {e}")
            self.db.rollback()
            return False
    
    def clear_user_state(self, telegram_id: int) -> bool:
        """Clear user state"""
        try:
            user_state = self.get_user_state(telegram_id)
            if user_state:
                self.db.delete(user_state)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing user state: {e}")
            self.db.rollback()
            return False
    
    def get_users_in_state(self, state: str) -> List[UserState]:
        """Get all users currently in a specific state"""
        try:
            return self.db.query(UserState)\
                .filter(UserState.current_state == state)\
                .all()
        except Exception as e:
            logger.error(f"Error getting users in state {state}: {e}")
            return []
    def update_user_language(self, telegram_id: int, language_code: str) -> bool:
        """Update user's language preference"""
        try:
            user = self.session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.language_code = language_code
                user.updated_at = datetime.utcnow()
                self.session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            self.session.rollback()
            return False
    
    def get_dashboard_data(self, telegram_id: int) -> Dict[str, Any]:
        """Get comprehensive dashboard data for user"""
        try:
            from sqlalchemy.orm import joinedload
            from sqlalchemy import func
            
            # Get user with related data pre-loaded
            user = self.session.query(User)\
                .options(joinedload(User.domains))\
                .filter(User.telegram_id == telegram_id)\
                .first()
            
            if not user:
                return {}
            
            # Get domain statistics
            total_domains = self.session.query(func.count(RegisteredDomain.id))\
                .filter(RegisteredDomain.telegram_id == telegram_id)\
                .scalar() or 0
            
            active_domains = self.session.query(func.count(RegisteredDomain.id))\
                .filter(
                    RegisteredDomain.telegram_id == telegram_id,
                    RegisteredDomain.expires_at > datetime.utcnow()
                )\
                .scalar() or 0
            
            # Get recent transactions
            recent_transactions = self.session.query(WalletTransaction)\
                .filter(WalletTransaction.telegram_id == telegram_id)\
                .order_by(WalletTransaction.created_at.desc())\
                .limit(5)\
                .all()
            
            return {
                "user": user,
                "total_domains": total_domains,
                "active_domains": active_domains,
                "expiring_soon": active_domains - total_domains if active_domains > total_domains else 0,
                "wallet_balance": float(user.balance_usd) if user.balance_usd else 0.0,
                "recent_transactions": recent_transactions,
                "last_activity": user.updated_at or user.created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    async def update_user_language(self, telegram_id: int, language_code: str) -> bool:
        """Update user language preference"""
        try:
            user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.language_code = language_code
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            self.db.rollback()
            return False