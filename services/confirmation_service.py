"""
Unified Confirmation System for Nomadly2
Centralizes all confirmation notifications using Brevo API
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from utils.translation_helper import t_user, get_user_language
from database import get_db_manager

logger = logging.getLogger(__name__)


class ConfirmationService:
    """Centralized confirmation notification system"""

    def __init__(self):
        self.brevo_api_key = os.environ.get("BREVO_API_KEY")
        self.brevo_smtp_key = os.environ.get("BREVO_SMTP_KEY")
        self.from_email = os.environ.get("INFOBIP_FROM_EMAIL", "noreply@nomadly.com")
        self.db = get_db_manager()

        # Brevo API endpoints
        self.brevo_api_url = "https://api.brevo.com/v3"

    def is_configured(self) -> bool:
        """Check if confirmation service is properly configured"""
        return bool(self.brevo_api_key or self.brevo_smtp_key)

    async def master_send_overpayment_notification(
            self, telegram_id: int, overpayment_amount: float, new_balance: float,
    ) -> bool:
        try:
            user_language = get_user_language(telegram_id)

            # Get payment confirmation template
            subject = t_user("payment_confirmation_subject", telegram_id)

            # Send via both Telegram and Email
            success = True

            # Use Master Notification Service
            from services.master_notification_service import get_master_notification_service

            notification_service = get_master_notification_service()
            telegram_success = await notification_service.send_overpayment_notification(telegram_id, overpayment_amount, new_balance, '')

            return success

        except Exception as e:
            logger.error(f"Error sending payment confirmation: {e}")
            return False

    async def send_payment_confirmation(
        self, telegram_id: int, order_data: Dict[str, Any]
    ) -> bool:
        """
        Send payment confirmation notification

        Args:
            telegram_id: User's Telegram ID
            order_data: Payment/order information

        Returns:
            Success status
        """
        logger.info(f"✅ IN send_payment_confirmation 1")
        try:
            user_language = get_user_language(telegram_id)

            # Get payment confirmation template
            subject = t_user("payment_confirmation_subject", telegram_id)

            # Build email content
            email_content = self._build_payment_confirmation_content(
                telegram_id, order_data, user_language
            )

            # Send via both Telegram and Email
            success = True

            # Use Master Notification Service
            from services.master_notification_service import get_master_notification_service
            
            notification_service = get_master_notification_service()
            telegram_success = await notification_service.send_payment_confirmation(telegram_id, order_data)

            # Send email confirmation if configured
            if self.is_configured():
                email_success = await self._send_email_confirmation(
                    telegram_id, subject, email_content, order_data
                )
            logger.info(f"✅ IN send_payment_confirmation order_data: {order_data}, {email_success} 1")
            success = success and email_success

            # Log confirmation in database
            await self._log_confirmation(telegram_id, "payment", order_data, success)

            return success

        except Exception as e:
            logger.error(f"Error sending payment confirmation: {e}")
            return False

    async def send_domain_registration_confirmation(
        self, telegram_id: int, domain_data: Dict[str, Any]
    ) -> bool:
        """
        Send domain registration confirmation

        Args:
            telegram_id: User's Telegram ID
            domain_data: Domain registration information

        Returns:
            Success status
        """

        logger.info(f"✅ IN send_domain_registration_confirmation 1")
        try:
            user_language = get_user_language(telegram_id)

            # Get domain confirmation template
            subject = t_user("domain_registration_subject", telegram_id)

            # Build email content
            email_content = self._build_domain_confirmation_content(
                telegram_id, domain_data, user_language
            )

            # Send via both Telegram and Email
            success = True

            # Use Master Notification Service
            from services.master_notification_service import get_master_notification_service
            
            notification_service = get_master_notification_service()
            telegram_success = await notification_service.send_domain_registration_success(telegram_id, domain_data)

            # Send email confirmation if configured
            if self.is_configured():
                email_success = await self._send_email_confirmation(
                    telegram_id, subject, email_content, domain_data
                )
                logger.info(f"✅ IN send_domain_registration_confirmation domain_data: {domain_data}, {email_success} : 1")
                success = success and email_success

            # Log confirmation in database
            await self._log_confirmation(
                telegram_id, "domain_registration", domain_data, success
            )

            return success

        except Exception as e:
            logger.error(f"Error sending domain confirmation: {e}")
            return False

    async def send_domain_wallet_top_confirmation(self, telegram_id: int, paid_amount: float):

        from services.master_notification_service import get_master_notification_service

        logger.info(
            f"📞📞 2. Notification for User {telegram_id}"
            )
            
        notification_service = get_master_notification_service()
        telegram_success = await notification_service.send_wallet_topup_notification(telegram_id, paid_amount)

        return True


    def _build_payment_confirmation_content(
        self, telegram_id: int, order_data: Dict[str, Any], language: str
    ) -> str:
        """Build payment confirmation email content"""

        content = f"""
{t_user('payment_confirmation_title', telegram_id)}

