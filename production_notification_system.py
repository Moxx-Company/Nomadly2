#!/usr/bin/env python3
"""
Production Dual Notification System
==================================
Comprehensive system for sending both Telegram and Email notifications
for overpayments, underpayments, and domain registrations in production
"""

import os
import sys
import asyncio
import logging
import requests
from typing import Optional, Dict, Any
sys.path.append('.')

from database import get_db_manager
from utils.brevo_email_service import BrevoEmailService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionNotificationService:
    """Production-ready notification service with Telegram + Email delivery"""
    
    def __init__(self):
        self.brevo_service = BrevoEmailService()
        self.bot_token = os.getenv('BOT_TOKEN')
        
        if not self.bot_token:
            logger.warning("BOT_TOKEN not found - Telegram notifications will be disabled")
        
        if not self.brevo_service.is_configured:
            logger.warning("Brevo not configured - Email notifications will be disabled")
    
    async def send_telegram_notification(self, telegram_id: int, message: str) -> bool:
        """Send notification via Telegram Bot API"""
        if not self.bot_token:
            logger.error("BOT_TOKEN not available for Telegram notification")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": telegram_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Telegram notification sent to user {telegram_id}")
                return True
            else:
                logger.error(f"❌ Telegram notification failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False
    
    def send_email_notification(self, email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send notification via Brevo Email API"""
        if not self.brevo_service.is_configured:
            logger.error("Brevo service not configured for email notification")
            return False
        
        try:
            success = self.brevo_service.send_email_api(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"✅ Email notification sent to {email}")
                return True
            else:
                logger.error(f"❌ Email notification failed to {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    async def send_overpayment_notification(self, telegram_id: int, overpayment_amount: float, 
                                          domain_name: str, order_id: str) -> Dict[str, bool]:
        """Send comprehensive overpayment notification via Telegram + Email"""
        results = {"telegram": False, "email": False}
        
        try:
            # Get user details
            db_manager = get_db_manager()
            user = db_manager.get_user(telegram_id)
            
            if not user:
                logger.error(f"User {telegram_id} not found for overpayment notification")
                return results
            
            # Prepare Telegram message
            telegram_message = (
                f"🎁 *Overpayment Credit Applied*\n\n"
                f"Great news! You sent more cryptocurrency than needed.\n\n"
                f"*Details:*\n"
                f"• Domain: `{domain_name}`\n"
                f"• Overpayment: `${overpayment_amount:.2f}` USD\n"
                f"• Order ID: `{order_id}`\n\n"
                f"💰 *Your overpayment has been credited to your wallet balance!*\n\n"
                f"You can use this credit for:\n"
                f"• Future domain registrations\n"
                f"• Additional services\n"
                f"• Or keep it as account balance\n\n"
                f"Check your wallet to see the updated balance."
            )
            
            # Send Telegram notification
            results["telegram"] = await self.send_telegram_notification(telegram_id, telegram_message)
            
            # Send email notification if user has email
            if user.technical_email:
                subject = f"Overpayment Credit Applied - ${overpayment_amount:.2f}"
                
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); padding: 30px; text-align: center; color: white;">
                        <h1 style="margin: 0; font-size: 24px;">🎁 Overpayment Credit Applied</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Nomadly Domain Services</p>
                    </div>
                    
                    <div style="padding: 30px; background: #f8fafc;">
                        <h2 style="color: #1e40af; margin-top: 0;">Great news!</h2>
                        <p>You sent more cryptocurrency than needed for your domain registration, and we've credited the difference to your account.</p>
                        
                        <div style="background: #e0f2fe; border-left: 4px solid #0284c7; padding: 20px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #0c4a6e;">Overpayment Details</h3>
                            <p><strong>Domain:</strong> {domain_name}</p>
                            <p><strong>Overpayment Amount:</strong> ${overpayment_amount:.2f} USD</p>
                            <p><strong>Order ID:</strong> {order_id}</p>
                        </div>
                        
                        <h3 style="color: #1e40af;">What happens next?</h3>
                        <ul style="padding-left: 20px;">
                            <li>Your overpayment has been added to your wallet balance</li>
                            <li>You can use this credit for future domain registrations</li>
                            <li>The balance remains in your account until used</li>
                        </ul>
                    </div>
                    
                    <div style="background: #334155; color: #cbd5e1; padding: 20px; text-align: center; font-size: 12px;">
                        <p>Nomadly - Offshore Hosting Solutions</p>
                    </div>
                </body>
                </html>
                """
                
                text_content = f"""
Overpayment Credit Applied - ${overpayment_amount:.2f}

Great news! You sent more cryptocurrency than needed for your domain registration.

Details:
- Domain: {domain_name}  
- Overpayment: ${overpayment_amount:.2f} USD
- Order ID: {order_id}

Your overpayment has been credited to your wallet balance and can be used for future services.

Access your account via Telegram to view your updated balance.

Nomadly - Offshore Hosting Solutions
                """
                
                results["email"] = self.send_email_notification(
                    user.technical_email, subject, html_content, text_content
                )
            else:
                logger.info(f"User {telegram_id} has no email address for overpayment notification")
                results["email"] = True  # Not an error, just no email to send
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending overpayment notification: {e}")
            return results
    
    async def send_underpayment_notification(self, telegram_id: int, underpayment_amount: float,
                                           domain_name: str, order_id: str, required_amount: float) -> Dict[str, bool]:
        """Send comprehensive underpayment notification via Telegram + Email"""
        results = {"telegram": False, "email": False}
        
        try:
            # Get user details
            db_manager = get_db_manager()
            user = db_manager.get_user(telegram_id)
            
            if not user:
                logger.error(f"User {telegram_id} not found for underpayment notification")
                return results
            
            shortage = required_amount - underpayment_amount
            
            # Prepare Telegram message
            telegram_message = (
                f"💳 *Payment Shortage - Amount Credited to Wallet*\n\n"
                f"We received your payment, but it was less than the required amount.\n\n"
                f"*Payment Details:*\n"
                f"• Domain: `{domain_name}`\n"
                f"• Required: `${required_amount:.2f}` USD\n"
                f"• Received: `${underpayment_amount:.2f}` USD\n"
                f"• Shortage: `${shortage:.2f}` USD\n"
                f"• Order ID: `{order_id}`\n\n"
                f"💰 *Your payment has been credited to your wallet balance!*\n\n"
                f"To complete your domain registration:\n"
                f"• Add `${shortage:.2f}` more to your wallet, OR\n"
                f"• Use existing wallet balance if available\n\n"
                f"Your funds are safe and ready to use!"
            )
            
            # Send Telegram notification
            results["telegram"] = await self.send_telegram_notification(telegram_id, telegram_message)
            
            # Send email notification if user has email
            if user.technical_email:
                subject = f"Payment Credited to Wallet - ${underpayment_amount:.2f} (${shortage:.2f} shortage)"
                
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #ea580c, #f97316); padding: 30px; text-align: center; color: white;">
                        <h1 style="margin: 0; font-size: 24px;">💳 Payment Credited to Wallet</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Nomadly Domain Services</p>
                    </div>
                    
                    <div style="padding: 30px; background: #f8fafc;">
                        <h2 style="color: #ea580c; margin-top: 0;">Payment Received!</h2>
                        <p>We received your cryptocurrency payment, but it was less than the required amount for your domain registration. Don't worry - your payment has been safely credited to your wallet!</p>
                        
                        <div style="background: #fed7aa; border-left: 4px solid #f97316; padding: 20px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #9a3412;">Payment Details</h3>
                            <p><strong>Domain:</strong> {domain_name}</p>
                            <p><strong>Required Amount:</strong> ${required_amount:.2f} USD</p>
                            <p><strong>Amount Received:</strong> ${underpayment_amount:.2f} USD</p>
                            <p><strong>Shortage:</strong> ${shortage:.2f} USD</p>
                            <p><strong>Order ID:</strong> {order_id}</p>
                        </div>
                        
                        <h3 style="color: #ea580c;">Complete Your Domain Registration:</h3>
                        <ul style="padding-left: 20px;">
                            <li>Add ${shortage:.2f} more to your wallet to cover the shortage</li>
                            <li>Use existing wallet balance if you have sufficient funds</li>
                            <li>Your payment is safe and ready to use</li>
                        </ul>
                    </div>
                    
                    <div style="background: #334155; color: #cbd5e1; padding: 20px; text-align: center; font-size: 12px;">
                        <p>Nomadly - Offshore Hosting Solutions</p>
                    </div>
                </body>
                </html>
                """
                
                text_content = f"""
Payment Credited to Wallet - ${underpayment_amount:.2f}

We received your cryptocurrency payment for domain registration, but it was less than the required amount.

Payment Details:
- Domain: {domain_name}
- Required Amount: ${required_amount:.2f} USD
- Amount Received: ${underpayment_amount:.2f} USD
- Shortage: ${shortage:.2f} USD
- Order ID: {order_id}

Your payment has been safely credited to your wallet balance. To complete your domain registration, please add ${shortage:.2f} more to your wallet or use existing balance if available.

Access your account via Telegram to complete the registration.

Nomadly - Offshore Hosting Solutions
                """
                
                results["email"] = self.send_email_notification(
                    user.technical_email, subject, html_content, text_content
                )
            else:
                logger.info(f"User {telegram_id} has no email address for underpayment notification")
                results["email"] = True  # Not an error, just no email to send
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending underpayment notification: {e}")
            return results
    
    async def send_registration_confirmation(self, telegram_id: int, domain_name: str, 
                                           order_id: str, amount_paid: float) -> Dict[str, bool]:
        """Send comprehensive domain registration confirmation via Telegram + Email"""
        results = {"telegram": False, "email": False}
        
        try:
            # Get user details
            db_manager = get_db_manager()
            user = db_manager.get_user(telegram_id)
            
            if not user:
                logger.error(f"User {telegram_id} not found for registration confirmation")
                return results
            
            # Prepare Telegram message
            telegram_message = (
                f"🏴‍☠️ *Domain Registration Successful!*\n\n"
                f"Welcome to the fleet! Your domain is now active and operational.\n\n"
                f"*Registration Details:*\n"
                f"• Domain: `{domain_name}`\n"
                f"• Amount Paid: `${amount_paid:.2f}` USD\n"
                f"• Order ID: `{order_id}`\n"
                f"• Status: ✅ Active and Operational\n\n"
                f"*What's Next?*\n"
                f"• Configure DNS records\n"
                f"• Set up email addresses\n"
                f"• Point domain to your website\n\n"
                f"Your domain is ready to sail the digital seas!"
            )
            
            # Send Telegram notification
            results["telegram"] = await self.send_telegram_notification(telegram_id, telegram_message)
            
            # Send email notification if user has email
            if user.technical_email:
                subject = f"Domain Registration Confirmed - {domain_name}"
                
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #059669, #10b981); padding: 30px; text-align: center; color: white;">
                        <h1 style="margin: 0; font-size: 28px;">🏴‍☠️ Domain Registration Successful!</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Nomadly Offshore Hosting</p>
                    </div>
                    
                    <div style="padding: 30px; background: #f8fafc;">
                        <h2 style="color: #059669; margin-top: 0;">Welcome to the Fleet!</h2>
                        <p>Your domain has been successfully registered and is now active and operational.</p>
                        
                        <div style="background: #ecfdf5; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #047857;">Registration Details</h3>
                            <p><strong>Domain:</strong> {domain_name}</p>
                            <p><strong>Amount Paid:</strong> ${amount_paid:.2f} USD</p>
                            <p><strong>Order ID:</strong> {order_id}</p>
                            <p><strong>Status:</strong> ✅ Active and Operational</p>
                        </div>
                        
                        <h3 style="color: #059669;">What's Next?</h3>
                        <ul style="padding-left: 20px;">
                            <li><strong>DNS Management:</strong> Configure your domain's DNS records</li>
                            <li><strong>Email Setup:</strong> Set up professional email addresses</li>
                            <li><strong>Web Hosting:</strong> Point your domain to your website</li>
                        </ul>
                        
                        <p style="margin-top: 20px;">Your domain is ready to sail the digital seas!</p>
                    </div>
                    
                    <div style="background: #334155; color: #cbd5e1; padding: 20px; text-align: center; font-size: 12px;">
                        <p>Nomadly - Offshore Hosting Solutions</p>
                    </div>
                </body>
                </html>
                """
                
                text_content = f"""
Domain Registration Successful - {domain_name}

Welcome to the fleet! Your domain has been successfully registered and is now active.

Registration Details:
- Domain: {domain_name}
- Amount Paid: ${amount_paid:.2f} USD
- Order ID: {order_id}
- Status: Active and Operational

What's Next?
- DNS Management: Configure your domain's DNS records
- Email Setup: Set up professional email addresses  
- Web Hosting: Point your domain to your website

Access your domain management via Telegram to get started.

Nomadly - Offshore Hosting Solutions
                """
                
                results["email"] = self.send_email_notification(
                    user.technical_email, subject, html_content, text_content
                )
            else:
                logger.info(f"User {telegram_id} has no email address for registration confirmation")
                results["email"] = True  # Not an error, just no email to send
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending registration confirmation: {e}")
            return results

# Global service instance
notification_service = ProductionNotificationService()

async def send_overpayment_notification(telegram_id: int, overpayment_amount: float, domain_name: str, order_id: str):
    """Global function for overpayment notifications"""
    return await notification_service.send_overpayment_notification(
        telegram_id, overpayment_amount, domain_name, order_id
    )

async def send_underpayment_notification(telegram_id: int, underpayment_amount: float, domain_name: str, order_id: str, required_amount: float):
    """Global function for underpayment notifications"""
    return await notification_service.send_underpayment_notification(
        telegram_id, underpayment_amount, domain_name, order_id, required_amount
    )

async def send_registration_confirmation(telegram_id: int, domain_name: str, order_id: str, amount_paid: float):
    """Global function for registration confirmations"""
    return await notification_service.send_registration_confirmation(
        telegram_id, domain_name, order_id, amount_paid
    )

if __name__ == "__main__":
    # Test the production notification system
    async def test_notifications():
        logger.info("🚀 Testing Production Dual Notification System")
        
        # Test overpayment notification with real data
        logger.info("Testing overpayment notification...")
        overpayment_results = await send_overpayment_notification(
            telegram_id=5590563715,
            overpayment_amount=4.41,
            domain_name="thankyoujesusmylord.sbs",
            order_id="f5d79497-3863-4f60-bc9d-e10ee327f423"
        )
        
        # Test underpayment notification
        logger.info("Testing underpayment notification...")
        underpayment_results = await send_underpayment_notification(
            telegram_id=5590563715,
            underpayment_amount=7.50,
            domain_name="example.sbs",
            order_id="test-order-123",
            required_amount=9.87
        )
        
        # Test registration confirmation
        logger.info("Testing registration confirmation...")
        registration_results = await send_registration_confirmation(
            telegram_id=5590563715,
            domain_name="thankyoujesusmylord.sbs",
            order_id="f5d79497-3863-4f60-bc9d-e10ee327f423",
            amount_paid=9.87
        )
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("PRODUCTION NOTIFICATION SYSTEM TEST RESULTS:")
        logger.info(f"🎁 Overpayment:  Telegram: {'✅' if overpayment_results['telegram'] else '❌'} | Email: {'✅' if overpayment_results['email'] else '❌'}")
        logger.info(f"💳 Underpayment: Telegram: {'✅' if underpayment_results['telegram'] else '❌'} | Email: {'✅' if underpayment_results['email'] else '❌'}")
        logger.info(f"🏴‍☠️ Registration: Telegram: {'✅' if registration_results['telegram'] else '❌'} | Email: {'✅' if registration_results['email'] else '❌'}")
        logger.info("="*60)
    
    # Run the test
    asyncio.run(test_notifications())