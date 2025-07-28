#!/usr/bin/env python3
"""Comprehensive payment trace for the latest order"""

import os
import json
import requests
from datetime import datetime

# Get the payment details from user sessions
with open('user_sessions.json', 'r') as f:
    sessions = json.load(f)

# Get the latest order details
user_id = '5590563715'
session = sessions.get(user_id, {})

eth_address = session.get('eth_address')
order_number = session.get('order_number')
expected_amount = session.get('payment_amount_usd', 0)
payment_time = session.get('payment_generated_time', 0)

print(f"🔍 Comprehensive Payment Trace for Order: {order_number}")
print(f"💳 ETH Address: {eth_address}")
print(f"💰 Expected amount: ${expected_amount}")
print(f"🕐 Payment generated: {datetime.fromtimestamp(payment_time).strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Check the payment monitor queue
print("📋 Checking payment monitor queue...")
with open('payment_monitor_queue.json', 'r') as f:
    queue = json.load(f)
    if eth_address in queue:
        print(f"✅ Address found in monitor queue")
        print(f"   Details: {json.dumps(queue[eth_address], indent=2)}")
    else:
        print(f"❌ Address NOT in monitor queue")

print()

# Try direct BlockBee API call
api_key = os.getenv('BLOCKBEE_API_KEY')
if api_key:
    print("📡 Direct BlockBee API Test...")
    
    # Try the info endpoint
    info_url = f"https://api.blockbee.io/ethereum/info/"
    params = {"apikey": api_key, "address": eth_address}
    
    print(f"   URL: {info_url}")
    print(f"   Params: {params}")
    
    try:
        response = requests.get(info_url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Try the logs endpoint (alternative)
    logs_url = f"https://api.blockbee.io/ethereum/logs/"
    params = {"apikey": api_key, "address": eth_address}
    
    print("📡 Trying logs endpoint...")
    print(f"   URL: {logs_url}")
    
    try:
        response = requests.get(logs_url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Try callback endpoint to see status
    callback_url = f"https://api.blockbee.io/ethereum/callback/"
    params = {"apikey": api_key, "address": eth_address}
    
    print("📡 Trying callback endpoint...")
    print(f"   URL: {callback_url}")
    
    try:
        response = requests.get(callback_url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")

print()
print("💡 Payment Monitoring Status:")
print("- The payment monitor is checking this address every 30 seconds")
print("- When payment is detected, you'll receive a Telegram notification")
print("- The domain will be automatically registered upon confirmation")
print()
print("🔍 If payment was sent:")
print("- It may take 1-5 minutes for blockchain confirmation")
print("- Make sure you sent at least 0.00270900 ETH")
print("- The payment monitor will continue checking until detected")