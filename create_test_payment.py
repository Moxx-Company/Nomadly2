#!/usr/bin/env python3
"""
Create Test Payment for @onarrival1 Domain Registration
Direct API call to create real payment address
"""

import os
import sys
import uuid
import random
import string

# Add project root to path
sys.path.insert(0, '/home/runner/workspace')

def generate_random_domain():
    """Generate random .sbs domain"""
    name = ''.join(random.choices(string.ascii_lowercase, k=10))
    return f"{name}.sbs"

def create_test_payment():
    """Create real payment using database and BlockBee API"""
    
    print("🎯 CREATING TEST PAYMENT FOR @onarrival1")
    print("=" * 45)
    
    # Generate test domain
    test_domain = generate_random_domain()
    print(f"📋 Test Domain: {test_domain}")
    
    try:
        # Initialize database
        from database import get_db_manager
        db_manager = get_db_manager()
        
        # Create order in database
        order_id = str(uuid.uuid4())
        
        # Insert order directly
        order_data = {
            'order_id': order_id,
            'telegram_id': 5590563715,  # @onarrival1 user ID
            'service_type': 'domain_registration',
            'amount_usd': 2.99,
            'status': 'pending_payment',
            'domain_name': test_domain,
            'contact_email': 'onarrival21@gmail.com',
            'nameserver_choice': 'cloudflare'
        }
        
        # Create order using database manager
        order = db_manager.create_order(
            telegram_id=5590563715,
            service_type="domain_registration",
            service_details={
                "domain_name": test_domain,
                "contact_email": "onarrival21@gmail.com",
                "nameserver_choice": "cloudflare"
            },
            amount=2.99,
            payment_method="crypto"
        )
        
        if not order:
            print("❌ Failed to create order")
            return None
            
        order_id = order.order_id
        print(f"✅ Order created: {order_id}")
        
        # Create BlockBee payment
        import requests
        
        api_key = os.getenv('BLOCKBEE_API_KEY')
        if not api_key:
            print("❌ Missing BLOCKBEE_API_KEY")
            return None
            
        # Build callback URL
        repl_domain = os.getenv('REPLIT_DOMAINS', '').split(',')[0] if os.getenv('REPLIT_DOMAINS') else 'localhost'
        callback_url = f"https://{repl_domain}/webhook/blockbee/{order_id}"
        
        # Call BlockBee API
        blockbee_url = f"https://api.blockbee.io/eth/create/"
        params = {
            'callback': callback_url,
            'apikey': api_key
        }
        
        response = requests.get(blockbee_url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('status') == 'success':
                payment_address = result.get('address_in')
                
                print(f"💰 ETH Payment Address: {payment_address}")
                print(f"💎 Amount Required: ~0.00115 ETH ($2.99)")
                print(f"🔗 Callback URL: {callback_url}")
                
                print(f"\n🎯 SEND PAYMENT TO TEST:")
                print(f"   Domain: {test_domain}")
                print(f"   Address: {payment_address}")
                print(f"   Amount: ~0.00115 ETH")
                print(f"   Order: {order_id}")
                
                return {
                    'domain': test_domain,
                    'order_id': order_id,
                    'payment_address': payment_address,
                    'amount_eth': '~0.00115',
                    'user_id': 5590563715
                }
            else:
                print(f"❌ BlockBee error: {result}")
                return None
        else:
            print(f"❌ BlockBee API failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Payment creation error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = create_test_payment()
    if result:
        print(f"\n✅ TEST PAYMENT READY")
        print(f"🔄 Send ETH and I'll monitor webhook notifications")
    else:
        print(f"\n❌ PAYMENT CREATION FAILED")