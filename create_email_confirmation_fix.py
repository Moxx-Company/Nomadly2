#!/usr/bin/env python3
"""
Create email notification system for domain registration confirmations
"""

import asyncio
import logging
from handlers.email_handlers import EmailHandlers
from database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_domain_confirmation_email():
    """Create and send domain registration confirmation email"""
    try:
        db = DatabaseManager()
        email_handlers = EmailHandlers(db)
        
        # Send domain registration confirmation for thanksjesus.sbs
        order_details = {
            "domain_name": "thanksjesus.sbs",
            "amount_usd": 9.87,
            "order_id": "ffc3fe5f-61e7-4dfa-8130-7b935808ef01",
            "payment_status": "completed",
            "service_type": "domain_registration"
        }
        
        success = email_handlers.send_payment_confirmation_with_invoice(
            telegram_id=5590563715,
            order_details=order_details,
            user_email="onarrival21@gmail.com",
            language="en"
        )
        
        if success:
            logger.info("✅ Domain registration confirmation email sent successfully!")
        else:
            logger.error("❌ Failed to send domain registration confirmation email")
            
    except Exception as e:
        logger.error(f"❌ Email confirmation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_domain_confirmation_email())