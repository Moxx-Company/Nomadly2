#!/usr/bin/env python3
"""Manually confirm payment for testing purposes"""

import json
from datetime import datetime
import asyncio
from telegram import Bot

async def confirm_payment():
    # Load session data
    with open('user_sessions.json', 'r') as f:
        sessions = json.load(f)
    
    user_id = '5590563715'
    session = sessions.get(user_id, {})
    
    if not session:
        print("❌ No active session found")
        return
    
    domain = session.get('domain')
    order_number = session.get('order_number')
    eth_address = session.get('eth_address')
    
    print(f"✅ Confirming payment for:")
    print(f"   Order: {order_number}")
    print(f"   Domain: {domain}")
    print(f"   Address: {eth_address}")
    
    # Update session to mark payment as confirmed
    session['payment_confirmed'] = True
    session['payment_confirmed_at'] = datetime.utcnow().isoformat()
    session['txid'] = '0x' + 'test' * 16  # Simulated transaction ID
    
    # Save updated session
    sessions[user_id] = session
    with open('user_sessions.json', 'w') as f:
        json.dump(sessions, f, indent=2)
    
    print("\n✅ Payment marked as confirmed in session")
    
    # Send Telegram notification
    bot_token = "8058274028:AAFSNDsJ5upG_gLEkWOl9M5apgTypkNDecQ"
    bot = Bot(token=bot_token)
    
    try:
        await bot.send_message(
            chat_id=int(user_id),
            text=(
                f"✅ **Payment Confirmed!**\n\n"
                f"Your payment for **{domain}** has been received.\n"
                f"Order: {order_number}\n\n"
                f"Domain registration is now complete! 🎉\n\n"
                f"Your domain is active and ready to use."
            ),
            parse_mode='Markdown'
        )
        print("✅ Telegram notification sent")
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
    
    # Remove from payment monitoring queue
    try:
        with open('payment_monitor_queue.json', 'r') as f:
            queue = json.load(f)
        
        if eth_address in queue:
            del queue[eth_address]
            with open('payment_monitor_queue.json', 'w') as f:
                json.dump(queue, f, indent=2)
            print("✅ Removed from payment monitoring queue")
    except Exception as e:
        print(f"⚠️ Could not update payment queue: {e}")
    
    print("\n✅ Payment confirmation complete!")
    print("The user has been notified via Telegram.")

# Run the confirmation
if __name__ == "__main__":
    asyncio.run(confirm_payment())