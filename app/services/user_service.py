"""
User Service for Nomadly3 API
Business logic for user management, authentication, and profile operations
"""

import logging
from typing import Dict, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta

from ..repositories.user_repo import UserRepository  
from ..repositories.transaction_repo import TransactionRepository

logger = logging.getLogger(__name__)

class UserService:
    """Business logic service for user operations"""
    
    def __init__(self, db_session, user_repo=None, transaction_repo=None):
        """Initialize with dependency injection flexibility"""
        if user_repo:
            self.user_repo = user_repo
        else:
            from ..repositories.user_repo import UserRepository
            self.user_repo = UserRepository(db_session)
            
        if transaction_repo:
            self.transaction_repo = transaction_repo
        else:
            from ..repositories.transaction_repo import TransactionRepository
            self.transaction_repo = TransactionRepository(db_session)
    
    def create_user(self, telegram_id: int, username: Optional[str] = None, 
                   first_name: Optional[str] = None, last_name: Optional[str] = None,
                   language_code: str = "en", initial_balance: Optional[Decimal] = None) -> Dict[str, Any]:
        """Create a new user - Clean Architecture method"""
        try:
            # Check if user already exists
            existing_user = self.user_repo.get_by_telegram_id(telegram_id)
            if existing_user:
                return {
                    "success": False,
                    "error": "User already exists",
                    "user": existing_user
                }
            
            # Create new user with business logic
            user_data = {
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "language_code": language_code,
                "balance_usd": initial_balance or Decimal("0.00"),
                "is_admin": False
            }
            
            user = self.user_repo.create(user_data)
            
            # Setup initial wallet if balance provided
            if initial_balance and initial_balance > 0:
                self.setup_initial_wallet(telegram_id, initial_balance)
            
            # Assign default loyalty tier
            self.assign_loyalty_tier(telegram_id)
            
            logger.info(f"👤 New user created: {telegram_id}")
            
            return {
                "success": True,
                "message": "User created successfully",
                "user": user
            }
            
        except Exception as e:
            logger.error(f"❌ User creation error: {e}")
            return {
                "success": False,
                "error": f"User creation failed: {str(e)}"
            }

    def register_user(self, telegram_id: int, username: Optional[str] = None, 
                     first_name: Optional[str] = None, last_name: Optional[str] = None,
                     language_code: str = "en") -> Dict[str, Any]:
        """Register a new user - Legacy wrapper"""
        return self.create_user(telegram_id, username, first_name, last_name, language_code)

    def setup_initial_wallet(self, telegram_id: int, amount: Decimal) -> Dict[str, Any]:
        """Setup initial wallet with starting balance"""
        try:
            transaction_data = {
                "telegram_id": telegram_id,
                "transaction_type": "deposit",
                "amount": amount,
                "status": "completed",
                "payment_method": "initial_balance",
                "metadata": {"type": "welcome_bonus"}
            }
            
            self.transaction_repo.create(transaction_data)
            
            return {
                "success": True,
                "message": f"Initial wallet setup with ${amount}"
            }
            
        except Exception as e:
            logger.error(f"❌ Wallet setup error: {e}")
            return {
                "success": False,
                "error": f"Wallet setup failed: {str(e)}"
            }

    def assign_loyalty_tier(self, telegram_id: int) -> Dict[str, Any]:
        """Assign default loyalty tier to new user"""
        try:
            # Business logic for tier assignment
            update_data = {
                "loyalty_tier": "bronze",  # Default tier for new users
                "tier_benefits": ["basic_support", "standard_pricing"]
            }
            
            self.user_repo.update(telegram_id, update_data)
            
            return {
                "success": True,
                "message": "Loyalty tier assigned successfully",
                "tier": "bronze"
            }
            
        except Exception as e:
            logger.error(f"❌ Tier assignment error: {e}")
            return {
                "success": False,
                "error": f"Tier assignment failed: {str(e)}"
            }
    
    def get_complete_dashboard_summary(self, telegram_id: int) -> Dict[str, Any]:
        """
        Get complete user dashboard data combining wallet + loyalty + domain stats
        Essential for Main Menu Hub UI (Stage 2)
        """
        try:
            # Get user basic info
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get comprehensive dashboard data
            dashboard_data = self.user_repo.get_dashboard_data(telegram_id)
            
            # Calculate wallet balance from transactions
            transactions = self.transaction_repo.get_by_telegram_id(telegram_id)
            current_balance = self._calculate_current_balance(transactions)
            
            # Determine loyalty tier progress
            tier_info = self._calculate_loyalty_tier_progress(telegram_id, dashboard_data.get('total_spent', 0))
            
            # Generate dashboard summary
            summary = {
                "success": True,
                "user_info": {
                    "telegram_id": telegram_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "language_code": user.language_code,
                    "member_since": user.created_at.strftime("%B %Y") if user.created_at else "Unknown"
                },
                "wallet_summary": {
                    "current_balance_usd": float(current_balance),
                    "total_spent_usd": float(dashboard_data.get('total_spent', 0)),
                    "pending_transactions": dashboard_data.get('pending_transactions', 0),
                    "last_transaction": dashboard_data.get('last_transaction_date')
                },
                "domain_portfolio": {
                    "total_domains": dashboard_data.get('domain_count', 0),
                    "active_domains": dashboard_data.get('active_domains', 0),
                    "expiring_soon": dashboard_data.get('expiring_domains', 0),
                    "expired_domains": dashboard_data.get('expired_domains', 0)
                },
                "loyalty_program": {
                    "current_tier": tier_info['current_tier'],
                    "next_tier": tier_info['next_tier'],
                    "progress_percent": tier_info['progress_percent'],
                    "benefits": tier_info['benefits'],
                    "spending_to_next_tier": tier_info['spending_needed']
                },
                "recent_activity": {
                    "recent_domains": dashboard_data.get('recent_domains', []),
                    "recent_transactions": dashboard_data.get('recent_transactions', []),
                    "support_tickets": dashboard_data.get('open_tickets', 0)
                }
            }
            
            logger.info(f"📊 Dashboard summary generated for user {telegram_id}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Dashboard summary error: {e}")
            return {
                "success": False,
                "error": f"Dashboard summary failed: {str(e)}"
            }
    
    def update_language_preference(self, telegram_id: int, language_code: str) -> Dict[str, Any]:
        """
        Update user language preference
        Essential for Language Selection UI (Stage 1)
        """
        try:
            # Validate language code
            supported_languages = ['en', 'fr', 'hi', 'zh', 'es']
            if language_code not in supported_languages:
                return {
                    "success": False,
                    "error": f"Unsupported language. Supported: {', '.join(supported_languages)}"
                }
            
            # Update user language
            update_data = {"language_code": language_code}
            self.user_repo.update(telegram_id, update_data)
            
            # Generate localized welcome message
            welcome_messages = {
                'en': "🏴‍☠️ Welcome to Nameword Offshore Hosting!\nResilience | Discretion | Independence",
                'fr': "🏴‍☠️ Bienvenue chez Nameword Offshore Hosting!\nRésilience | Discrétion | Indépendance",
                'hi': "🏴‍☠️ नेमवर्ड ऑफशोर होस्टिंग में आपका स्वागत है!\nलचीलापन | विवेक | स्वतंत्रता",
                'zh': "🏴‍☠️ 欢迎来到Nameword离岸托管!\n韧性 | 谨慎 | 独立",
                'es': "🏴‍☠️ ¡Bienvenido a Nameword Offshore Hosting!\nResistencia | Discreción | Independencia"
            }
            
            return {
                "success": True,
                "language": language_code,
                "welcome_message": welcome_messages.get(language_code, welcome_messages['en'])
            }
            
        except Exception as e:
            logger.error(f"❌ Language update error: {e}")
            return {
                "success": False,
                "error": f"Language update failed: {str(e)}"
            }
    
    def update_contact_preferences(self, telegram_id: int, email: Optional[str] = None, 
                                  anonymous_mode: bool = False) -> Dict[str, Any]:
        """
        Update user contact preferences for domain registration
        Essential for Email Collection UI (Stage 4)
        """
        try:
            # Validate email if provided
            if email and not self._is_valid_email(email):
                return {
                    "success": False,
                    "error": "Invalid email format"
                }
            
            # Update user contact info
            update_data = {
                "email": email,
                "anonymous_registration": anonymous_mode
            }
            
            if anonymous_mode:
                update_data["email"] = None  # Clear email for anonymous mode
            
            self.user_repo.update(telegram_id, update_data)
            
            privacy_level = "anonymous" if anonymous_mode else "standard"
            
            return {
                "success": True,
                "privacy_level": privacy_level,
                "email_stored": email is not None and not anonymous_mode,
                "message": "Anonymous registration selected" if anonymous_mode else "Email contact stored securely"
            }
            
        except Exception as e:
            logger.error(f"❌ Contact preferences update error: {e}")
            return {
                "success": False,
                "error": f"Contact update failed: {str(e)}"
            }
    
    def _calculate_current_balance(self, transactions) -> Decimal:
        """Calculate current balance from transaction history"""
        balance = Decimal('0.00')
        
        for transaction in transactions:
            if transaction.transaction_type in ['deposit', 'credit', 'overpayment_credit']:
                balance += transaction.amount
            elif transaction.transaction_type in ['payment', 'debit', 'domain_purchase']:
                balance -= transaction.amount
                
        return balance
    
    def _calculate_loyalty_tier_progress(self, telegram_id: int, total_spent: float) -> Dict[str, Any]:
        """Calculate loyalty tier and progress"""
        tier_thresholds = {
            'bronze': {'min': 0, 'max': 100, 'benefits': ['Basic Support', 'Standard Pricing']},
            'silver': {'min': 100, 'max': 500, 'benefits': ['Priority Support', '5% Discount', 'Free DNS Management']},
            'gold': {'min': 500, 'max': 1500, 'benefits': ['Premium Support', '10% Discount', 'Free SSL Certificates']},
            'platinum': {'min': 1500, 'max': float('inf'), 'benefits': ['VIP Support', '15% Discount', 'Free Everything']}
        }
        
        current_tier = 'bronze'
        for tier, info in tier_thresholds.items():
            if info['min'] <= total_spent < info['max']:
                current_tier = tier
                break
        
        # Calculate progress to next tier
        current_info = tier_thresholds[current_tier]
        if current_info['max'] == float('inf'):
            progress_percent = 100
            next_tier = None
            spending_needed = 0
        else:
            progress_percent = min(100, ((total_spent - current_info['min']) / (current_info['max'] - current_info['min'])) * 100)
            next_tier = list(tier_thresholds.keys())[list(tier_thresholds.keys()).index(current_tier) + 1] if current_tier != 'platinum' else None
            spending_needed = max(0, current_info['max'] - total_spent)
        
        return {
            'current_tier': current_tier,
            'next_tier': next_tier,
            'progress_percent': round(progress_percent, 1),
            'benefits': current_info['benefits'],
            'spending_needed': spending_needed
        }
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_user_profile(self, telegram_id: int) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            return {
                "success": True,
                "user": user
            }
            
        except Exception as e:
            logger.error(f"❌ Get user profile error: {e}")
            return {
                "success": False,
                "error": f"Failed to get profile: {str(e)}"
            }
    
    def update_user_profile(self, telegram_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile information"""
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            updated_user = self.user_repo.update(user.id, update_data)
            
            return {
                "success": True,
                "message": "Profile updated successfully",
                "user": updated_user
            }
            
        except Exception as e:
            logger.error(f"❌ Update profile error: {e}")
            return {
                "success": False,
                "error": f"Failed to update profile: {str(e)}"
            }
    
    def manage_balance(self, telegram_id: int, operation: str, amount: Decimal, 
                      description: str = "") -> Dict[str, Any]:
        """Manage user balance (add, deduct, set)"""
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            old_balance = user.balance_usd
            
            if operation == "add":
                new_balance = old_balance + amount
            elif operation == "deduct":
                new_balance = old_balance - amount
                if new_balance < 0:
                    return {
                        "success": False,
                        "error": "Insufficient balance"
                    }
            elif operation == "set":
                new_balance = amount
            else:
                return {
                    "success": False,
                    "error": "Invalid operation"
                }
            
            # Update balance
            updated_user = self.user_repo.update(user.id, {"balance_usd": new_balance})
            
            # Log transaction
            transaction_data = {
                "telegram_id": telegram_id,
                "transaction_type": operation,
                "amount": amount,
                "description": description or f"Balance {operation}",
                "old_balance": old_balance,
                "new_balance": new_balance
            }
            
            self.transaction_repo.create(transaction_data)
            
            logger.info(f"💰 Balance {operation} for user {telegram_id}: {old_balance} → {new_balance}")
            
            return {
                "success": True,
                "message": f"Balance {operation} successful",
                "old_balance": old_balance,
                "new_balance": new_balance,
                "user": updated_user
            }
            
        except Exception as e:
            logger.error(f"❌ Balance management error: {e}")
            return {
                "success": False,
                "error": f"Balance operation failed: {str(e)}"
            }
    
    def get_user_statistics(self, telegram_id: int) -> Dict[str, Any]:
        """Get user statistics including domains, transactions, etc."""
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get transaction history
            transactions = self.transaction_repo.get_by_telegram_id(telegram_id, limit=10)
            
            # Get domain count (would need domain repo for this)
            # For now, return basic stats
            
            stats = {
                "user_id": user.id,
                "telegram_id": telegram_id,
                "current_balance": user.balance_usd,
                "registration_date": user.created_at,
                "last_activity": user.updated_at,
                "recent_transactions": transactions,
                "transaction_count": len(transactions),
                "is_admin": user.is_admin
            }
            
            return {
                "success": True,
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"❌ Get user statistics error: {e}")
            return {
                "success": False,
                "error": f"Failed to get statistics: {str(e)}"
            }
    
    def authenticate_user(self, telegram_id: int) -> Dict[str, Any]:
        """Authenticate user for API access"""
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Update last login
            self.user_repo.update(user.id, {"updated_at": datetime.utcnow()})
            
            return {
                "success": True,
                "message": "Authentication successful",
                "user": user
            }
            
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return {
                "success": False,
                "error": f"Authentication failed: {str(e)}"
            }
    
    async def get_dashboard_data(self, telegram_id: int) -> dict:
        """Get comprehensive dashboard data for user"""
        try:
            # Get user info
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                raise Exception("User not found")
            
            # Get dashboard data from repository
            dashboard_data = self.user_repo.get_dashboard_data(telegram_id)
            
            return {
                "user_info": {
                    "telegram_id": telegram_id,
                    "username": user.username,
                    "language": user.language_code,
                    "balance_usd": float(user.balance_usd),
                    "total_spent": float(user.total_spent),
                    "created_at": user.created_at.isoformat() if user.created_at else None
                },
                "statistics": {
                    "total_domains": dashboard_data.get("domain_count", 0),
                    "active_domains": dashboard_data.get("active_domains", 0),
                    "expired_domains": dashboard_data.get("expired_domains", 0),
                    "expiring_domains": dashboard_data.get("expiring_domains", 0),
                    "total_spent": dashboard_data.get("total_spent", 0),
                    "pending_transactions": dashboard_data.get("pending_transactions", 0)
                },
                "recent_activity": dashboard_data.get("recent_domains", []),
                "recent_transactions": dashboard_data.get("recent_transactions", [])
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise Exception(f"Could not get dashboard data: {str(e)}")

    async def update_language_preference(self, telegram_id: int, language_code: str) -> dict:
        """Update user language preference"""
        try:
            result = await self.user_repo.update_user_language(telegram_id, language_code)
            if result:
                return {
                    "success": True,
                    "language_code": language_code,
                    "message": f"Language updated to {language_code}"
                }
            else:
                raise Exception("Failed to update language")
        except Exception as e:
            logger.error(f"Error updating language: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_wallet_balance(self, telegram_id: int) -> dict:
        """Get user wallet balance and transaction summary"""
        try:
            user = await self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                raise Exception("User not found")
                
            balance = user.balance_usd
            # Get recent transactions from transaction repo if available
            recent_transactions = []
            try:
                recent_transactions = await self.transaction_repo.get_recent_transactions(telegram_id, 10)
            except:
                recent_transactions = []
            
            return {
                "balance_usd": float(balance),
                "recent_transactions": [
                    {
                        "id": tx.id,
                        "type": tx.transaction_type,
                        "amount": float(tx.amount_usd),
                        "status": tx.status,
                        "created_at": tx.created_at.isoformat()
                    }
                    for tx in recent_transactions
                ]
            }
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            raise Exception(f"Could not get wallet balance: {str(e)}")