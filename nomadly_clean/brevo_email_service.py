"""
Brevo (Sendinblue) email service for Nomadly
Professional email delivery with high deliverability rates
"""

import os
import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class BrevoEmailService:
    def __init__(self):
        self.api_key = os.environ.get("BREVO_API_KEY")
        self.smtp_key = os.environ.get("BREVO_SMTP_KEY")
        self.smtp_server = "smtp-relay.brevo.com"
        self.smtp_port = 587
        self.sender_email = os.environ.get(
            "BREVO_SENDER_EMAIL", "noreply@cloakhost.ru"
        )  # Configure with verified domain
        self.api_url = "https://api.brevo.com/v3"

        # Check if credentials are available
        self.is_configured = bool(self.api_key and self.smtp_key)

        if self.is_configured:
            logger.info("Brevo email service configured successfully")
        else:
            logger.warning(
                "Brevo credentials not found - email service will operate in simulation mode"
            )

    def send_email_smtp(
        self, to_email: str, subject: str, html_content: str, text_content: str = None
    ) -> bool:
        """Send email using Brevo SMTP service"""
        if not self.is_configured:
            logger.info(f"[SIMULATION] Email to {to_email}: {subject}")
            return True

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.sender_email
            msg["To"] = to_email
            msg["Subject"] = subject

            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)

            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.smtp_key)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email} via Brevo SMTP")
            return True

        except Exception as e:
            logger.error(f"Failed to send email via Brevo SMTP: {e}")
            return False

    def send_email_api(
        self, to_email: str, subject: str, html_content: str, text_content: str = None
    ) -> bool:
        """Send email using Brevo API"""
        if not self.is_configured:
            logger.info(f"[SIMULATION] Email to {to_email}: {subject}")
            return True

        try:
            headers = {"api-key": self.api_key, "Content-Type": "application/json"}

            payload = {
                "sender": {"name": "Nomadly", "email": self.sender_email},
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html_content,
            }

            if text_content:
                payload["textContent"] = text_content

            response = requests.post(
                f"{self.api_url}/smtp/email", headers=headers, json=payload, timeout=30
            )

            if response.status_code in [200, 201]:
                logger.info(f"Email sent successfully to {to_email} via Brevo API")
                return True
            else:
                logger.error(
                    f"Brevo API error: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to send email via Brevo API: {e}")
            return False

    def send_welcome_email(self, to_email: str, username: str = None) -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to Nomadly - Offshore Hosting Solutions"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Welcome to Nomadly</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; padding: 20px; background: #1a1a1a; color: white;">
                    <h1 style="margin: 0; color: #fff;">🔒 Nomadly</h1>
                    <p style="margin: 10px 0 0 0; color: #ccc;"><i>Resilient • Discrete • Independent</i></p>
                </div>
                
                <div style="padding: 30px; background: #f9f9f9;">
                    <h2 style="color: #333;">Welcome{f", {username}" if username else ""}!</h2>
                    
                    <p>Thank you for choosing Nomadly for your offshore hosting needs. Your account is now active and ready to use.</p>
                    
                    <h3 style="color: #555;">🛡️ What You Get:</h3>
                    <ul style="margin-left: 20px;">
                        <li><strong>Anti-red Protection:</strong> DMCA takedown resistance</li>
                        <li><strong>Offshore Jurisdiction:</strong> Privacy-focused hosting</li>
                        <li><strong>Anonymous Payments:</strong> Cryptocurrency support</li>
                        <li><strong>Professional DNS:</strong> Advanced domain management</li>
                    </ul>
                    
                    <h3 style="color: #555;">🚀 Getting Started:</h3>
                    <p>Your Nomadly bot is ready to use. Simply return to Telegram and explore our hosting plans, domain registration, and Inbox Shortener services.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://t.me/NomadlyOfficial_bot" style="background: #333; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Open Nomadly Bot</a>
                    </div>
                    
                    <hr style="border: 1px solid #ddd; margin: 30px 0;">
                    
                    <h3 style="color: #555;">📱 Support:</h3>
                    <p>Need help? Our support team is available 24/7:</p>
                    <p><strong>Telegram Support:</strong> @Nomadly_Support</p>
                    <p><strong>Response Time:</strong> Under 5 minutes</p>
                </div>
                
                <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                    <p>This email was sent because you registered with Nomadly.<br>
                    For support, contact @Nomadly_Support on Telegram.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to Nomadly - Offshore Hosting Solutions
        
        Welcome{f", {username}" if username else ""}!
        
        Thank you for choosing Nomadly for your offshore hosting needs. Your account is now active and ready to use.
        
        What You Get:
        • Anti-red Protection: DMCA takedown resistance
        • Offshore Jurisdiction: Privacy-focused hosting
        • Anonymous Payments: Cryptocurrency support
        • Professional DNS: Advanced domain management
        
        Getting Started:
        Your Nomadly bot is ready to use. Simply return to Telegram and explore our hosting plans, domain registration, and Inbox Shortener services.
        
        Support:
        Need help? Our support team is available 24/7:
        Telegram Support: @Nomadly_Support
        Response Time: Under 5 minutes
        
        This email was sent because you registered with Nomadly.
        For support, contact @Nomadly_Support on Telegram.
        """

        # Try API first, fallback to SMTP
        if self.send_email_api(to_email, subject, html_content, text_content):
            return True
        return self.send_email_smtp(to_email, subject, html_content, text_content)

    def send_payment_receipt(
        self,
        to_email: str,
        order_id: str,
        service_type: str,
        amount: float,
        crypto_currency: str = None,
        crypto_amount: str = None,
    ) -> bool:
        """Send payment receipt email"""
        subject = f"Payment Confirmed - Nomadly Order #{order_id}"

        payment_details = ""
        if crypto_currency and crypto_amount:
            payment_details = f"""
            <h3 style="color: #555;">💰 Payment Details:</h3>
            <ul style="margin-left: 20px;">
                <li><strong>Amount:</strong> ${amount:.2f} USD</li>
                <li><strong>Cryptocurrency:</strong> {crypto_currency}</li>
                <li><strong>Crypto Amount:</strong> {crypto_amount}</li>
                <li><strong>Status:</strong> Confirmed</li>
            </ul>
            """
        else:
            payment_details = f"""
            <h3 style="color: #555;">💰 Payment Details:</h3>
            <ul style="margin-left: 20px;">
                <li><strong>Amount:</strong> ${amount:.2f} USD</li>
                <li><strong>Payment Method:</strong> Account Balance</li>
                <li><strong>Status:</strong> Confirmed</li>
            </ul>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Payment Confirmed - Nomadly</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; padding: 20px; background: #1a1a1a; color: white;">
                    <h1 style="margin: 0; color: #fff;">🔒 Nomadly</h1>
                    <p style="margin: 10px 0 0 0; color: #ccc;">Payment Confirmed</p>
                </div>
                
                <div style="padding: 30px; background: #f9f9f9;">
                    <h2 style="color: #28a745;">✅ Payment Confirmed!</h2>
                    
                    <p>Your payment has been successfully processed and your order is now active.</p>
                    
                    <h3 style="color: #555;">📦 Order Information:</h3>
                    <ul style="margin-left: 20px;">
                        <li><strong>Order ID:</strong> #{order_id}</li>
                        <li><strong>Service:</strong> {service_type}</li>
                        <li><strong>Status:</strong> Active</li>
                    </ul>
                    
                    {payment_details}
                    
                    <h3 style="color: #555;">🚀 Next Steps:</h3>
                    <p>Your service is being activated automatically. You'll receive another email with your credentials and setup instructions within the next few minutes.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://t.me/NomadlyOfficial_bot" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Manage Your Services</a>
                    </div>
                    
                    <hr style="border: 1px solid #ddd; margin: 30px 0;">
                    
                    <p><strong>Questions?</strong> Contact our support team at @Nomadly_Support</p>
                </div>
                
                <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                    <p>Nomadly - Offshore Hosting Solutions<br>
                    For support, contact @Nomadly_Support on Telegram.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Try API first, fallback to SMTP
        if self.send_email_api(to_email, subject, html_content):
            return True
        return self.send_email_smtp(to_email, subject, html_content)

    def send_service_ready_email(
        self,
        to_email: str,
        order_id: str,
        service_type: str,
        domain_name: str = None,
        credentials: Dict[str, Any] = None,
    ) -> bool:
        """Send service ready notification email"""
        subject = f"Your {service_type} is Ready - Nomadly Order #{order_id}"

        service_details = ""
        if domain_name:
            service_details = f"""
            <h3 style="color: #555;">🌐 Service Details:</h3>
            <ul style="margin-left: 20px;">
                <li><strong>Domain:</strong> {domain_name}</li>
                <li><strong>Status:</strong> Active</li>
                <li><strong>DNS:</strong> Configured</li>
            </ul>
            """

        credential_details = ""
        if credentials:
            credential_details = """
            <h3 style="color: #555;">🔑 Access Credentials:</h3>
            <div style="background: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 5px; font-family: monospace;">
            """
            for key, value in credentials.items():
                credential_details += f"<strong>{key}:</strong> {value}<br>"
            credential_details += "</div>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Service Ready - Nomadly</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; padding: 20px; background: #1a1a1a; color: white;">
                    <h1 style="margin: 0; color: #fff;">🔒 Nomadly</h1>
                    <p style="margin: 10px 0 0 0; color: #ccc;">Service Activated</p>
                </div>
                
                <div style="padding: 30px; background: #f9f9f9;">
                    <h2 style="color: #28a745;">🚀 Your Service is Ready!</h2>
                    
                    <p>Great news! Your {service_type} has been successfully activated and is ready to use.</p>
                    
                    <h3 style="color: #555;">📦 Order Information:</h3>
                    <ul style="margin-left: 20px;">
                        <li><strong>Order ID:</strong> #{order_id}</li>
                        <li><strong>Service Type:</strong> {service_type}</li>
                        <li><strong>Status:</strong> Active</li>
                    </ul>
                    
                    {service_details}
                    {credential_details}
                    
                    <h3 style="color: #555;">🛡️ Security Features:</h3>
                    <ul style="margin-left: 20px;">
                        <li>✅ Anti-red protection enabled</li>
                        <li>✅ Offshore jurisdiction hosting</li>
                        <li>✅ SSL certificates auto-configured</li>
                        <li>✅ DDoS protection active</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://t.me/NomadlyOfficial_bot" style="background: #333; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Manage Your Account</a>
                    </div>
                    
                    <hr style="border: 1px solid #ddd; margin: 30px 0;">
                    
                    <p><strong>Need Help?</strong> Our support team is available 24/7 at @Nomadly_Support</p>
                </div>
                
                <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                    <p>Nomadly - Offshore Hosting Solutions<br>
                    Secure • Private • Reliable</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Try API first, fallback to SMTP
        if self.send_email_api(to_email, subject, html_content):
            return True
        return self.send_email_smtp(to_email, subject, html_content)

    def test_connection(self) -> Dict[str, Any]:
        """Test Brevo connection and return status"""
        if not self.is_configured:
            return {
                "status": "not_configured",
                "message": "Brevo credentials not found",
                "smtp_available": False,
                "api_available": False,
            }

        results = {
            "status": "success",
            "message": "Brevo service ready",
            "smtp_available": False,
            "api_available": False,
        }

        # Test SMTP connection
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.smtp_key)
            results["smtp_available"] = True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")

        # Test API connection
        try:
            headers = {"api-key": self.api_key}
            response = requests.get(
                f"{self.api_url}/account", headers=headers, timeout=10
            )
            if response.status_code == 200:
                results["api_available"] = True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")

        if not results["smtp_available"] and not results["api_available"]:
            results["status"] = "failed"
            results["message"] = "Both SMTP and API connections failed"

        return results


# Global instance
brevo_service = BrevoEmailService()
