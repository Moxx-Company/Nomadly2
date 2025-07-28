"""
Infobip API integration for email communications
"""

import os
import logging
import requests
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class InfobipAPI:
    """Infobip API client for email communications"""

    def __init__(self):
        self.api_key = os.getenv("INFOBIP_API_KEY")
        base_url = os.getenv("INFOBIP_BASE_URL", "https://api.infobip.com")
        # Ensure the base URL has the proper scheme
        if not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"
        self.base_url = base_url
        self.from_email = os.getenv("INFOBIP_FROM_EMAIL", "noreply@nomadly.com")
        self.from_name = os.getenv("INFOBIP_FROM_NAME", "Nomadly")

        if not self.api_key:
            logger.warning("Infobip API key not configured")

    def send_email(
        self, to_email: str, subject: str, html_content: str, text_content: str = None
    ) -> Dict[str, Any]:
        """Send an email via Infobip"""
        try:
            if not self.api_key:
                return {"success": False, "error": "Infobip API key not configured"}

            headers = {"Authorization": f"App {self.api_key}"}

            # Use multipart form data (files parameter)
            files = {
                "from": (None, self.from_email),
                "to": (None, to_email),
                "subject": (None, subject),
                "html": (None, html_content),
            }

            # Add text content if provided
            if text_content:
                files["text"] = (None, text_content)

            response = requests.post(
                f"{self.base_url}/email/1/send",
                headers=headers,
                files=files,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Email sent successfully to {to_email}")
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("messageId"),
                    "status": result.get("messages", [{}])[0]
                    .get("status", {})
                    .get("description"),
                }
            else:
                logger.error(
                    f"Infobip email failed: {response.status_code} - {response.text}"
                )
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                }

        except Exception as e:
            logger.error(f"Infobip email error: {e}")
            return {"success": False, "error": str(e)}

    def send_welcome_email(
        self, to_email: str, user_name: str = None
    ) -> Dict[str, Any]:
        """Send welcome email to new user"""
        subject = "🎭 Welcome to Nomadly - Your Privacy Journey Begins"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Nomadly</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #0a0a0a; color: #e0e0e0; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #1a1a1a; }}
                .header {{ background: linear-gradient(135deg, #2d1b69 0%, #11998e 100%); padding: 40px 20px; text-align: center; }}
                .logo {{ font-size: 32px; font-weight: bold; color: #ffffff; margin-bottom: 10px; }}
                .content {{ padding: 30px 20px; }}
                .welcome-box {{ background-color: #252525; border-radius: 10px; padding: 25px; margin: 20px 0; border-left: 4px solid #11998e; }}
                .feature {{ margin: 15px 0; padding: 15px; background-color: #2a2a2a; border-radius: 8px; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #11998e 0%, #2d1b69 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: bold; }}
                .footer {{ background-color: #0f0f0f; padding: 20px; text-align: center; font-size: 12px; color: #888; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎭 Nomadly</div>
                    <p style="margin: 0; opacity: 0.9;">Offshore Hosting • Privacy First • Anonymous</p>
                </div>
                
                <div class="content">
                    <div class="welcome-box">
                        <h2 style="margin-top: 0; color: #11998e;">🚀 Welcome to the Underground!</h2>
                        <p>{"Hi " + (user_name or "Privacy Seeker") + "," if user_name else "Hello Privacy Seeker,"}</p>
                        <p>You've just joined the most discreet hosting community on the internet. Your journey into true digital independence starts now.</p>
                    </div>
                    
                    <h3 style="color: #11998e;">🛡️ What Makes Nomadly Special?</h3>
                    
                    <div class="feature">
                        <strong>🌍 Offshore Jurisdiction Protection</strong><br>
                        Your content is protected by privacy-friendly jurisdictions that respect digital freedom.
                    </div>
                    
                    <div class="feature">
                        <strong>🔒 Anti-Red & Anti-Ban Technology</strong><br>
                        Advanced systems designed to keep your sites online and undetected.
                    </div>
                    
                    <div class="feature">
                        <strong>💰 Cryptocurrency Payments Only</strong><br>
                        Complete financial anonymity with Bitcoin, Ethereum, Litecoin and more.
                    </div>
                    
                    <div class="feature">
                        <strong>🤐 Zero-Knowledge Operations</strong><br>
                        We don't log, we don't track, we don't know - that's how it should be.
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://t.me/nomadly" class="cta-button">🎯 Start Your First Project</a>
                    </div>
                    
                    <div style="background-color: #1f1f1f; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h4 style="color: #11998e; margin-top: 0;">🎁 Special Welcome Bonus</h4>
                        <p>Get <strong>5% extra credits</strong> on your first deposit of $25 or more!</p>
                        <p><em>Use this bonus to explore our hosting plans risk-free.</em></p>
                    </div>
                    
                    <p style="margin-top: 30px;">Need help getting started? Our anonymous support team is ready:</p>
                    <p>
                        📞 <strong>Live Support:</strong> <a href="https://t.me/nomadlyhelp" style="color: #11998e;">@nomadlyhelp</a><br>
                        📢 <strong>Updates:</strong> <a href="https://t.me/nomadly" style="color: #11998e;">@nomadly</a>
                    </p>
                </div>
                
                <div class="footer">
                    <p>This email was sent because you registered for Nomadly services.</p>
                    <p>🎭 <strong>Nomadly</strong> - Where Privacy Meets Performance</p>
                    <p style="font-size: 10px; margin-top: 15px;">
                        For maximum privacy, this email will self-destruct from our servers within 30 days.<br>
                        No tracking pixels • No analytics • No data retention
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to Nomadly - Your Privacy Journey Begins!
        
        {"Hi " + (user_name or "Privacy Seeker") + "," if user_name else "Hello Privacy Seeker,"}
        
        You've just joined the most discreet hosting community on the internet.
        
        What Makes Nomadly Special:
        🌍 Offshore Jurisdiction Protection
        🔒 Anti-Red & Anti-Ban Technology  
        💰 Cryptocurrency Payments Only
        🤐 Zero-Knowledge Operations
        
        Special Welcome Bonus:
        Get 5% extra credits on your first deposit of $25 or more!
        
        Get Started: https://t.me/nomadly
        Support: https://t.me/nomadlyhelp
        
        Nomadly - Where Privacy Meets Performance
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_payment_receipt(
        self, to_email: str, order_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send payment receipt email"""
        order_id = order_details.get("order_id", "N/A")
        amount = order_details.get("amount", "0")
        currency = order_details.get("currency", "USD")
        plan_type = order_details.get("plan_type", "Hosting")
        domain = order_details.get("domain", "N/A")

        subject = f"🎯 Payment Confirmed - Order #{order_id} | Nomadly"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Payment Receipt - Nomadly</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #0a0a0a; color: #e0e0e0; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #1a1a1a; }}
                .header {{ background: linear-gradient(135deg, #2d1b69 0%, #11998e 100%); padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; }}
                .receipt-box {{ background-color: #252525; border-radius: 10px; padding: 25px; margin: 20px 0; border: 2px solid #11998e; }}
                .order-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #333; }}
                .total-row {{ font-weight: bold; font-size: 18px; color: #11998e; }}
                .footer {{ background-color: #0f0f0f; padding: 20px; text-align: center; font-size: 12px; color: #888; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; color: white;">✅ Payment Confirmed!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Your order is being processed</p>
                </div>
                
                <div class="content">
                    <div class="receipt-box">
                        <h2 style="margin-top: 0; color: #11998e;">📋 Order Receipt</h2>
                        
                        <div class="order-row">
                            <span>Order ID:</span>
                            <span><strong>#{order_id}</strong></span>
                        </div>
                        
                        <div class="order-row">
                            <span>Service:</span>
                            <span>{plan_type}</span>
                        </div>
                        
                        {f'<div class="order-row"><span>Domain:</span><span>{domain}</span></div>' if domain != 'N/A' else ''}
                        
                        <div class="order-row">
                            <span>Payment Method:</span>
                            <span>Cryptocurrency ({currency})</span>
                        </div>
                        
                        <div class="order-row total-row">
                            <span>Total Paid:</span>
                            <span>${amount} USD</span>
                        </div>
                    </div>
                    
                    <div style="background-color: #1f2f1f; border-radius: 10px; padding: 20px; margin: 20px 0; border-left: 4px solid #4caf50;">
                        <h3 style="margin-top: 0; color: #4caf50;">🚀 What Happens Next?</h3>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>Your hosting environment is being prepared</li>
                            <li>DNS configuration will be completed automatically</li>
                            <li>You'll receive access credentials within 15 minutes</li>
                            <li>Anti-red and anti-ban protection is being activated</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <p>Track your order status in our bot:</p>
                        <a href="https://t.me/nomadly" style="display: inline-block; background: linear-gradient(135deg, #11998e 0%, #2d1b69 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold;">🎯 Open Nomadly Bot</a>
                    </div>
                    
                    <p>Questions? Our anonymous support team is available 24/7:</p>
                    <p>📞 <a href="https://t.me/nomadlyhelp" style="color: #11998e;">@nomadlyhelp</a></p>
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing Nomadly for your privacy needs.</p>
                    <p>🎭 <strong>Nomadly</strong> - Offshore • Anonymous • Secure</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)

    def send_hosting_ready_email(
        self, to_email: str, hosting_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send hosting ready notification email"""
        domain = hosting_details.get("domain", "your-domain.com")
        plan = hosting_details.get("plan", "Nomadly Plan")

        subject = f"🎉 Your Hosting is Live! {domain} | Nomadly"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Hosting Ready - Nomadly</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #0a0a0a; color: #e0e0e0; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #1a1a1a; }}
                .header {{ background: linear-gradient(135deg, #2d1b69 0%, #11998e 100%); padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; }}
                .success-box {{ background-color: #1f3f1f; border-radius: 10px; padding: 25px; margin: 20px 0; border: 2px solid #4caf50; }}
                .credentials-box {{ background-color: #2a2a2a; border-radius: 10px; padding: 20px; margin: 20px 0; border-left: 4px solid #ff9800; }}
                .footer {{ background-color: #0f0f0f; padding: 20px; text-align: center; font-size: 12px; color: #888; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; color: white;">🎉 Your Hosting is Live!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Welcome to the underground</p>
                </div>
                
                <div class="content">
                    <div class="success-box">
                        <h2 style="margin-top: 0; color: #4caf50;">✅ {domain} is Ready!</h2>
                        <p>Your <strong>{plan}</strong> hosting environment is now active and protected by our offshore infrastructure.</p>
                        <p>🛡️ <strong>Anti-red protection:</strong> Enabled<br>
                           🚫 <strong>Anti-ban security:</strong> Active<br>
                           🌍 <strong>Offshore jurisdiction:</strong> Protected</p>
                    </div>
                    
                    <div class="credentials-box">
                        <h3 style="margin-top: 0; color: #ff9800;">🔑 Access Your Hosting</h3>
                        <p><strong>Important:</strong> Your hosting credentials have been securely delivered through our Telegram bot for maximum privacy.</p>
                        <p>Open the Nomadly bot to:</p>
                        <ul>
                            <li>View your hosting login details</li>
                            <li>Manage DNS records</li>
                            <li>Access your control panel</li>
                            <li>Monitor your services</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="https://t.me/nomadly" style="display: inline-block; background: linear-gradient(135deg, #11998e 0%, #2d1b69 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold;">🎯 Access Hosting Dashboard</a>
                        </div>
                    </div>
                    
                    <div style="background-color: #252525; border-radius: 10px; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #11998e; margin-top: 0;">🚀 Next Steps</h3>
                        <ol>
                            <li><strong>Upload your content</strong> via FTP or file manager</li>
                            <li><strong>Configure your applications</strong> using our optimized environment</li>
                            <li><strong>Monitor performance</strong> through our bot interface</li>
                            <li><strong>Scale as needed</strong> with additional resources</li>
                        </ol>
                    </div>
                    
                    <p>Need assistance? Our experts are standing by:</p>
                    <p>
                        📞 <strong>Live Support:</strong> <a href="https://t.me/nomadlyhelp" style="color: #11998e;">@nomadlyhelp</a><br>
                        📢 <strong>Updates:</strong> <a href="https://t.me/nomadly" style="color: #11998e;">@nomadly</a>
                    </p>
                </div>
                
                <div class="footer">
                    <p>Your privacy is our priority. This notification contains no tracking elements.</p>
                    <p>🎭 <strong>Nomadly</strong> - Offshore • Anonymous • Secure</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)
