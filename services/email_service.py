"""
Email Service for Phase 6
Comprehensive email notification and delivery system using Brevo SMTP
"""

import os
import logging
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


# Global function that payment service expects
async def send_brevo_email(recipient_email: str, subject: str, html_content: str, **kwargs):
    """Global function wrapper for sending emails via Brevo API"""
    try:
        api_key = os.getenv("BREVO_API_KEY")
        if not api_key:
            logger.warning("📧 Brevo API key not configured, skipping email notification")
            return False
            
        # Use Brevo API instead of SMTP (more reliable)
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": api_key
        }
        
        payload = {
            "sender": {"name": "Nomadly", "email": "noreply@cloakhost.ru"},
            "to": [{"email": recipient_email}],
            "subject": subject,
            "htmlContent": html_content
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 201:
            logger.info(f"📧 Email sent successfully to {recipient_email} via Brevo API")
            return True
        else:
            logger.error(f"📧 Brevo API error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"📧 Email sending error: {e}")
        return False


class EmailService:
    """Professional email service using Brevo SMTP for Nomadly platform"""

    def __init__(self):
        # Brevo SMTP Configuration
        self.smtp_host = "smtp-relay.sendinblue.com"
        self.smtp_port = 587
        self.smtp_username = os.getenv("INFOBIP_FROM_EMAIL", "noreply@cloakhost.ru")
        self.smtp_password = os.getenv("BREVO_SMTP_KEY", "")
        self.api_key = os.getenv("BREVO_API_KEY", "")

        # Default sender information
        self.default_sender = {"name": "Nomadly Support", "email": self.smtp_username}

        # Validate configuration
        if not all([self.smtp_username, self.smtp_password]):
            logger.warning("Email service not configured - missing SMTP credentials")
            self.configured = False
        else:
            self.configured = True
            logger.info("Email service initialized successfully")

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        attachments: List[str] = None,
        sender_name: str = None,
    ) -> bool:
        """Send email via Brevo SMTP"""

        if not self.configured:
            logger.error("Email service not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = (
                f"{sender_name or self.default_sender['name']} <{self.default_sender['email']}>"
            )
            msg["To"] = recipient_email
            msg["Subject"] = subject

            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                msg.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(file_path)}",
                        )
                        msg.attach(part)

            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False

    def send_welcome_email(
        self, user_email: str, user_name: str, language: str = "en"
    ) -> bool:
        """Send welcome email to new users"""

        welcome_content = self._get_welcome_email_content(user_name, language)

        return self.send_email(
            recipient_email=user_email,
            subject=welcome_content["subject"],
            html_content=welcome_content["html"],
            text_content=welcome_content["text"],
        )

    def send_payment_confirmation(
        self,
        user_email: str,
        order_details: Dict,
        language: str = "en",
        invoice_path: str = None,
    ) -> bool:
        """Send payment confirmation email with invoice"""

        payment_content = self._get_payment_confirmation_content(
            order_details, language
        )
        attachments = (
            [invoice_path] if invoice_path and os.path.exists(invoice_path) else None
        )

        return self.send_email(
            recipient_email=user_email,
            subject=payment_content["subject"],
            html_content=payment_content["html"],
            text_content=payment_content["text"],
            attachments=attachments,
        )

    def send_service_activation(
        self,
        user_email: str,
        service_details: Dict,
        credentials: Dict = None,
        language: str = "en",
    ) -> bool:
        """Send service activation notification with credentials"""

        activation_content = self._get_service_activation_content(
            service_details, credentials, language
        )

        return self.send_email(
            recipient_email=user_email,
            subject=activation_content["subject"],
            html_content=activation_content["html"],
            text_content=activation_content["text"],
        )

    def send_domain_registration_confirmation(
        self, user_email: str, domain_details: Dict, language: str = "en"
    ) -> bool:
        """Send domain registration confirmation"""

        domain_content = self._get_domain_confirmation_content(domain_details, language)

        return self.send_email(
            recipient_email=user_email,
            subject=domain_content["subject"],
            html_content=domain_content["html"],
            text_content=domain_content["text"],
        )

    def _get_welcome_email_content(
        self, user_name: str, language: str
    ) -> Dict[str, str]:
        """Generate welcome email content"""

        templates = {
            "en": {
                "subject": f"Welcome to Nomadly, {user_name}!",
                "html": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #2c5aa0;">Welcome to Nomadly!</h1>
                        <p>Hello {user_name},</p>
                        <p>Thank you for joining Nomadly - your premium platform for offshore hosting, domain registration, and URL shortening services.</p>
                        
                        <h2>What you can do with Nomadly:</h2>
                        <ul>
                            <li><strong>Offshore Hosting:</strong> Deploy privacy-focused hosting infrastructure</li>
                            <li><strong>Domain Registration:</strong> Register domains with multiple TLD options</li>
                            <li><strong>URL Shortener:</strong> Create branded short links with analytics</li>
                            <li><strong>Secure Payments:</strong> Pay securely with cryptocurrency</li>
                        </ul>
                        
                        <p>Your account is ready to use. Start by exploring our services through the Telegram bot.</p>
                        
                        <p>Best regards,<br>The Nomadly Team</p>
                        
                        <hr style="margin: 30px 0; border: 1px solid #eee;">
                        <p style="font-size: 12px; color: #666;">
                            This is an automated message from Nomadly. If you have questions, contact @nomadlysupport
                        </p>
                    </div>
                </body>
                </html>
                """,
                "text": f"""Welcome to Nomadly!

Hello {user_name},

Thank you for joining Nomadly - your premium platform for offshore hosting, domain registration, and URL shortening services.

What you can do with Nomadly:
- Offshore Hosting: Deploy privacy-focused hosting infrastructure
- Domain Registration: Register domains with multiple TLD options  
- URL Shortener: Create branded short links with analytics
- Secure Payments: Pay securely with cryptocurrency

Your account is ready to use. Start by exploring our services through the Telegram bot.

Best regards,
The Nomadly Team

---
This is an automated message from Nomadly. If you have questions, contact @nomadlysupport""",
            }
        }

        return templates.get(language, templates["en"])

    def _get_payment_confirmation_content(
        self, order_details: Dict, language: str
    ) -> Dict[str, str]:
        """Generate payment confirmation email content"""

        amount = order_details.get("amount", "0.00")
        service = order_details.get("service_type", "Service")
        order_id = order_details.get("order_id", "N/A")

        templates = {
            "en": {
                "subject": f"Payment Confirmed - Order #{order_id}",
                "html": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #28a745;">Payment Confirmed!</h1>
                        
                        <p>Your payment has been successfully processed.</p>
                        
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h3>Order Details:</h3>
                            <p><strong>Order ID:</strong> {order_id}</p>
                            <p><strong>Service:</strong> {service}</p>
                            <p><strong>Amount:</strong> ${amount}</p>
                            <p><strong>Status:</strong> Paid</p>
                        </div>
                        
                        <p>Your service will be activated shortly. You'll receive another email with your access details.</p>
                        
                        <p>Thank you for choosing Nomadly!</p>
                        
                        <p>Best regards,<br>The Nomadly Team</p>
                    </div>
                </body>
                </html>
                """,
                "text": f"""Payment Confirmed!

Your payment has been successfully processed.

Order Details:
Order ID: {order_id}
Service: {service}
Amount: ${amount}
Status: Paid

Your service will be activated shortly. You'll receive another email with your access details.

Thank you for choosing Nomadly!

Best regards,
The Nomadly Team""",
            }
        }

        return templates.get(language, templates["en"])

    def _get_service_activation_content(
        self, service_details: Dict, credentials: Dict, language: str
    ) -> Dict[str, str]:
        """Generate service activation email content"""

        service_type = service_details.get("service_type", "Service")

        templates = {
            "en": {
                "subject": f"Service Activated - {service_type}",
                "html": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #28a745;">Service Activated!</h1>
                        
                        <p>Your {service_type} service has been successfully activated.</p>
                        
                        {self._format_credentials_html(credentials) if credentials else ''}
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <strong>Important:</strong> Please save your login credentials in a secure location.
                        </div>
                        
                        <p>If you have any questions, please contact our support team at @nomadlysupport</p>
                        
                        <p>Best regards,<br>The Nomadly Team</p>
                    </div>
                </body>
                </html>
                """,
                "text": f"""Service Activated!

Your {service_type} service has been successfully activated.

{self._format_credentials_text(credentials) if credentials else ''}

Important: Please save your login credentials in a secure location.

If you have any questions, please contact our support team at @nomadlysupport

Best regards,
The Nomadly Team""",
            }
        }

        return templates.get(language, templates["en"])

    def _get_domain_confirmation_content(
        self, domain_details: Dict, language: str
    ) -> Dict[str, str]:
        """Generate domain registration confirmation email content"""

        domain_name = domain_details.get("domain_name", "your domain")

        templates = {
            "en": {
                "subject": f"Domain Registered - {domain_name}",
                "html": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #28a745;">Domain Registered Successfully!</h1>
                        
                        <p>Your domain <strong>{domain_name}</strong> has been registered successfully.</p>
                        
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h3>Domain Information:</h3>
                            <p><strong>Domain:</strong> {domain_name}</p>
                            <p><strong>Registration Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
                            <p><strong>Status:</strong> Active</p>
                        </div>
                        
                        <p>You can now manage your domain's DNS settings through the Nomadly bot.</p>
                        
                        <p>Best regards,<br>The Nomadly Team</p>
                    </div>
                </body>
                </html>
                """,
                "text": f"""Domain Registered Successfully!

Your domain {domain_name} has been registered successfully.

Domain Information:
Domain: {domain_name}
Registration Date: {datetime.now().strftime('%Y-%m-%d')}
Status: Active

You can now manage your domain's DNS settings through the Nomadly bot.

Best regards,
The Nomadly Team""",
            }
        }

        return templates.get(language, templates["en"])

    def _format_credentials_html(self, credentials: Dict) -> str:
        """Format credentials for HTML email"""
        if not credentials:
            return ""

        html = '<div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">'
        html += "<h3>Your Login Credentials:</h3>"

        for key, value in credentials.items():
            html += f'<p><strong>{key.replace("_", " ").title()}:</strong> {value}</p>'

        html += "</div>"
        return html

    def _format_credentials_text(self, credentials: Dict) -> str:
        """Format credentials for text email"""
        if not credentials:
            return ""

        text = "\nYour Login Credentials:\n"
        for key, value in credentials.items():
            text += f'{key.replace("_", " ").title()}: {value}\n'

        return text

    def get_service_status(self) -> Dict[str, Any]:
        """Get email service status and configuration"""
        return {
            "configured": self.configured,
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "smtp_username": self.smtp_username,
            "has_api_key": bool(self.api_key),
            "has_smtp_password": bool(self.smtp_password),
        }
