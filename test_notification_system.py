#!/usr/bin/env python3
"""
Test notification system to identify why users aren't receiving notifications
"""

import asyncio
import logging
import os
from payment_service import PaymentService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_overpayment_notification():
    """Test overpayment notification system"""
    try:
        # Check if BOT_TOKEN is available
        bot_token = os.getenv('BOT_TOKEN')  # As shown in available secrets
        if bot_token:
            logger.info("✅ BOT_TOKEN is available")
        else:
            logger.error("❌ BOT_TOKEN not found")
        
        payment_service = PaymentService()
        
        # Test sending overpayment notification directly
        await payment_service._send_overpayment_notification(
            telegram_id=5590563715,
            overpayment_amount=9.74,
            new_balance=9.74,
            order_id="ffc3fe5f-61e7-4dfa-8130-7b935808ef01"
        )
        
        logger.info("✅ Overpayment notification test completed")
        
    except Exception as e:
        logger.error(f"❌ Notification test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_telegram_bot_direct():
    """Test direct Telegram bot communication"""
    try:
        from telegram import Bot
        
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("❌ BOT_TOKEN not available for direct test")
            return
        
        bot = Bot(token=bot_token)
        
        message = (
            "🧪 **Notification System Test**\n\n"
            "This is a test message to verify notification delivery.\n\n"
            "✅ If you received this, notifications are working!"
        )
        
        await bot.send_message(
            chat_id=5590563715,
            text=message,
            parse_mode='Markdown'
        )
        
        logger.info("✅ Direct Telegram test message sent")
        
    except Exception as e:
        logger.error(f"❌ Direct Telegram test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_overpayment_notification())
    asyncio.run(test_telegram_bot_direct())