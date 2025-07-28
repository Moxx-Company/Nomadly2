#!/usr/bin/env python3
"""Test BlockBee logs endpoint using callback URL"""

import os
import json
import requests

# Get the payment details from user sessions
with open('user_sessions.json', 'r') as f:
    sessions = json.load(f)

user_id = '5590563715'
session = sessions.get(user_id, {})

eth_address = session.get('eth_address')
order_number = session.get('order_number')
callback_url = session.get('blockbee_callback_url')
expected_amount = session.get('payment_amount_usd', 0)

print(f"🔍 Testing BlockBee Logs for Order: {order_number}")
print(f"💳 ETH Address: {eth_address}")
print(f"🔗 Callback URL: {callback_url}")
print(f"💰 Expected amount: ${expected_amount}")
print()

api_key = os.getenv('BLOCKBEE_API_KEY')
if not api_key:
    print("❌ BLOCKBEE_API_KEY not set")
    exit(1)

# Test the logs endpoint with callback URL
print("📡 Testing logs endpoint with callback URL...")
logs_url = "https://api.blockbee.io/ethereum/logs/"
params = {
    "apikey": api_key,
    "callback": callback_url
}

print(f"URL: {logs_url}")
print(f"Params: {json.dumps(params, indent=2)}")

try:
    response = requests.get(logs_url, params=params, timeout=10)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Check if there are any callbacks (payments)
        callbacks = data.get('callbacks', [])
        if callbacks:
            print(f"\n✅ Found {len(callbacks)} payment(s)!")
            for i, callback in enumerate(callbacks):
                print(f"\nPayment {i+1}:")
                print(f"  Transaction ID: {callback.get('txid_in')}")
                print(f"  Amount: {callback.get('value_coin')} ETH")
                print(f"  Confirmations: {callback.get('confirmations')}")
                print(f"  Status: {callback.get('result')}")
        else:
            print("\n⏳ No payments received yet")
            print("The address is being monitored and payments will appear here when received")
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n💡 Notes:")
print("- BlockBee uses a callback/webhook system for real-time notifications")
print("- The logs endpoint shows historical payment data")
print("- Payments typically appear within 1-5 minutes of blockchain confirmation")