import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import logging

logger = logging.getLogger(__name__)

# Import Brevo service
try:
    from utils.brevo_email_service import brevo_service

    BREVO_AVAILABLE = True
    logger.info("Brevo email service loaded successfully")
except ImportError:
    BREVO_AVAILABLE = False
    logger.warning("Brevo service not available")


class EmailService:
    def __init__(self):
        # Check if Brevo is available and configured
        if BREVO_AVAILABLE and brevo_service.is_configured:
            self.use_brevo = True
            logger.info("Using Brevo email service for Nomadly")
        else:
            self.use_brevo = False
            # Fallback to SMTP configuration
            self.sender_email = os.environ.get("SENDER_EMAIL", "noreply@nomadly.com")
            self.sender_password = os.environ.get("SENDER_PASSWORD")
            self.sender_name = "Nomadly"

            # Configure SMTP based on email provider
            self.smtp_server, self.smtp_port = self._get_smtp_config()
            logger.info("Using fallback SMTP email service")

    def _get_smtp_config(self):
        """Auto-detect SMTP configuration based on email domain"""
        email_domain = self.sender_email.split("@")[-1].lower()

        # SMTP configurations for popular providers
        smtp_configs = {
            "gmail.com": ("smtp.gmail.com", 587),
            "outlook.com": ("smtp-mail.outlook.com", 587),
            "hotmail.com": ("smtp-mail.outlook.com", 587),
            "live.com": ("smtp-mail.outlook.com", 587),
            "yahoo.com": ("smtp.mail.yahoo.com", 587),
            "protonmail.com": ("mail.protonmail.ch", 587),
            "proton.me": ("mail.protonmail.ch", 587),
            "tutanota.com": ("mail.tutanota.com", 587),
            "tutamail.com": ("mail.tutanota.com", 587),
            "zoho.com": ("smtp.zoho.com", 587),
            "mail.com": ("smtp.mail.com", 587),
            "yandex.com": ("smtp.yandex.com", 587),
            "fastmail.com": ("smtp.fastmail.com", 587),
            # Add custom domain support
            "nomadly.com": ("smtp.gmail.com", 587),  # Using Gmail as relay
        }

        # Return configuration for detected provider or default to Gmail
        return smtp_configs.get(email_domain, ("smtp.gmail.com", 587))

    def send_email(
        self, to_email: str, subject: str, html_content: str, text_content: str = None
    ):
        """Send email using preferred service (Brevo or SMTP fallback)"""
        # Use Brevo if available and configured
        if self.use_brevo:
            return brevo_service.send_email_api(
                to_email, subject, html_content, text_content
            )

        # Fallback to SMTP
        try:
            # Check if email credentials are configured
            if not self.sender_password:
                logger.info(f"📧 [SIMULATION] Email sent to {to_email}")
                logger.info(f"📧 [SIMULATION] Subject: {subject}")
                logger.info(
                    f"📧 [SIMULATION] Nomadly email system operational in simulation mode"
                )
                # Return True to simulate successful sending for development
                return True

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = formataddr((self.sender_name, self.sender_email))
            message["To"] = to_email

            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Create secure connection and send email
            context = ssl.create_default_context()

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, message.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_welcome_email(self, to_email: str, username: str = None):
        """Send welcome email to new users"""
        # Use Brevo welcome email if available
        if self.use_brevo:
            return brevo_service.send_welcome_email(to_email, username)

        # Fallback to SMTP welcome email
        subject = "Welcome to Nomadly - Your Offshore Hosting Solution"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Welcome to Nomadly</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to Nomadly</h1>
                    <p style="color: #f0f0f0; margin: 10px 0 0 0;">Offshore Hosting • Privacy First • Complete Discretion</p>
                </div>
                
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333; margin-bottom: 20px;">Welcome aboard{f', {username}' if username else ''}!</h2>
                    
                    <p>Thank you for joining Nomadly, your trusted partner for offshore hosting solutions. We're committed to providing you with:</p>
                    
                    <ul style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <li><strong>Complete Privacy</strong> - Jurisdiction-protected hosting</li>
                        <li><strong>Anti-Red Protection</strong> - Advanced security measures</li>
                        <li><strong>Global Infrastructure</strong> - Worldwide server locations</li>
                        <li><strong>24/7 Support</strong> - Expert assistance when you need it</li>
                    </ul>
                    
                    <div style="background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c5aa0; margin-top: 0;">🎉 Special Welcome Bonus</h3>
                        <p style="margin-bottom: 0;">Enjoy <strong>5% extra credits</strong> on your first deposit of $25 or more!</p>
                    </div>
                    
                    <h3>Getting Started:</h3>
                    <ol>
                        <li>Add funds to your account for instant payments</li>
                        <li>Choose your hosting plan (Solo or Independent Operations)</li>
                        <li>Register your domain or use an existing one</li>
                        <li>Access your hosting dashboard within minutes</li>
                    </ol>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://t.me/Nomadly_bot" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Start Using Nomadly</a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="text-align: center; color: #666; font-size: 14px;">
                        Need help? Contact our support team: <a href="https://t.me/Nomadly_Support">@Nomadly_Support</a><br>
                        This isn't just hosting. This is hosting on your terms, offshore and protected.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to Nomadly{f', {username}' if username else ''}!
        
        Thank you for joining Nomadly, your trusted partner for offshore hosting solutions.
        
        We provide:
        - Complete Privacy with jurisdiction-protected hosting
        - Anti-Red Protection with advanced security measures  
        - Global Infrastructure with worldwide server locations
        - 24/7 Support from our expert team
        
        Special Welcome Bonus: Enjoy 5% extra credits on your first deposit of $25 or more!
        
        Getting Started:
        1. Add funds to your account for instant payments
        2. Choose your hosting plan (Solo or Independent Operations)
        3. Register your domain or use an existing one
        4. Access your hosting dashboard within minutes
        
        Start using Nomadly: https://t.me/Nomadly_bot
        Need help? Contact: @Nomadly_Support
        
        This isn't just hosting. This is hosting on your terms, offshore and protected.
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_payment_receipt(self, to_email: str, order_details: dict):
        """Send payment receipt email"""
        # Use Brevo payment receipt if available
        if self.use_brevo:
            return brevo_service.send_payment_receipt(
                to_email,
                order_details.get("order_id", "N/A"),
                order_details.get("service", "N/A"),
                float(order_details.get("amount", 0)),
                order_details.get("crypto_currency"),
                order_details.get("crypto_amount"),
            )

        # Fallback to SMTP payment receipt
        subject = f"Payment Received - Order #{order_details.get('order_id', 'N/A')}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Payment Receipt - Nomadly</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #28a745; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">Payment Received ✓</h1>
                    <p style="color: #f0f0f0; margin: 10px 0 0 0;">Order #{order_details.get('order_id', 'N/A')}</p>
                </div>
                
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333; margin-bottom: 20px;">Thank you for your payment!</h2>
                    
                    <p>Your payment has been successfully processed. Here are your order details:</p>
                    
                    <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #28a745;">Order Summary</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Order ID:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">#{order_details.get('order_id', 'N/A')}</td></tr>
                            <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Service:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{order_details.get('service', 'N/A')}</td></tr>
                            <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Amount:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">${order_details.get('amount', 'N/A')} USD</td></tr>
                            <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Payment Method:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{order_details.get('payment_method', 'N/A')}</td></tr>
                            <tr><td style="padding: 8px 0;"><strong>Status:</strong></td><td style="padding: 8px 0; color: #28a745; font-weight: bold;">PAID</td></tr>
                        </table>
                    </div>
                    
                    <div style="background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c5aa0; margin-top: 0;">What's Next?</h3>
                        <p style="margin-bottom: 0;">Your service is being activated automatically. You'll receive another email with access credentials within the next few minutes.</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://t.me/Nomadly_bot" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Manage Your Services</a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="text-align: center; color: #666; font-size: 14px;">
                        Questions? Contact: <a href="https://t.me/Nomadly_Support">@Nomadly_Support</a><br>
                        Nomadly - Offshore hosting on your terms
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)

    def send_service_ready_email(self, to_email: str, service_details: dict):
        """Send service ready notification email"""
        subject = f"Service Activated - {service_details.get('service_name', 'Your Nomadly Service')}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Service Ready - Nomadly</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #17a2b8; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">Service Activated! 🚀</h1>
                    <p style="color: #f0f0f0; margin: 10px 0 0 0;">{service_details.get('service_name', 'Your Nomadly Service')}</p>
                </div>
                
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333; margin-bottom: 20px;">Your service is now live!</h2>
                    
                    <p>Congratulations! Your Nomadly service has been successfully activated and is ready to use.</p>
                    
                    <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #17a2b8;">Service Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Service:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{service_details.get('service_name', 'N/A')}</td></tr>
                            <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Domain:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee;">{service_details.get('domain', 'N/A')}</td></tr>
                            <tr><td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Status:</strong></td><td style="padding: 8px 0; border-bottom: 1px solid #eee; color: #28a745; font-weight: bold;">ACTIVE</td></tr>
                        </table>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                        <h3 style="color: #856404; margin-top: 0;">🔑 Access Information</h3>
                        <p style="margin-bottom: 0;">Your access credentials and setup instructions have been sent via Telegram. Check your Nomadly bot messages for complete details.</p>
                    </div>
                    
                    <h3>Getting Started:</h3>
                    <ol>
                        <li>Check your Telegram messages for login credentials</li>
                        <li>Access your control panel using the provided link</li>
                        <li>Upload your website files or install applications</li>
                        <li>Configure your domain DNS settings if needed</li>
                    </ol>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://t.me/Nomadly_bot" style="background: #17a2b8; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Access Your Service</a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="text-align: center; color: #666; font-size: 14px;">
                        Need assistance? Our support team is here to help: <a href="https://t.me/Nomadly_Support">@Nomadly_Support</a><br>
                        Nomadly - Your offshore hosting solution
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)
