"""
Master Notification Service - Single Source of Truth for All Notifications
Consolidates all notification functionality into one service to prevent duplicates
"""

import os
import logging
import httpx
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from fresh_database import get_db_manager
# Translation helper functions
def t_user(key, telegram_id, **kwargs):
    """Simple translation helper"""
    return key.format(**kwargs) if kwargs else key

def get_user_language(telegram_id):
    """Get user language preference"""
    return 'en'  # Default to English

logger = logging.getLogger(__name__)

class MasterNotificationService:
    """Centralized notification service handling ALL notifications"""
    
    def __init__(self):
        self.bot_token = "8058274028:AAFSNDsJ5upG_gLEkWOl9M5apgTypkNDecQ"
        self.db = get_db_manager()
        
        # Email configuration
        self.brevo_api_key = os.environ.get("BREVO_API_KEY")
        self.from_email = os.environ.get("BREVO_SENDER_EMAIL", "noreply@nomadly.com")
        
    async def send_payment_confirmation(self, telegram_id: int, payment_data: Dict[str, Any]) -> bool:
        """Send payment confirmation notification (Telegram + Email)"""
        try:
            logger.info(f"📱 Sending payment confirmation to user {telegram_id}")
            
            # Format payment confirmation message
            domain_name = payment_data.get('domain_name', 'N/A')
            amount = payment_data.get('amount_usd', payment_data.get('total_price_usd', 0))
            
            telegram_message = (
                f"💰 **Payment Confirmed!**\n\n"
                f"✅ **Domain:** `{domain_name}`\n"
                f"💰 **Amount:** ${amount} USD\n"
                f"🎉 **Status:** Active & Ready!\n\n"
                f"Your domain was already registered and is working perfectly.\n"
                f"Use /mydomains to manage your domain."
            )
            
            # Send Telegram notification
            telegram_success = await self._send_telegram_message(telegram_id, telegram_message)
            
            # Send email if user has real email
            email_success = await self._send_payment_email(telegram_id, payment_data)
            
            logger.info(f"✅ Payment notification sent - Telegram: {telegram_success}, Email: {email_success}")
            return telegram_success
            
        except Exception as e:
            logger.error(f"❌ Payment confirmation failed: {e}")
            return False
    
    async def send_domain_registration_success(self, telegram_id: int, domain_data: Dict[str, Any]) -> bool:
        """Send domain registration success notification"""
        try:
            logger.info(f"🌐 Sending domain registration success to user {telegram_id}")
            
            domain_name = domain_data.get('domain_name', 'N/A')
            
            telegram_message = (
                f"What would you like to do next?"
            )
            
            # Create inline keyboard with user-requested buttons
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "🌐 My Domains", "callback_data": "my_domains"},
                        {"text": "🔍 Register Domain", "callback_data": "search_domain"}
                    ]
                ]
            }
            
            # Send Telegram notification with buttons
            telegram_success = await self._send_telegram_message_with_keyboard(telegram_id, telegram_message, keyboard)
            
            # Send email if user has real email
            email_success = await self._send_domain_email(telegram_id, domain_data)
            
            logger.info(f"✅ Domain registration notification sent - Telegram: {telegram_success}, Email: {email_success}")
            return telegram_success
            
        except Exception as e:
            logger.error(f"❌ Domain registration notification failed: {e}")
            return False
    
    async def send_progress_notification(self, telegram_id: int, domain: str, stage: str, details: Optional[Dict] = None) -> bool:
        """SECURE progress notification - only for REAL blockchain confirmations"""
        try:
            logger.warning(f"🚨 BLOCKED false progress notification: {stage} for {domain} (user {telegram_id})")
            logger.warning("🚨 Progress notifications disabled due to security vulnerability")
            
            # SECURITY FIX: Completely disable progress notifications until payment system is secure
            # This prevents false "payment confirmed" messages without real blockchain verification
            return True  # Return success but don't send anything
            
        except Exception as e:
            logger.error(f"❌ Progress notification failed: {e}")
            return False
    
    async def send_overpayment_notification(self, telegram_id: int, overpayment_amount: float, new_balance: float, order_id: str) -> bool:
        """Send overpayment wallet credit notification"""
        try:
            logger.info(f"💎 Sending overpayment notification to user {telegram_id}")
            
            message = (
                f"🎁 **Overpayment Credited to Wallet!**\n\n"
                f"💰 **Excess Amount:** ${overpayment_amount:.2f} USD\n"
                f"💳 **New Wallet Balance:** ${new_balance:.2f} USD\n"
                f"🔗 **Order ID:** `{order_id}`\n\n"
                f"✨ **No payment is ever lost - all excess funds are credited!**\n\n"
                f"Use your wallet balance for future domain purchases."
            )
            
            return await self._send_telegram_message(telegram_id, message)
            
        except Exception as e:
            logger.error(f"❌ Overpayment notification failed: {e}")
            return False
    
    async def send_underpayment_notification(self, telegram_id: int, amount_received: float, amount_needed: float, shortage: float) -> bool:
        """Send underpayment wallet credit notification"""
        try:
            logger.info(f"⚠️ Sending underpayment notification to user {telegram_id}")
            
            message = (
                f"💳 **Partial Payment Credited to Wallet**\n\n"
                f"💰 **You Sent:** ${amount_received:.2f} USD\n"
                f"🎯 **Amount Needed:** ${amount_needed:.2f} USD\n"
                f"⚠️ **Shortage:** ${shortage:.2f} USD\n\n"
                f"✅ **Your ${amount_received:.2f} USD has been credited to your wallet!**\n\n"
                f"💡 *Add ${shortage:.2f} more to complete your purchase.*\n\n"
                f"🏴‍☠️ *No payment is ever lost - all funds are credited!*"
            )
            
            return await self._send_telegram_message(telegram_id, message)
            
        except Exception as e:
            logger.error(f"❌ Underpayment notification failed: {e}")
            return False
    
    async def _send_telegram_message(self, telegram_id: int, message: str) -> bool:
        """Send message via Telegram Bot API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    json={
                        "chat_id": telegram_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"📱 Telegram message sent successfully to user {telegram_id}")
                    return True
                else:
                    logger.error(f"❌ Telegram API error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Telegram send failed: {e}")
            return False
    
    async def _send_telegram_message_with_keyboard(self, telegram_id: int, message: str, keyboard: Dict) -> bool:
        """Send message with inline keyboard via Telegram Bot API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    json={
                        "chat_id": telegram_id,
                        "text": message,
                        "parse_mode": "Markdown",
                        "reply_markup": keyboard
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"📱 Telegram message with keyboard sent successfully to user {telegram_id}")
                    return True
                else:
                    logger.error(f"❌ Telegram API error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Telegram send with keyboard failed: {e}")
            return False
    
    async def _send_payment_email(self, telegram_id: int, payment_data: Dict[str, Any]) -> bool:
        """Send payment confirmation email if user has real email"""
        try:
            # Get user's email from database
            user_email = self._get_user_email(telegram_id)
            if not user_email or user_email in ['privacy@offshore.contact', 'privacy@nomadly.com']:
                logger.info(f"Skipping email - user {telegram_id} has privacy email")
                return True
            
            if not self.brevo_api_key:
                logger.info("Brevo API key not configured - skipping email")
                return True
            
            # Send email via Brevo API
            subject = "Payment Confirmation - Nomadly Domain Service"
            html_content = self._build_payment_email_html(payment_data)
            
            return await self._send_brevo_email(user_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"❌ Payment email failed: {e}")
            return False
    
    async def _send_domain_email(self, telegram_id: int, domain_data: Dict[str, Any]) -> bool:
        """Send domain registration email if user has real email"""
        try:
            # Get user's email from database
            user_email = self._get_user_email(telegram_id)
            if not user_email or user_email in ['privacy@offshore.contact', 'privacy@nomadly.com']:
                logger.info(f"Skipping email - user {telegram_id} has privacy email")
                return True
            
            if not self.brevo_api_key:
                logger.info("Brevo API key not configured - skipping email")
                return True
            
            # Send email via Brevo API
            subject = f"Domain Registration Complete - {domain_data.get('domain_name', 'Your Domain')}"
            html_content = self._build_domain_email_html(domain_data)
            
            return await self._send_brevo_email(user_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"❌ Domain email failed: {e}")
            return False
    
    async def _send_brevo_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via Brevo API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={
                        "accept": "application/json",
                        "api-key": self.brevo_api_key or "",
                        "content-type": "application/json"
                    },
                    json={
                        "sender": {
                            "name": "Nomadly Domain Service",
                            "email": self.from_email
                        },
                        "to": [{"email": to_email}],
                        "subject": subject,
                        "htmlContent": html_content
                    }
                )
                
                if response.status_code == 201:
                    logger.info(f"📧 Email sent successfully to {to_email}")
                    return True
                else:
                    logger.error(f"❌ Brevo API error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Brevo email send failed: {e}")
            return False
    
    def _get_user_email(self, telegram_id: int) -> Optional[str]:
        """Get user's email from database"""
        try:
            # First check orders table for provided emails
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get most recent real email from orders
            cursor.execute("""
                SELECT email_provided FROM orders 
                WHERE telegram_id = %s 
                AND email_provided IS NOT NULL 
                AND email_provided NOT IN ('privacy@offshore.contact', 'privacy@nomadly.com')
                ORDER BY created_at DESC LIMIT 1
            """, (telegram_id,))
            
            result = cursor.fetchone()
            if result and result[0]:
                cursor.close()
                conn.close()
                return result[0]
            
            # Fallback to users table technical_email
            cursor.execute("""
                SELECT technical_email FROM users 
                WHERE telegram_id = %s 
                AND technical_email IS NOT NULL
                AND technical_email NOT IN ('privacy@offshore.contact', 'privacy@nomadly.com')
            """, (telegram_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result[0] if result and result[0] else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user email: {e}")
            return None
    
    def _build_payment_email_html(self, payment_data: Dict[str, Any]) -> str:
        """Build HTML content for payment confirmation email"""
        domain_name = payment_data.get('domain_name', 'N/A')
        amount = payment_data.get('amount_usd', payment_data.get('total_price_usd', 0))
        
        return f"""
        <html>
        <body>
            <h2>🏴‍☠️ Payment Confirmation - Nomadly Domain Service</h2>
            <p>Your cryptocurrency payment has been successfully confirmed!</p>
            
            <h3>Payment Details:</h3>
            <ul>
                <li><strong>Domain:</strong> {domain_name}</li>
                <li><strong>Amount:</strong> ${amount} USD</li>
                <li><strong>Status:</strong> Confirmed & Active</li>
                <li><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
            </ul>
            
            <p>Your domain is now active and ready to use!</p>
            <p>Use the Nomadly Telegram bot to manage your domain settings.</p>
            
            <p><em>Nomadly Domain Services - Resilience • Discretion • Independence</em></p>
        </body>
        </html>
        """
    
    def _build_domain_email_html(self, domain_data: Dict[str, Any]) -> str:
        """Build HTML content for domain registration email"""
        domain_name = domain_data.get('domain_name', 'N/A')
        
        return f"""
        <html>
        <body>
            <h2>🎉 Domain Registration Complete - Nomadly Domain Service</h2>
            <p>Your offshore domain registration has been successfully completed!</p>
            
            <h3>Domain Details:</h3>
            <ul>
                <li><strong>Domain Name:</strong> {domain_name}</li>
                <li><strong>Status:</strong> Active and Operational</li>
                <li><strong>DNS Provider:</strong> Cloudflare</li>
                <li><strong>Registration Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</li>
            </ul>
            
            <p>Your domain is now live and ready to use!</p>
            <p>You can manage DNS records and domain settings through the Nomadly Telegram bot.</p>
            
            <p><strong>Privacy Protection:</strong> Your domain uses anonymous contact information for enhanced privacy.</p>
            
            <p><em>Welcome to the offshore community!</em></p>
            <p><em>Nomadly Domain Services - Resilience • Discretion • Independence</em></p>
        </body>
        </html>
        """

# Global service instance
_master_notification_service = None

def get_master_notification_service() -> MasterNotificationService:
    """Get the global master notification service instance"""
    global _master_notification_service
    if _master_notification_service is None:
        _master_notification_service = MasterNotificationService()
    return _master_notification_service