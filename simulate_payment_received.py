#!/usr/bin/env python3
"""Simulate that a payment was received for testing"""

import json
from datetime import datetime

# Load current sessions
with open('user_sessions.json', 'r') as f:
    sessions = json.load(f)

user_id = '5590563715'
session = sessions.get(user_id, {})

if not session:
    print("❌ No active session found")
    exit(1)

domain = session.get('domain')
order_number = session.get('order_number')
eth_address = session.get('eth_address')

print(f"🔍 Current payment status for order {order_number}:")
print(f"   Domain: {domain}")
print(f"   ETH Address: {eth_address}")
print(f"   Status: Waiting for payment")
print()

# Create a payment confirmation file that the bot can check
payment_confirmation = {
    "order_number": order_number,
    "domain": domain,
    "eth_address": eth_address,
    "user_id": user_id,
    "amount_eth": 0.00270900,
    "amount_usd": 9.87,
    "txid": "0x" + "a" * 64,
    "confirmations": 6,
    "confirmed_at": datetime.utcnow().isoformat(),
    "status": "confirmed"
}

# Save to a file that can be checked
with open('payment_confirmations.json', 'w') as f:
    json.dump({eth_address: payment_confirmation}, f, indent=2)

print("✅ Payment confirmation created!")
print(f"   Transaction ID: {payment_confirmation['txid']}")
print(f"   Amount: {payment_confirmation['amount_eth']} ETH (${payment_confirmation['amount_usd']})")
print(f"   Confirmations: {payment_confirmation['confirmations']}")
print()
print("💡 Next steps:")
print("1. The payment monitor should detect this confirmation")
print("2. You'll receive a Telegram notification")
print("3. Domain registration will be triggered automatically")
print()
print("📋 To check if the bot processes this payment:")
print("   - Watch the Payment Monitor logs")
print("   - Check your Telegram for notifications")
print("   - The payment should be processed within 30 seconds")