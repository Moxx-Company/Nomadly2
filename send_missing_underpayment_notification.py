#!/usr/bin/env python3
"""
Send missing underpayment notification to user 5590563715 using CORRECT bot token from .env
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_notification():
    """Send the missing underpayment notification with CORRECT bot token"""
    try:
        # Load environment variables from .env file
        load_dotenv()
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
            return False
            
        print(f"🤖 Using bot token: {bot_token[:20]}...")
        
        bot = Bot(token=bot_token)
        
        message = (
            f"💳 *Wallet Deposit - Underpayment Credited*\n\n"
            f"🎯 **Expected:** $20.00 USD\n"
            f"💰 **You Sent:** $15.04 USD\n"
            f"⚠️ **Shortage:** $4.96 USD\n\n"
            f"✅ **Your $15.04 USD has been credited to your wallet!**\n\n"
            f"🔗 **Order ID:** `8b972942`\n"
            f"💎 **Crypto:** 0.00404932 ETH\n"
            f"💳 **New Balance:** $32.13 USD\n\n"
            f"💡 *Add $4.96 more to reach your intended deposit amount.*\n\n"
            f"🏴‍☠️ *No payment is ever lost - all funds are credited!*"
        )
        
        await bot.send_message(
            chat_id=5590563715,
            text=message,
            parse_mode='Markdown'
        )
        
        print("✅ Underpayment notification sent successfully to CORRECT bot")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(send_notification())