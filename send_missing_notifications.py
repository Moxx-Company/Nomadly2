#!/usr/bin/env python3
"""
Send missing overpayment notification for completed order ffc3fe5f
"""

import asyncio
import logging
from payment_service import PaymentService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_missing_overpayment_notification():
    """Send the missing overpayment notification for your completed order"""
    try:
        payment_service = PaymentService()
        
        # Send the missing overpayment notification for order ffc3fe5f
        await payment_service._send_overpayment_notification(
            telegram_id=5590563715,
            overpayment_amount=9.74,  # From wallet_transactions table
            new_balance=9.74,         # Current balance 
            order_id="ffc3fe5f-61e7-4dfa-8130-7b935808ef01"
        )
        
        logger.info("✅ Missing overpayment notification sent successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to send missing notification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(send_missing_overpayment_notification())