#!/usr/bin/env python3
"""
Create Overpayment Notification Fix for Nomadly2
===============================================
Ensures overpayment notifications are sent to users via both Telegram and email
"""

import sys
sys.path.append('.')

import logging
import asyncio
from database import get_db_manager
from utils.brevo_email_service import BrevoEmailService

logger = logging.getLogger(__name__)

async def send_overpayment_notification(telegram_id: int, overpayment_amount: float, domain_name: str, order_id: str):
    """Send overpayment notification to user via Telegram and email"""
    try:
        # Get user details
        db_manager = get_db_manager()
        user = db_manager.get_user(telegram_id)
        
        if not user:
            logger.error(f"User {telegram_id} not found for overpayment notification")
            return False
        
        # Create notification message
        telegram_message = (
            f"🎁 **Overpayment Credit Applied**\n\n"
            f"Great news! You sent more cryptocurrency than needed for your domain registration.\n\n"
            f"**Details:**\n"
            f"• Domain: `{domain_name}`\n"
            f"• Overpayment: `${overpayment_amount:.2f}` USD\n"
            f"• Order ID: `{order_id}`\n\n"
            f"💰 **Your overpayment has been credited to your wallet balance!**\n\n"
            f"You can use this credit for:\n"
            f"• Future domain registrations\n"
            f"• Additional services\n"
            f"• Or keep it as account balance\n\n"
            f"Check your wallet to see the updated balance."
        )
        
        # Send Telegram notification
        from nomadly2_bot import bot_instance
        if bot_instance:
            try:
                await bot_instance.application.bot.send_message(
                    chat_id=telegram_id,
                    text=telegram_message,
                    parse_mode="Markdown"
                )
                logger.info(f"Overpayment notification sent via Telegram to user {telegram_id}")
            except Exception as e:
                logger.error(f"Failed to send Telegram overpayment notification: {e}")
        
        # Send email notification if user has email
        if user.technical_email:
            try:
                brevo_service = BrevoEmailService()
                
                email_subject = f"Overpayment Credit Applied - ${overpayment_amount:.2f}"
                
                email_html = f"""
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
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <p style="color: #64748b;">Access your account via Telegram to view your updated balance</p>
                        </div>
                    </div>
                    
                    <div style="background: #334155; color: #cbd5e1; padding: 20px; text-align: center; font-size: 12px;">
                        <p>Nomadly - Offshore Hosting Solutions | Discretion • Independence • Resilience</p>
                    </div>
                </body>
                </html>
                """
                
                email_text = f"""
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
                
                success = brevo_service.send_email_api(
                    to_email=user.technical_email,
                    subject=email_subject,
                    html_content=email_html,
                    text_content=email_text
                )
                
                if success:
                    logger.info(f"Overpayment email notification sent to {user.technical_email}")
                else:
                    logger.error(f"Failed to send overpayment email to {user.technical_email}")
                    
            except Exception as e:
                logger.error(f"Error sending overpayment email notification: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending overpayment notification: {e}")
        return False

if __name__ == "__main__":
    # Test overpayment notification for recent order
    asyncio.run(send_overpayment_notification(
        telegram_id=5590563715,
        overpayment_amount=4.41,
        domain_name="thankyoujesusmylord.sbs", 
        order_id="f5d79497-3863-4f60-bc9d-e10ee327f423"
    ))