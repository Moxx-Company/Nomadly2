"""
User Controller - Handles user management operations
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from .base_controller import BaseController
from app.schemas.user_schemas import (
    UserRegistrationRequest,
    UserUpdateRequest,
    LanguageUpdateRequest
)
import logging

logger = logging.getLogger(__name__)

class UserController(BaseController):
    """Controller for user management operations"""
    
    def __init__(self, user_service, wallet_service):
        super().__init__()
        self.user_service = user_service
        self.wallet_service = wallet_service
    
    async def register_user(self, request: UserRegistrationRequest) -> Dict[str, Any]:
        """
        Controller: Register new user
        - Validates registration data
        - Creates user account
        - Initializes wallet
        - Returns user DTO
        """
        try:
            # Validate input
            user_data = self.validate_input(request)
            
            self.logger.info(f"Registering new user: {user_data['telegram_id']}")
            
            # Check if user already exists
            existing_user = await self.user_service.get_user_by_telegram_id(
                user_data['telegram_id']
            )
            if existing_user:
                raise HTTPException(status_code=400, detail="User already exists")
            
            # Call user service
            new_user = await self.user_service.create_user(
                telegram_id=user_data['telegram_id'],
                username=user_data.get('username'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                language_code=user_data.get('language_code', 'en'),
                initial_balance=user_data.get('initial_balance', 0.0)
            )
            
            # Map to DTO
            user_dto = {
                "telegram_id": new_user.telegram_id,
                "username": new_user.username,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "language_code": new_user.language_code,
                "balance_usd": float(new_user.balance_usd),
                "loyalty_tier": new_user.loyalty_tier,
                "is_premium": new_user.is_premium,
                "created_at": new_user.created_at.isoformat(),
                "last_activity": new_user.last_activity.isoformat() if new_user.last_activity else None
            }
            
            return self.success_response(
                data=user_dto,
                message=f"User registered successfully: {new_user.username or new_user.first_name}"
            )
            
        except Exception as e:
            self.handle_service_error(e, "register user")
    
    async def get_user_profile(self, telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Get user profile
        - Retrieves user data
        - Includes wallet balance and statistics
        - Returns comprehensive profile DTO
        """
        try:
            # Validate input (telegram_id as pseudo-request)
            if not telegram_id or telegram_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid telegram_id")
            
            self.logger.info(f"Fetching profile for user {telegram_id}")
            
            # Call user service
            user_profile = await self.user_service.get_complete_user_profile(telegram_id)
            
            if not user_profile:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Map to comprehensive DTO
            profile_dto = {
                "user_info": {
                    "telegram_id": user_profile.telegram_id,
                    "username": user_profile.username,
                    "first_name": user_profile.first_name,
                    "last_name": user_profile.last_name,
                    "language_code": user_profile.language_code,
                    "created_at": user_profile.created_at.isoformat(),
                    "last_activity": user_profile.last_activity.isoformat() if user_profile.last_activity else None
                },
                "wallet_info": {
                    "balance_usd": float(user_profile.balance_usd),
                    "total_spent": float(getattr(user_profile, 'total_spent', 0)),
                    "loyalty_tier": user_profile.loyalty_tier,
                    "is_premium": user_profile.is_premium
                },
                "account_stats": {
                    "domains_owned": getattr(user_profile, 'domains_count', 0),
                    "active_domains": getattr(user_profile, 'active_domains_count', 0),
                    "total_transactions": getattr(user_profile, 'transactions_count', 0),
                    "account_age_days": (user_profile.created_at - user_profile.created_at).days if user_profile.created_at else 0
                },
                "preferences": {
                    "language": user_profile.language_code,
                    "notifications_enabled": getattr(user_profile, 'notifications_enabled', True),
                    "email_notifications": getattr(user_profile, 'email_notifications', False)
                }
            }
            
            return self.success_response(
                data=profile_dto,
                message="User profile retrieved"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get user profile")
    
    async def update_user_profile(self, request: UserUpdateRequest, 
                                telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Update user profile
        - Validates update data
        - Updates user information
        - Returns updated profile DTO
        """
        try:
            # Validate input
            update_data = self.validate_input(request)
            
            self.logger.info(f"Updating profile for user {telegram_id}")
            
            # Call user service
            updated_user = await self.user_service.update_user_profile(
                telegram_id=telegram_id,
                **update_data
            )
            
            if not updated_user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Map to DTO
            user_dto = {
                "telegram_id": updated_user.telegram_id,
                "username": updated_user.username,
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "language_code": updated_user.language_code,
                "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
            }
            
            return self.success_response(
                data=user_dto,
                message="User profile updated successfully"
            )
            
        except Exception as e:
            self.handle_service_error(e, "update user profile")
    
    async def update_user_language(self, request: LanguageUpdateRequest, 
                                 telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Update user language preference
        - Validates language code
        - Updates user language
        - Returns updated language DTO
        """
        try:
            # Validate input
            language_data = self.validate_input(request)
            
            self.logger.info(f"Updating language for user {telegram_id}")
            
            # Validate language code
            supported_languages = ['en', 'fr', 'hi', 'zh', 'es']
            if language_data['language_code'] not in supported_languages:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported language. Supported: {supported_languages}"
                )
            
            # Call user service
            updated_user = await self.user_service.update_language_preference(
                telegram_id=telegram_id,
                language_code=language_data['language_code']
            )
            
            if not updated_user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Map to DTO
            language_dto = {
                "telegram_id": telegram_id,
                "language_code": updated_user.language_code,
                "language_name": self._get_language_name(updated_user.language_code),
                "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
            }
            
            return self.success_response(
                data=language_dto,
                message=f"Language updated to {language_dto['language_name']}"
            )
            
        except Exception as e:
            self.handle_service_error(e, "update user language")
    
    async def get_user_dashboard_data(self, telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Get user dashboard data
        - Retrieves comprehensive dashboard information
        - Includes domains, wallet, recent activity
        - Returns dashboard DTO
        """
        try:
            # Validate input parameters
            if not telegram_id or telegram_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid telegram_id")
            
            self.logger.info(f"Fetching dashboard data for user {telegram_id}")
            
            # Call user service
            dashboard_data = await self.user_service.get_dashboard_data(telegram_id)
            
            if not dashboard_data:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Map to comprehensive dashboard DTO
            dashboard_dto = {
                "user_summary": {
                    "telegram_id": telegram_id,
                    "display_name": dashboard_data.display_name,
                    "language": dashboard_data.language_code,
                    "member_since": dashboard_data.created_at.isoformat(),
                    "loyalty_tier": dashboard_data.loyalty_tier
                },
                "wallet_overview": {
                    "current_balance": float(dashboard_data.balance_usd),
                    "total_spent": float(dashboard_data.total_spent),
                    "pending_payments": dashboard_data.pending_payments_count,
                    "last_transaction": dashboard_data.last_transaction_date.isoformat() if dashboard_data.last_transaction_date else None
                },
                "domain_portfolio": {
                    "total_domains": dashboard_data.total_domains,
                    "active_domains": dashboard_data.active_domains,
                    "expiring_soon": dashboard_data.expiring_domains_count,
                    "next_expiry": dashboard_data.next_expiry_date.isoformat() if dashboard_data.next_expiry_date else None
                },
                "recent_activity": [
                    {
                        "action": activity.action,
                        "description": activity.description,
                        "timestamp": activity.timestamp.isoformat(),
                        "resource_type": activity.resource_type
                    }
                    for activity in dashboard_data.recent_activities
                ],
                "quick_stats": {
                    "dns_records": dashboard_data.total_dns_records,
                    "successful_payments": dashboard_data.successful_payments,
                    "account_age_days": dashboard_data.account_age_days
                }
            }
            
            return self.success_response(
                data=dashboard_dto,
                message="Dashboard data retrieved"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get dashboard data")
    
    async def delete_user_account(self, telegram_id: int, confirmation: bool = False) -> Dict[str, Any]:
        """
        Controller: Delete user account
        - Validates deletion request
        - Handles data cleanup
        - Returns deletion confirmation
        """
        try:
            if not confirmation:
                raise HTTPException(
                    status_code=400, 
                    detail="Account deletion requires explicit confirmation"
                )
            
            self.logger.info(f"Deleting user account: {telegram_id}")
            
            # Call user service
            deletion_result = await self.user_service.delete_user_account(
                telegram_id=telegram_id,
                confirmed=True
            )
            
            if not deletion_result:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Map to DTO
            deletion_dto = {
                "telegram_id": telegram_id,
                "deleted": True,
                "domains_transferred": deletion_result.domains_count,
                "data_cleanup_completed": deletion_result.cleanup_completed,
                "deleted_at": deletion_result.deleted_at.isoformat()
            }
            
            return self.success_response(
                data=deletion_dto,
                message="User account deleted successfully"
            )
            
        except Exception as e:
            self.handle_service_error(e, "delete user account")
    
    def _get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        language_names = {
            'en': 'English',
            'fr': 'Français',
            'hi': 'हिंदी',
            'zh': '中文',
            'es': 'Español'
        }
        return language_names.get(language_code, language_code)