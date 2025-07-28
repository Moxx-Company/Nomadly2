"""
Domain Registration Progress Notification System
Provides friendly updates to users during the domain registration process
"""

import logging
import requests
import asyncio
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)


class DomainProgressNotifier:
    def __init__(self, config: Config):
        self.config = config
        self.bot_token = "8058274028:AAFSNDsJ5upG_gLEkWOl9M5apgTypkNDecQ"

    async def send_progress_notification(
        self,
        user_telegram_id: int,
        domain_name: str,
        stage: str,
        order_id: int,
        details: Optional[dict] = None,
    ):
        """Send domain registration progress notification to user"""
        try:
            message = self._create_progress_message(
                domain_name, stage, order_id, details
            )

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": user_telegram_id,
                "text": message,
                "parse_mode": "HTML",  # Changed from Markdown to HTML to avoid formatting issues
            }

            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(
                    f"Progress notification sent: {stage} for domain {domain_name}"
                )
            else:
                logger.error(
                    f"Failed to send progress notification: {response.status_code} - {response.text}"
                )
                # Try without parse_mode as fallback
                data["parse_mode"] = None
                response = requests.post(url, json=data, timeout=10)
                if response.status_code == 200:
                    logger.info(
                        f"Progress notification sent (plain text): {stage} for domain {domain_name}"
                    )

        except Exception as e:
            logger.error(f"Error sending progress notification: {e}")

    def _create_progress_message(
        self,
        domain_name: str,
        stage: str,
        order_id: int,
        details: Optional[dict] = None,
    ) -> str:
        """Create user-friendly progress message based on stage"""
        base_info = f"🌐 <b>{domain_name}</b> | Order #{order_id}"

        if stage == "dns_setup_started":
            return f"""🚀 <b>Domain Setup Started!</b>

{base_info}

✅ Payment confirmed
🔧 Setting up DNS infrastructure...

⏱️ Next: DNS zone creation"""

        elif stage == "dns_zone_created":
            return f"""📡 <b>DNS Infrastructure Ready!</b>

{base_info}

✅ Payment confirmed
✅ DNS zone created
🔧 Configuring domain records...

⏱️ Next: Official domain registration"""

        elif stage == "domain_registration_started":
            return f"""📝 <b>Official Registration Starting!</b>

{base_info}

✅ Payment confirmed
✅ DNS infrastructure ready
🔧 Registering with domain authority...

⏱️ Next: Nameserver configuration"""

        elif stage == "domain_registered":
            nameservers = details.get("nameservers", []) if details else []
            ns_display = nameservers[:2] if nameservers else ["Configuring..."]
            return f"""🎉 <b>Domain Successfully Registered!</b>

{base_info}

✅ Payment confirmed
✅ DNS infrastructure ready
✅ Domain officially registered
🔧 Final nameserver configuration...

Nameservers: {', '.join(ns_display)}
⏱️ Next: Final activation"""

        elif stage == "domain_ready":
            return f"""🎊 <b>Domain Registration Complete!</b>

{base_info}

✅ Payment confirmed
✅ DNS infrastructure ready
✅ Domain officially registered
✅ Nameservers configured
✅ Domain fully operational

🌍 Your domain: https://{domain_name}
📞 Support: @Nomadly_Support

Thank you for choosing Nomadly! 🚀"""

        elif stage == "dns_setup_failed":
            error = (
                details.get("error", "Unknown error") if details else "Unknown error"
            )
            return f"""❌ <b>DNS Setup Issue</b>

{base_info}

✅ Payment confirmed
❌ DNS configuration encountered an issue

Don't worry! Our technical team has been notified and will resolve this quickly. Your payment is secure and your domain registration will be completed.

<b>Issue:</b> {error}
🔧 <b>Action:</b> Admin team investigating
📧 <b>Updates:</b> You'll be notified once resolved

<b>Need immediate help?</b> Contact @Nomadly_Support"""

        elif stage == "registration_failed":
            error = (
                details.get("error", "Unknown error") if details else "Unknown error"
            )
            return f"""❌ <b>Registration Issue Detected</b>

{base_info}

✅ Payment confirmed
✅ DNS infrastructure ready
❌ Domain registration encountered an issue

Our admin team has been automatically notified and will resolve this immediately. Your payment is protected and the registration will be completed.

<b>Issue:</b> {error}
🔧 <b>Action:</b> Priority resolution in progress
📧 <b>Updates:</b> You'll receive confirmation once completed

<b>Need assistance?</b> Contact @Nomadly_Support"""

        else:
            return f"""📋 **Domain Status Update**

{base_info}

Your domain registration is being processed. Our technical team is working on your order and you'll receive detailed updates as we progress.

📧 You'll be notified at each major milestone
📞 Contact @Nomadly_Support for questions"""

    def send_progress_notification_sync(
        self,
        user_telegram_id: int,
        domain_name: str,
        stage: str,
        order_id: int,
        details: Optional[dict] = None,
    ):
        """Synchronous version for use in non-async contexts"""
        try:
            message = self._create_progress_message(
                domain_name, stage, order_id, details
            )

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": user_telegram_id,
                "text": message,
                "parse_mode": "Markdown",
            }

            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(
                    f"Progress notification sent: {stage} for domain {domain_name}"
                )
                return True
            else:
                logger.error(
                    f"Failed to send progress notification: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Error sending progress notification: {e}")
            return False
