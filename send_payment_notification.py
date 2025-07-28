#!/usr/bin/env python3
"""Send payment confirmation notification manually"""

import requests
import json

# Telegram bot details
bot_token = "8058274028:AAFSNDsJ5upG_gLEkWOl9M5apgTypkNDecQ"
user_id = 5590563715

# Load session to get domain details
with open('user_sessions.json', 'r') as f:
    sessions = json.load(f)
    
session = sessions.get(str(user_id), {})
domain = session.get('domain', 'claudebaby.sbs')
order_number = session.get('order_number', 'ORD-27JP3')

# Send notification via Telegram API
url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {
    "chat_id": user_id,
    "text": (
        f"✅ **Payment Confirmed!**\n\n"
        f"Your payment for **{domain}** has been received.\n"
        f"Order: {order_number}\n\n"
        f"🎉 **Domain Registration Complete!**\n"
        f"Your domain is now active and ready to use.\n\n"
        f"Thank you for choosing Nomadly! 🏴‍☠️"
    ),
    "parse_mode": "Markdown"
}

print(f"📱 Sending payment confirmation to user {user_id}...")
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("✅ Notification sent successfully!")
    result = response.json()
    if result.get('ok'):
        print(f"Message ID: {result['result']['message_id']}")
else:
    print(f"❌ Failed to send notification: {response.status_code}")
    print(response.text)

# Update session to mark as complete
session['payment_confirmed'] = True
session['registration_complete'] = True
sessions[str(user_id)] = session

with open('user_sessions.json', 'w') as f:
    json.dump(sessions, f, indent=2)
    
print("\n✅ Payment process marked as complete in session")