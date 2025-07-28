#!/usr/bin/env python3
"""
Brevo (formerly Sendinblue) Email Service for Nomadly
Handles all transactional emails including welcome emails and domain registration confirmations
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

class BrevoEmailService:
    """Brevo email service for sending transactional emails"""
    
    def __init__(self):
        """Initialize Brevo email service with API key"""
        self.api_key = os.getenv("BREVO_API_KEY")
        self.base_url = "https://api.brevo.com/v3"
        self.sender_email = "noreply@nomadly.io"
        self.sender_name = "Nomadly Domain Services"
        
        if not self.api_key:
            logger.warning("⚠️ BREVO_API_KEY not configured - email service disabled")
        else:
            logger.info("✅ Brevo email service initialized")
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None,
        template_id: Optional[int] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send email via Brevo API
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of email
            text_content: Plain text content (optional)
            template_id: Brevo template ID (optional)
            params: Template parameters (optional)
            
        Returns:
            Dict with success status and message ID
        """
        if not self.api_key:
            logger.warning("Email not sent - Brevo API key not configured")
            return {"success": False, "error": "Email service not configured"}
        
        try:
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": self.api_key
            }
            
            # Build email data
            email_data = {
                "sender": {
                    "name": self.sender_name,
                    "email": self.sender_email
                },
                "to": [{
                    "email": to_email
                }],
                "subject": subject
            }
            
            # Use template or direct content
            if template_id and params:
                email_data["templateId"] = template_id
                email_data["params"] = params
            else:
                email_data["htmlContent"] = html_content
                if text_content:
                    email_data["textContent"] = text_content
            
            # Send email via Brevo API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/smtp/email",
                    headers=headers,
                    json=email_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"✅ Email sent successfully to {to_email} - ID: {result.get('messageId')}")
                    return {
                        "success": True,
                        "message_id": result.get("messageId")
                    }
                else:
                    error_msg = f"Brevo API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_welcome_email(self, email: str, domain: str, order_id: str) -> Dict[str, Any]:
        """
        Send welcome email after domain registration starts
        
        Args:
            email: Technical contact email
            domain: Domain being registered
            order_id: Order reference number
            
        Returns:
            Dict with success status
        """
        subject = f"🏴‍☠️ Welcome to Nomadly - Domain Registration Started for {domain}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #1a1a1a; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏴‍☠️ Nomadly Domain Services</h1>
                    <p>Your Gateway to Private Domain Registration</p>
                </div>
                
                <div class="content">
                    <h2>Welcome to Nomadly!</h2>
                    
                    <p>Thank you for choosing Nomadly for your domain registration needs. We've received your payment and are processing your domain registration.</p>
                    
                    <div class="info-box">
                        <h3>Registration Details:</h3>
                        <p><strong>Domain:</strong> {domain}</p>
                        <p><strong>Order ID:</strong> {order_id}</p>
                        <p><strong>Status:</strong> Processing</p>
                    </div>
                    
                    <h3>What Happens Next?</h3>
                    <ul>
                        <li>Domain availability verification</li>
                        <li>Nameserver configuration</li>
                        <li>WHOIS privacy protection activation</li>
                        <li>Domain activation (usually within 5-10 minutes)</li>
                    </ul>
                    
                    <p>You'll receive another email once your domain registration is complete.</p>
                    
                    <h3>Need Help?</h3>
                    <p>Access our support through the Nomadly Telegram bot or visit our FAQ section.</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated email from Nomadly Domain Services</p>
                    <p>🏴‍☠️ Offshore Hosting - Resilience | Discretion | Independence</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Nomadly!
        
        Thank you for choosing Nomadly for your domain registration needs. 
        We've received your payment and are processing your domain registration.
        
        Registration Details:
        - Domain: {domain}
        - Order ID: {order_id}
        - Status: Processing
        
        What Happens Next?
        - Domain availability verification
        - Nameserver configuration
        - WHOIS privacy protection activation
        - Domain activation (usually within 5-10 minutes)
        
        You'll receive another email once your domain registration is complete.
        
        Need Help?
        Access our support through the Nomadly Telegram bot.
        
        🏴‍☠️ Nomadly Domain Services
        Offshore Hosting - Resilience | Discretion | Independence
        """
        
        return await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_registration_complete_email(
        self, 
        email: str, 
        domain: str, 
        order_id: str,
        nameservers: List[str],
        expiry_date: str
    ) -> Dict[str, Any]:
        """
        Send confirmation email after domain registration completes
        
        Args:
            email: Technical contact email
            domain: Registered domain
            order_id: Order reference number
            nameservers: List of configured nameservers
            expiry_date: Domain expiry date
            
        Returns:
            Dict with success status
        """
        subject = f"✅ Domain Registration Complete - {domain} is now active!"
        
        ns_list = "\n".join([f"<li>{ns}</li>" for ns in nameservers])
        ns_text = "\n".join([f"- {ns}" for ns in nameservers])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .success-box {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #28a745; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Registration Complete!</h1>
                    <p>Your domain is now active</p>
                </div>
                
                <div class="content">
                    <div class="success-box">
                        <h2>🎉 Congratulations!</h2>
                        <p>Your domain <strong>{domain}</strong> has been successfully registered and is now active.</p>
                    </div>
                    
                    <div class="info-box">
                        <h3>Domain Information:</h3>
                        <p><strong>Domain:</strong> {domain}</p>
                        <p><strong>Order ID:</strong> {order_id}</p>
                        <p><strong>Status:</strong> Active</p>
                        <p><strong>Registration Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                        <p><strong>Expiry Date:</strong> {expiry_date}</p>
                    </div>
                    
                    <div class="info-box">
                        <h3>Nameservers:</h3>
                        <ul>
                            {ns_list}
                        </ul>
                    </div>
                    
                    <div class="info-box">
                        <h3>WHOIS Privacy:</h3>
                        <p>✅ WHOIS privacy protection is active. Your personal information is hidden from public WHOIS lookups.</p>
                    </div>
                    
                    <h3>What's Next?</h3>
                    <ul>
                        <li>Configure DNS records through the Nomadly bot</li>
                        <li>Set up your website or email services</li>
                        <li>Monitor your domain through "My Domains" in the bot</li>
                    </ul>
                    
                    <h3>Important Notes:</h3>
                    <ul>
                        <li>DNS changes can take up to 48 hours to propagate globally</li>
                        <li>Your domain will auto-renew before expiry (if wallet funded)</li>
                        <li>Keep your technical contact email updated</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing Nomadly Domain Services</p>
                    <p>🏴‍☠️ Offshore Hosting - Resilience | Discretion | Independence</p>
                    <p>Manage your domain anytime through the Nomadly Telegram bot</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Registration Complete!
        
        Congratulations! Your domain {domain} has been successfully registered and is now active.
        
        Domain Information:
        - Domain: {domain}
        - Order ID: {order_id}
        - Status: Active
        - Registration Date: {datetime.now().strftime('%B %d, %Y')}
        - Expiry Date: {expiry_date}
        
        Nameservers:
        {ns_text}
        
        WHOIS Privacy:
        ✅ WHOIS privacy protection is active. Your personal information is hidden from public WHOIS lookups.
        
        What's Next?
        - Configure DNS records through the Nomadly bot
        - Set up your website or email services
        - Monitor your domain through "My Domains" in the bot
        
        Important Notes:
        - DNS changes can take up to 48 hours to propagate globally
        - Your domain will auto-renew before expiry (if wallet funded)
        - Keep your technical contact email updated
        
        Thank you for choosing Nomadly Domain Services
        🏴‍☠️ Offshore Hosting - Resilience | Discretion | Independence
        """
        
        return await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_payment_confirmation_email(
        self,
        email: str,
        domain: str,
        order_id: str,
        amount: float,
        crypto_type: str,
        crypto_amount: float
    ) -> Dict[str, Any]:
        """
        Send payment confirmation email
        
        Args:
            email: Technical contact email
            domain: Domain being registered
            order_id: Order reference number
            amount: USD amount
            crypto_type: Cryptocurrency used
            crypto_amount: Amount in cryptocurrency
            
        Returns:
            Dict with success status
        """
        crypto_names = {
            'btc': 'Bitcoin',
            'eth': 'Ethereum',
            'ltc': 'Litecoin',
            'doge': 'Dogecoin'
        }
        crypto_name = crypto_names.get(crypto_type.lower(), crypto_type.upper())
        
        subject = f"💰 Payment Received - {domain} registration in progress"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #17a2b8; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #17a2b8; }}
                .payment-box {{ background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💰 Payment Confirmed</h1>
                    <p>Thank you for your payment!</p>
                </div>
                
                <div class="content">
                    <div class="payment-box">
                        <h3>Payment Details:</h3>
                        <p><strong>Amount:</strong> ${amount:.2f} USD</p>
                        <p><strong>Cryptocurrency:</strong> {crypto_amount:.8f} {crypto_name}</p>
                        <p><strong>Order ID:</strong> {order_id}</p>
                        <p><strong>Status:</strong> Confirmed</p>
                    </div>
                    
                    <p>We've received your payment and are now processing your domain registration for <strong>{domain}</strong>.</p>
                    
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>Domain availability verification</li>
                        <li>Customer account creation</li>
                        <li>Nameserver configuration</li>
                        <li>Domain registration with registrar</li>
                        <li>WHOIS privacy activation</li>
                    </ol>
                    
                    <p>This process typically takes 5-10 minutes. You'll receive another email once your domain is active.</p>
                </div>
                
                <div class="footer">
                    <p>🏴‍☠️ Nomadly Domain Services</p>
                    <p>Offshore Hosting - Resilience | Discretion | Independence</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Payment Confirmed
        
        Thank you for your payment!
        
        Payment Details:
        - Amount: ${amount:.2f} USD
        - Cryptocurrency: {crypto_amount:.8f} {crypto_name}
        - Order ID: {order_id}
        - Status: Confirmed
        
        We've received your payment and are now processing your domain registration for {domain}.
        
        Next Steps:
        1. Domain availability verification
        2. Customer account creation
        3. Nameserver configuration
        4. Domain registration with registrar
        5. WHOIS privacy activation
        
        This process typically takes 5-10 minutes. You'll receive another email once your domain is active.
        
        🏴‍☠️ Nomadly Domain Services
        Offshore Hosting - Resilience | Discretion | Independence
        """
        
        return await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

# Singleton instance
_email_service = None

def get_email_service() -> BrevoEmailService:
    """Get singleton email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = BrevoEmailService()
    return _email_service