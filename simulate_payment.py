#!/usr/bin/env python3
"""Simulate a blockchain payment for testing"""

import os
import sys
from apis.blockbee import BlockBeeAPI

# Get the payment address from user_sessions.json
import json
with open('user_sessions.json', 'r') as f:
    sessions = json.load(f)
    
# Find the ETH address
eth_address = None
for user_id, session in sessions.items():
    if 'eth_address' in session:
        eth_address = session['eth_address']
        print(f"Found ETH address: {eth_address}")
        break

if not eth_address:
    print("No ETH address found in sessions")
    sys.exit(1)

# Initialize BlockBee API
api_key = os.getenv('BLOCKBEE_API_KEY')
if not api_key:
    print("BLOCKBEE_API_KEY not set")
    sys.exit(1)

blockbee = BlockBeeAPI(api_key)

# For testing, we'll just print what would happen
print(f"\nTo test payment detection:")
print(f"1. Send ETH to address: {eth_address}")
print(f"2. The payment monitor will check every 30 seconds")
print(f"3. Once detected, you'll receive a Telegram notification")
print(f"\nPayment monitor is actively checking this address...")