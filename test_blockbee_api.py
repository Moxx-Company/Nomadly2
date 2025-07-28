#!/usr/bin/env python3
"""Test BlockBee API endpoints to find the correct one"""

import os
import requests
import json

api_key = os.getenv('BLOCKBEE_API_KEY')
eth_address = "0xE0B4D227C8df941920854b6A5b2C69aD33b9AB3E"

print("🔍 Testing BlockBee API endpoints...")
print(f"API Key: {api_key[:10]}...")
print(f"ETH Address: {eth_address}")
print()

# Test different possible endpoints
endpoints = [
    # Try address-specific endpoints
    f"https://api.blockbee.io/ethereum/address/{eth_address}/",
    f"https://api.blockbee.io/eth/address/{eth_address}/",
    
    # Try with different parameters
    f"https://api.blockbee.io/ethereum/logs/?apikey={api_key}&callback={eth_address}",
    f"https://api.blockbee.io/ethereum/callback/logs/?apikey={api_key}&callback={eth_address}",
    
    # Try the create endpoint to see if it returns info
    f"https://api.blockbee.io/ethereum/create/?apikey={api_key}&callback=test&address={eth_address}",
    
    # Try general info
    f"https://api.blockbee.io/info/?apikey={api_key}",
    f"https://api.blockbee.io/ethereum/?apikey={api_key}",
]

for endpoint in endpoints:
    print(f"Testing: {endpoint[:60]}...")
    try:
        response = requests.get(endpoint, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.text[:100]}...")
        else:
            print(f"  Response: {response.text[:100]}...")
    except Exception as e:
        print(f"  Error: {e}")
    print()

# Check if we need to use the callback system
print("\n📡 Testing callback registration...")
callback_url = "https://nomadly.com/api/v1/payments/callback/test"
create_url = f"https://api.blockbee.io/ethereum/create/"
params = {
    "apikey": api_key,
    "callback": callback_url
}

try:
    response = requests.get(create_url, params=params, timeout=10)
    print(f"Create endpoint status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # If we get an address, maybe we can query it
        if 'address_in' in data:
            test_addr = data['address_in']
            print(f"\n🔍 Got address: {test_addr}")
            print("Maybe we need to use the address from create endpoint to check payments...")
except Exception as e:
    print(f"Error: {e}")

print("\n💡 Conclusion:")
print("- BlockBee API might only track addresses created through their system")
print("- The /info/, /logs/, and /callback/ endpoints seem to be deprecated or changed")
print("- Payment monitoring might need to use webhook callbacks instead of polling")