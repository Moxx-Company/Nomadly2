#!/usr/bin/env python3
"""
Manual Webhook Test
Simulate BlockBee webhook call to test registration flow
"""

import sys
import requests
import json
sys.path.insert(0, '/home/runner/workspace')

def test_webhook():
    """Test webhook manually with simulated payment confirmation"""
    
    print("🧪 TESTING WEBHOOK MANUALLY")
    print("=" * 40)
    
    # Test webhook endpoint - correct BlockBee format
    order_id = "2884d40b-4b2e-40a5-927b-d41f43400c19"
    webhook_url = f"http://localhost:8000/webhook/blockbee/{order_id}"
    
    # Simulate BlockBee payment confirmation
    test_data = {
        "order_id": "2884d40b-4b2e-40a5-927b-d41f43400c19",
        "txid_in": "0x1234567890abcdef1234567890abcdef12345678",
        "value_coin": "0.0037",
        "value_forwarded_coin": "0.0037",
        "coin": "eth",
        "confirmations": "1",
        "address_in": "0x47F2a1CC87c719C3cA608f638e8d354cC2F5b2C7",
        "address_out": "0x7fcdf5eCf86ab2d70216d1F17A7E91FB4BbeDb94"
    }
    
    print(f"Webhook URL: {webhook_url}")
    print(f"Test Data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Send test webhook - BlockBee sends as GET with query params
        response = requests.get(
            webhook_url,
            params=test_data,
            timeout=30
        )
        
        print(f"\n📡 Webhook Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Webhook processed successfully")
            
            # Check order status after webhook
            print(f"\n🔍 Checking order status after webhook...")
            from database import get_db_manager
            db = get_db_manager()
            order = db.get_order(test_data["order_id"])
            
            if order:
                print(f"Order Status: {order.payment_status}")
                if hasattr(order, 'payment_txid'):
                    print(f"Transaction ID: {order.payment_txid}")
            
            return True
        else:
            print(f"❌ Webhook failed")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False

if __name__ == "__main__":
    success = test_webhook()
    if success:
        print(f"\n🎉 WEBHOOK TEST SUCCESSFUL")
    else:
        print(f"\n💥 WEBHOOK TEST FAILED")