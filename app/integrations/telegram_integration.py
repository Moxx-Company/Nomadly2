"""
Telegram API Integration for Nomadly3
Complete implementation for user interface and notification management
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from decimal import Decimal

from ..core.config import config
from ..core.external_services import TelegramServiceInterface
from ..repositories.external_integration_repo import (
    TelegramIntegrationRepository, APIUsageLogRepository
)

logger = logging.getLogger(__name__)

class TelegramAPI(TelegramServiceInterface):
    """Complete Telegram API integration for bot operations"""
    
    def __init__(self, bot_instance=None):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.bot = bot_instance  # Reference to actual telegram.Bot instance
        
        # Repository dependencies
        self.telegram_repo = TelegramIntegrationRepository()
        self.api_usage_repo = APIUsageLogRepository()
        
        # Notification templates
        self.notification_templates = {
            "domain_registration_success": "🏴‍☠️ *Domain Registration Successful!*\n\n"
                                          "Domain: `{domain_name}`\n"
                                          "Price: ${price_paid} USD\n"
                                          "Expires: {expiry_date}\n\n"
                                          "Your domain is now active and ready to use!",
            
            "payment_confirmed": "💰 *Payment Confirmed!*\n\n"
                               "Amount: ${amount} USD\n"
                               "Currency: {cryptocurrency}\n"
                               "Order: {order_id}\n\n"
                               "Your payment has been processed successfully.",
            
            "payment_overpaid": "🎁 *Payment Received - Bonus Credit!*\n\n"
                              "Paid: ${amount_paid} USD\n"
                              "Required: ${amount_required} USD\n"
                              "Bonus: ${bonus_amount} USD\n\n"
                              "The bonus has been added to your wallet balance!",
            
            "payment_underpaid": "⚠️ *Payment Received - Amount Short*\n\n"
                               "Received: ${amount_received} USD\n"
                               "Required: ${amount_required} USD\n"
                               "Shortage: ${shortage_amount} USD\n\n"
                               "Please send the remaining amount or contact support.",
            
            "domain_expiry_warning": "⏰ *Domain Expiry Warning*\n\n"
                                   "Domain: `{domain_name}`\n"
                                   "Expires in: {days_until_expiry} days\n"
                                   "Expiry Date: {expiry_date}\n\n"
                                   "Renew now to avoid service interruption.",
            
            "dns_record_created": "✅ *DNS Record Created*\n\n"
                                "Domain: `{domain_name}`\n"
                                "Type: {record_type}\n"
                                "Name: {record_name}\n"
                                "Content: {record_content}\n\n"
                                "DNS changes may take up to 24 hours to propagate.",
            
            "wallet_deposit": "💳 *Wallet Deposit Confirmed*\n\n"
                            "Amount: ${amount} USD\n"
                            "New Balance: ${new_balance} USD\n"
                            "Transaction: {transaction_hash}\n\n"
                            "Your wallet has been updated successfully."
        }
    
    async def send_message(self, chat_id: int, text: str, 
                          reply_markup=None, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """Send message to Telegram user"""
        if not self.bot:
            return {
                "success": False,
                "error": "Bot instance not available"
            }
        
        start_time = datetime.now()
        
        try:
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Store message integration record
            integration = self.telegram_repo.create_message_record(
                user_id=chat_id,
                message_type="text",
                telegram_message_id=message.message_id,
                message_content=text,
                delivery_status="sent"
            )
            
            # Log API usage
            await self._log_api_usage(
                endpoint="sendMessage",
                method="POST",
                status=200,
                user_id=chat_id,
                response_time_ms=response_time
            )
            
            logger.info(f"Successfully sent message to user {chat_id}")
            
            return {
                "success": True,
                "message_id": message.message_id,
                "integration_id": integration.id,
                "telegram_data": {
                    "message_id": message.message_id,
                    "date": message.date,
                    "text": message.text
                }
            }
            
        except Exception as e:
            # Update integration record with failure
            try:
                integration = self.telegram_repo.create_message_record(
                    user_id=chat_id,
                    message_type="text",
                    message_content=text,
                    delivery_status="failed",
                    error_message=str(e)
                )
            except:
                pass
            
            logger.error(f"Exception sending message to user {chat_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to send message: {str(e)}"
            }
    
    async def send_notification(self, user_id: int, notification_type: str, 
                               data: Dict[str, Any]) -> Dict[str, Any]:
        """Send structured notification to user"""
        if notification_type not in self.notification_templates:
            return {
                "success": False,
                "error": f"Unknown notification type: {notification_type}"
            }
        
        # Format notification message
        template = self.notification_templates[notification_type]
        try:
            formatted_message = template.format(**data)
        except KeyError as e:
            logger.error(f"Missing template data for {notification_type}: {str(e)}")
            return {
                "success": False,
                "error": f"Missing template data: {str(e)}"
            }
        
        # Send the formatted message
        result = await self.send_message(user_id, formatted_message)
        
        if result["success"]:
            # Update integration record with notification details
            try:
                self.telegram_repo.update_message_record(
                    result["integration_id"],
                    notification_type=notification_type,
                    notification_data=data
                )
            except Exception as e:
                logger.error(f"Failed to update notification record: {str(e)}")
        
        return result
    
    async def edit_message(self, chat_id: int, message_id: int, text: str, 
                          reply_markup=None) -> Dict[str, Any]:
        """Edit existing message"""
        if not self.bot:
            return {
                "success": False,
                "error": "Bot instance not available"
            }
        
        try:
            message = await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
            logger.info(f"Successfully edited message {message_id} for user {chat_id}")
            
            return {
                "success": True,
                "message_id": message.message_id,
                "telegram_data": {
                    "message_id": message.message_id,
                    "text": message.text,
                    "edit_date": message.edit_date
                }
            }
            
        except Exception as e:
            logger.error(f"Exception editing message {message_id} for user {chat_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to edit message: {str(e)}"
            }
    
    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Delete message"""
        if not self.bot:
            return False
        
        try:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            
            # Update integration record
            integration = self.telegram_repo.get_by_message_id(message_id)
            if integration:
                self.telegram_repo.update_delivery_status(
                    integration.id,
                    delivery_status="deleted"
                )
            
            logger.info(f"Successfully deleted message {message_id} for user {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Exception deleting message {message_id} for user {chat_id}: {str(e)}")
            return False
    
    async def send_domain_registration_notification(self, user_id: int, domain_name: str, 
                                                   registration_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send domain registration success notification"""
        notification_data = {
            "domain_name": domain_name,
            "price_paid": registration_details.get("price_paid", "N/A"),
            "expiry_date": registration_details.get("expiry_date", "N/A")
        }
        
        return await self.send_notification(
            user_id, 
            "domain_registration_success", 
            notification_data
        )
    
    async def send_payment_confirmation_notification(self, user_id: int, 
                                                    payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send payment confirmation notification"""
        notification_data = {
            "amount": payment_details.get("amount", "N/A"),
            "cryptocurrency": payment_details.get("cryptocurrency", "N/A"),
            "order_id": payment_details.get("order_id", "N/A")
        }
        
        return await self.send_notification(
            user_id,
            "payment_confirmed",
            notification_data
        )
    
    async def send_overpayment_notification(self, user_id: int, 
                                          payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send overpayment bonus notification"""
        notification_data = {
            "amount_paid": payment_details.get("amount_paid", "N/A"),
            "amount_required": payment_details.get("amount_required", "N/A"),
            "bonus_amount": payment_details.get("bonus_amount", "N/A")
        }
        
        return await self.send_notification(
            user_id,
            "payment_overpaid",
            notification_data
        )
    
    async def send_underpayment_notification(self, user_id: int, 
                                           payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send underpayment shortage notification"""
        notification_data = {
            "amount_received": payment_details.get("amount_received", "N/A"),
            "amount_required": payment_details.get("amount_required", "N/A"),
            "shortage_amount": payment_details.get("shortage_amount", "N/A")
        }
        
        return await self.send_notification(
            user_id,
            "payment_underpaid",
            notification_data
        )
    
    async def send_domain_expiry_warning(self, user_id: int, domain_name: str, 
                                        days_until_expiry: int, expiry_date: str) -> Dict[str, Any]:
        """Send domain expiry warning notification"""
        notification_data = {
            "domain_name": domain_name,
            "days_until_expiry": days_until_expiry,
            "expiry_date": expiry_date
        }
        
        return await self.send_notification(
            user_id,
            "domain_expiry_warning",
            notification_data
        )
    
    async def send_dns_record_notification(self, user_id: int, domain_name: str, 
                                         record_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send DNS record creation notification"""
        notification_data = {
            "domain_name": domain_name,
            "record_type": record_details.get("record_type", "N/A"),
            "record_name": record_details.get("record_name", "N/A"),
            "record_content": record_details.get("record_content", "N/A")
        }
        
        return await self.send_notification(
            user_id,
            "dns_record_created",
            notification_data
        )
    
    async def send_wallet_deposit_notification(self, user_id: int, 
                                             deposit_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send wallet deposit confirmation notification"""
        notification_data = {
            "amount": deposit_details.get("amount", "N/A"),
            "new_balance": deposit_details.get("new_balance", "N/A"),
            "transaction_hash": deposit_details.get("transaction_hash", "N/A")[:20] + "..."
        }
        
        return await self.send_notification(
            user_id,
            "wallet_deposit",
            notification_data
        )
    
    async def get_user_notification_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notification history for user"""
        try:
            notifications = self.telegram_repo.get_user_notifications(user_id, limit)
            return [
                {
                    "id": notif.id,
                    "message_type": notif.message_type,
                    "notification_type": notif.notification_type,
                    "delivery_status": notif.delivery_status,
                    "created_at": notif.created_at,
                    "telegram_message_id": notif.telegram_message_id
                }
                for notif in notifications
            ]
        except Exception as e:
            logger.error(f"Exception getting notification history for user {user_id}: {str(e)}")
            return []
    
    async def get_delivery_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get message delivery statistics"""
        try:
            stats = self.telegram_repo.get_delivery_stats(days)
            return {
                "success": True,
                "period_days": days,
                "stats": stats
            }
        except Exception as e:
            logger.error(f"Exception getting delivery stats: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get delivery stats: {str(e)}"
            }
    
    async def retry_failed_notifications(self, max_retries: int = 3) -> Dict[str, Any]:
        """Retry failed notification deliveries"""
        try:
            failed_notifications = self.telegram_repo.get_failed_notifications(max_retries)
            retry_results = []
            
            for notification in failed_notifications:
                # Attempt to resend
                result = await self.send_message(
                    notification.user_id,
                    notification.message_content
                )
                
                if result["success"]:
                    # Update status to sent
                    self.telegram_repo.update_delivery_status(
                        notification.id,
                        delivery_status="sent"
                    )
                    retry_results.append({
                        "notification_id": notification.id,
                        "status": "success"
                    })
                else:
                    # Increment retry count
                    self.telegram_repo.increment_retry_count(notification.id)
                    retry_results.append({
                        "notification_id": notification.id,
                        "status": "failed",
                        "error": result.get("error", "Unknown error")
                    })
            
            successful_retries = len([r for r in retry_results if r["status"] == "success"])
            
            logger.info(f"Retried {len(retry_results)} failed notifications, {successful_retries} successful")
            
            return {
                "success": True,
                "total_retried": len(retry_results),
                "successful_retries": successful_retries,
                "retry_results": retry_results
            }
            
        except Exception as e:
            logger.error(f"Exception retrying failed notifications: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retry notifications: {str(e)}"
            }
    
    async def _log_api_usage(self, endpoint: str, method: str, status: int,
                            user_id: int = None, response_time_ms: int = None):
        """Log API usage for monitoring"""
        try:
            self.api_usage_repo.log_api_call(
                service_name="telegram",
                api_endpoint=endpoint,
                http_method=method,
                response_status=status,
                user_id=user_id,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.error(f"Failed to log API usage: {str(e)}")
    
    def set_bot_instance(self, bot_instance):
        """Set the telegram.Bot instance for API operations"""
        self.bot = bot_instance
        logger.info("Telegram bot instance updated")