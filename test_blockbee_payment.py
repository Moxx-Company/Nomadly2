#!/usr/bin/env python3
"""
Test BlockBee payment address creation to diagnose the transaction failure
"""

import os
import sys
import requests
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_blockbee_payment_creation():
    """Test BlockBee payment address creation end-to-end"""
    print("🔍 Testing BlockBee Payment Address Creation...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('BLOCKBEE_API_KEY')
    if not api_key:
        print("❌ BLOCKBEE_API_KEY not found in environment")
        return False
        
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-10:]} (length: {len(api_key)})")
    
    # Test basic connectivity
    print("\n📡 Testing Basic API Connectivity...")
    try:
        response = requests.get("https://api.blockbee.io/eth/info/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ ETH Info: {info.get('ticker', 'unknown')} - {info.get('coin', 'unknown')}")
        else:
            print(f"   ❌ Failed to get ETH info: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Connectivity error: {e}")
        return False
    
    # Test payment address creation
    print("\n💳 Testing Payment Address Creation...")
    
    callback_url = "https://nomadly2-onarrival.replit.app/webhook/blockbee/test"
    amount = 9.87  # Test amount
    
    params = {
        "apikey": api_key,
        "callback": callback_url,
        "value": str(amount)
    }
    
    print(f"   URL: https://api.blockbee.io/eth/create/")
    print(f"   Params: {json.dumps(params, indent=6)}")
    
    try:
        response = requests.get(
            "https://api.blockbee.io/eth/create/", 
            params=params, 
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Payment Address Creation Result:")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Address: {result.get('address_in', 'not provided')}")
            print(f"   QR Code: {result.get('qr_code', 'not provided')}")
            
            if result.get('status') == 'success' and result.get('address_in'):
                print(f"\n🎉 SUCCESS: Payment address created successfully!")
                return True
            else:
                print(f"\n❌ FAILED: Invalid response format or missing address")
                return False
        else:
            print(f"\n❌ FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        return False

def test_payment_integration_in_bot():
    """Test the payment integration from the bot's perspective"""
    print("\n🤖 Testing Bot Payment Integration...")
    print("=" * 50)
    
    try:
        # Import the BlockBee API class from the bot
        sys.path.append('apis')
        from blockbee import BlockBeeAPI
        
        api_key = os.getenv('BLOCKBEE_API_KEY')
        blockbee = BlockBeeAPI(api_key)
        
        callback_url = "https://nomadly2-onarrival.replit.app/webhook/blockbee/test-123"
        amount = 9.87
        
        print(f"   Testing with amount: ${amount}")
        print(f"   Callback URL: {callback_url}")
        
        result = blockbee.create_payment_address("eth", callback_url, amount)
        
        print(f"   Result: {json.dumps(result, indent=6)}")
        
        if result.get('status') == 'success':
            print(f"✅ Bot integration working - address: {result.get('address_in', 'missing')}")
            return True
        else:
            print(f"❌ Bot integration failed - {result.get('message', 'unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Bot integration error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BlockBee Payment Address Creation Diagnostic")
    print("=" * 60)
    
    success1 = test_blockbee_payment_creation()
    success2 = test_payment_integration_in_bot()
    
    print("\n📊 DIAGNOSTIC SUMMARY:")
    print("=" * 30)
    print(f"Direct API Test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Bot Integration: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed - payment system should be working!")
    else:
        print("\n⚠️ Issues detected - payment address generation may be failing")