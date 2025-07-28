#!/usr/bin/env python3
"""
Debug script to test payment status check issue
"""

import asyncio
import json
from types import SimpleNamespace

# Create a fake query object to debug the payment status check
async def test_payment_status_check():
    print("Testing payment status check...")
    
    # Load user sessions to understand the data structure
    try:
        with open('user_sessions.json', 'r') as f:
            sessions = json.load(f)
            print(f"Sessions loaded: {json.dumps(sessions, indent=2)}")
    except:
        sessions = {}
    
    # Import the bot
    from nomadly3_clean_bot import NomadlyCleanBot
    
    # Create bot instance
    bot = NomadlyCleanBot()
    
    # Create fake query object
    query = SimpleNamespace()
    query.from_user = SimpleNamespace()
    query.from_user.id = 789499746  # Test user
    query.data = "check_payment_status_btc_wewillwin_sbs"
    query.answer = lambda msg="": print(f"Query answered: {msg}")
    query.edit_message_text = lambda text, **kwargs: print(f"Message edited: {text[:100]}...")
    query.message = SimpleNamespace()
    query.message.reply_text = lambda text, **kwargs: print(f"Reply sent: {text[:100]}...")
    
    # Test the callback parsing
    data = query.data
    if data.startswith("check_payment_status_"):
        parts = data.split("_", 4)
        if len(parts) >= 5:
            crypto_type = parts[3]
            domain = "_".join(parts[4:])
            print(f"Parsed: crypto_type={crypto_type}, domain={domain}")
            
            # Try to call the handler directly
            try:
                await bot.handle_payment_status_check(query, crypto_type, domain)
                print("✅ Payment status check completed successfully")
            except Exception as e:
                print(f"❌ Error in payment status check: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Invalid callback data format: {data}")
    
if __name__ == "__main__":
    asyncio.run(test_payment_status_check())