{t_user('payment_details', telegram_id)}:
• {t_user('amount', telegram_id)}: ${order_data.get('amount_usd', 0):.2f} USD
• {t_user('payment_method', telegram_id)}: {order_data.get('payment_method', 'Cryptocurrency')}
• {t_user('transaction_id', telegram_id)}: {order_data.get('transaction_id', 'N/A')}
• {t_user('order_id', telegram_id)}: {order_data.get('order_id', 'N/A')}
• {t_user('date', telegram_id)}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

{t_user('service_details', telegram_id)}:
{order_data.get('service_description', t_user('service_processing', telegram_id))}

{t_user('offshore_community_welcome', telegram_id)}

{t_user('support_contact', telegram_id)}
"""
        return content

    def _build_domain_confirmation_content(
        self, telegram_id: int, domain_data: Dict[str, Any], language: str
    ) -> str:
        """Build domain registration confirmation email content"""

        # Handle nameservers properly - could be string, list, or JSON
        nameservers = domain_data.get("nameservers", [])

        # Handle nameservers - database stores them as double-encoded JSON
        if isinstance(nameservers, list):
            nameserver_list = (
                ", ".join(nameservers) if nameservers else "Not configured"
            )
        elif isinstance(nameservers, str):
            try:
                import json

                # First JSON decode
                first_decode = json.loads(nameservers)

                # If result is still a string, decode again (double-encoded)
                if isinstance(first_decode, str):
                    second_decode = json.loads(first_decode)
                    if isinstance(second_decode, list):
                        nameserver_list = ", ".join(second_decode)
                    else:
                        nameserver_list = str(second_decode)
                elif isinstance(first_decode, list):
                    nameserver_list = ", ".join(first_decode)
                else:
                    nameserver_list = str(first_decode)
            except:
                # If parsing fails, treat as single nameserver
                nameserver_list = (
                    nameservers if nameservers != "N/A" else "Not configured"
                )
        else:
            nameserver_list = "Not configured"

        # Get Nameword and Cloudflare IDs for technical details
        nameword_id = domain_data.get("openprovider_domain_id", "N/A")
        cloudflare_zone = domain_data.get("cloudflare_zone_id", "N/A")

        content = f"""
🏴‍☠️ {os.getenv('PROJECT_NAME')} DOMAIN REGISTRATION COMPLETE 🏴‍☠️

Your offshore domain registration has been successfully completed!

DOMAIN DETAILS:
• Domain Name: {domain_data.get('domain_name', 'N/A')}
• Registration Status: ACTIVE
• Registration Date: {domain_data.get('registration_date', 'Today')}
• Expiry Date: {domain_data.get('expiry_date', 'N/A')}
• OpenProvider Domain ID: {nameword_id}
• Nameservers: {nameserver_list}

DNS CONFIGURATION:
{domain_data.get('dns_info', 'DNS configured and active')}
• Cloudflare Zone ID: {cloudflare_zone}
• DNS Provider: Cloudflare DNS
• Status: Fully configured and operational

DOMAIN MANAGEMENT:
Your domain is now live and ready to use. You can manage DNS records, update nameservers, and configure hosting through your {os.getenv('PROJECT_NAME')} bot interface.

Use /my_domains command in the bot to access domain management features.

OFFSHORE PRIVACY:
Your domain registration uses anonymous contact information for enhanced privacy. All technical details are handled through our offshore infrastructure for maximum discretion.

SUPPORT:
For any questions or assistance with your domain, contact our offshore support team through the {os.getenv('PROJECT_NAME')} bot interface.

Welcome to the offshore community!

---
{os.getenv('PROJECT_NAME')} Offshore Domain Services
Resilience • Discretion • Independence
"""
        return content

    async def _send_telegram_notification(
        self, telegram_id: int, title: str, content: str
    ) -> bool:
        """Send notification via Telegram Bot API"""
        try:
            import os
            import aiohttp
            from dotenv import load_dotenv
            
            # Ensure environment variables are loaded
            load_dotenv()
            
            bot_token = "8058274028:AAFSNDsJ5upG_gLEkWOl9M5apgTypkNDecQ"
            if not bot_token:
                logger.warning("BOT_TOKEN not found, skipping Telegram notification")
                return False
            
            # Format message for Telegram with proper domain details
            if "Domain Registration" in title:
                # Extract domain data for proper formatting
                domain_name = content.split("Domain Name: ")[1].split("\n")[0] if "Domain Name: " in content else "Unknown"
                message = f"""🎉 <b>DOMAIN REGISTRATION SUCCESSFUL!</b>

