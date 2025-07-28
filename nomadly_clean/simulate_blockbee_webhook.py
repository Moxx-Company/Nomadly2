#!/usr/bin/env python3
"""Simulate a BlockBee webhook to test the payment processing"""

import requests
import json

# Simulate BlockBee webhook data
webhook_data = {
    "value": 26560000,  # Value in satoshis (0.00265600 ETH = 2656000 gwei)
    "coin": "eth",
    "address_in": "0x2AEa92a4c83957FBa2c720378a0705DBEBf883F5",
    "confirmations": 12,
    "txid_in": "0x1234567890abcdef",  # Simulated transaction ID
    "value_forwarded": 26560000,
    "uuid": "blockbee-payment-uuid"
}

# Send webhook to local server
order_id = "c63030b2-e5c4-46c0-a241-5cfc37de7fbe"
url = f"http://localhost:5000/webhook/blockbee/{order_id}"

print(f"🚀 Simulating BlockBee webhook for order {order_id}")
print(f"📍 Sending to: {url}")
print(f"💰 Payment details:")
print(f"   - Amount: 0.00265600 ETH")
print(f"   - Address: {webhook_data['address_in']}")
print(f"   - Confirmations: {webhook_data['confirmations']}")
print()

try:
    response = requests.post(url, json=webhook_data)
    print(f"✅ Response Status: {response.status_code}")
    print(f"📄 Response: {response.text}")
    
    if response.status_code == 200:
        print("\n🎉 Payment webhook processed successfully!")
        print("Check your Telegram bot for domain registration confirmation.")
    else:
        print("\n⚠️ Webhook processing failed")
        
except Exception as e:
    print(f"❌ Error: {e}")