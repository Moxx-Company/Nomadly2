#!/usr/bin/env python3
"""Trace payment for the latest order"""

import os
import json
from apis.blockbee import BlockBeeAPI

# Get the payment details from user sessions
with open('user_sessions.json', 'r') as f:
    sessions = json.load(f)

# Get the latest order details
user_id = '5590563715'
session = sessions.get(user_id, {})

eth_address = session.get('eth_address')
order_number = session.get('order_number')
expected_amount = session.get('payment_amount_usd', 0)

print(f"🔍 Tracing payment for order: {order_number}")
print(f"💳 ETH Address: {eth_address}")
print(f"💰 Expected amount: ${expected_amount}")
print()

# Initialize BlockBee API
api_key = os.getenv('BLOCKBEE_API_KEY')
if not api_key:
    print("❌ BLOCKBEE_API_KEY not set")
    exit(1)

blockbee = BlockBeeAPI(api_key)

# Check payment info
print("📡 Querying BlockBee API for payment status...")
payment_info = blockbee.get_payment_info('eth', eth_address)

if payment_info:
    print("\n✅ Payment Info Retrieved:")
    print(json.dumps(payment_info, indent=2))
    
    # Check if payment received
    value_received = payment_info.get('value_received', 0)
    if value_received > 0:
        print(f"\n💰 PAYMENT DETECTED!")
        print(f"Amount received: {value_received} ETH")
    else:
        print(f"\n⏳ No payment received yet")
else:
    print("\n❌ Could not retrieve payment info from BlockBee")
    print("This may be because:")
    print("- The address was just created and needs time to propagate")
    print("- No payment has been sent yet")
    print("- The address is in test mode")