✅ <b>Domain:</b> {domain_name}
🌐 <b>Status:</b> Active and ready to use
📡 <b>DNS:</b> Fully configured with Cloudflare

🚀 <b>Your domain is now live!</b>

Use /my_domains to manage your domain."""
            else:
                message = f"🎉 <b>{title}</b>\n\n{content}"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": telegram_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"✅ Telegram notification sent successfully to user {telegram_id}")
                        return True
                    else:
                        response_text = await response.text()
                        logger.error(f"❌ Failed to send Telegram notification: {response.status} - {response_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error sending Telegram notification: {e}")
            return False

    async def _send_email_confirmation(
        self, telegram_id: int, subject: str, content: str, data: Dict[str, Any]
    ) -> bool:
        """Send email confirmation via Brevo API"""
        if not self.is_configured():
            logger.warning("Brevo API not configured, skipping email confirmation")
            return False

        try:
            # Get email from data first (for domain registration), then fall back to user database
            recipient_email = None
            
            # For domain registration, email is in the data
            if 'contact_email' in data:
                recipient_email = data.get('contact_email')
            elif 'technical_email' in data:
                recipient_email = data.get('technical_email')
            
            # Fall back to database if not in data
            if not recipient_email or recipient_email == 'cloakhost@tutamail.com':
                user = self.db.get_user(telegram_id)
                if user and hasattr(user, 'technical_email'):
                    recipient_email = user.technical_email
            
            logger.info(f"recipient_email: {recipient_email}, subject.lower(): {subject.lower()}")

            # Skip if no valid email or using default privacy email
            if not recipient_email or recipient_email == 'cloakhost@tutamail.com':
                logger.info(f"No custom email found for user {telegram_id}, skipping email notification")
                return True  # Return True as this is not an error
            
            # Import and use our Brevo email service
            from services.brevo_email_service import get_email_service
            email_service = get_email_service()
            
            # Handle different notification types
            if "payment" in subject.lower():
                # Payment confirmation
                order_id = data.get('order_id', 'ORD-XXXXX')
                domain = data.get('domain_name', 'domain')
                amount = data.get('amount_usd', data.get('amount', 0))
                crypto_type = data.get('payment_method', 'cryptocurrency')
                crypto_amount = data.get('crypto_amount', 0)
                
                result = await email_service.send_payment_confirmation_email(
                    email=recipient_email,
                    domain=domain,
                    order_id=order_id,
                    amount=amount,
                    crypto_type=crypto_type,
                    crypto_amount=crypto_amount
                )
            elif "domain" in subject.lower() and "registration" in subject.lower():
                # Domain registration confirmation
                domain = data.get('domain_name', 'domain')
                order_id = data.get('order_id', 'ORD-XXXXX')
                nameservers = data.get('nameservers', ['ns1.cloudflare.com', 'ns2.cloudflare.com'])
                expiry_date = data.get('expiry_date', 'One year from today')
                
                # Parse nameservers if they're JSON encoded
                if isinstance(nameservers, str):
                    try:
                        import json
                        nameservers = json.loads(nameservers)
                        if isinstance(nameservers, str):  # Double encoded
                            nameservers = json.loads(nameservers)
                    except:
                        nameservers = [nameservers]
                
                result = await email_service.send_registration_complete_email(
                    email=recipient_email,
                    domain=domain,
                    order_id=order_id,
                    nameservers=nameservers if isinstance(nameservers, list) else [str(nameservers)],
                    expiry_date=expiry_date
                )
            else:
                # Generic email - use original Brevo API
                result = await email_service.send_email(
                    to_email=recipient_email,
                    subject=subject,
                    html_content=f"<pre>{content}</pre>",
                    text_content=content
                )
            
            if result.get('success'):
                logger.info(f"✅ Email confirmation sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"❌ Failed to send email: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            logger.error(f"Error sending email confirmation: {e}")
            return False

    async def _log_confirmation(
        self,
        telegram_id: int,
        confirmation_type: str,
        data: Dict[str, Any],
        success: bool,
    ) -> None:
        """Log confirmation attempt in database"""
        try:
            # This would typically insert into an email_notifications or confirmations table
            logger.info(
                f"Confirmation logged: user={telegram_id}, type={confirmation_type}, success={success}"
            )
            # TODO: Add database logging when EmailNotification model is available

        except Exception as e:
            logger.error(f"Error logging confirmation: {e}")


# Global confirmation service instance
_confirmation_service = None


def get_confirmation_service() -> ConfirmationService:
    """Get global confirmation service instance"""
    global _confirmation_service
    if _confirmation_service is None:
        _confirmation_service = ConfirmationService()
    return _confirmation_service
