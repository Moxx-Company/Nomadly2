#!/usr/bin/env python3
"""
Simulate Real User Domain Registration for @onarrival1
Creates actual payment address and tests notification system
"""

import random
import string
import os
from datetime import datetime

def generate_random_sbs_domain():
    """Generate a random .sbs domain"""
    # Random 8-12 character domain name
    length = random.randint(8, 12)
    domain_name = ''.join(random.choices(string.ascii_lowercase, k=length))
    return f"{domain_name}.sbs"

def simulate_domain_registration():
    """Simulate complete domain registration flow"""
    
    print("🎯 SIMULATING REAL USER REGISTRATION TEST")
    print("=" * 50)
    
    # Generate test domain
    test_domain = generate_random_sbs_domain()
    print(f"📋 Test Domain: {test_domain}")
    print(f"👤 Test User: @onarrival1 (ID: 5590563715)")
    
    # Create order and payment
    try:
        from payment_service import PaymentService
        payment_service = PaymentService()
        
        # Create order for domain registration
        order_id = payment_service.create_order(
            telegram_id=5590563715,
            service_type="domain_registration", 
            amount=2.99,
            domain_name=test_domain,
            contact_email="onarrival21@gmail.com"
        )
        
        print(f"📝 Order Created: {order_id}")
        
        # Create ETH payment
        payment_data = payment_service.create_crypto_payment(
            order_id=order_id,
            crypto_type="eth",
            amount=2.99,
            service_type="domain_registration"
        )
        
        if payment_data:
            print(f"💰 ETH Payment Address: {payment_data['address']}")
            print(f"💎 Amount Required: {payment_data['amount_crypto']} ETH")
            print(f"🔗 Callback URL: {payment_data['callback_url']}")
            
            print(f"\n🎯 PAYMENT INSTRUCTIONS FOR USER:")
            print(f"   Domain: {test_domain}")
            print(f"   Send: {payment_data['amount_crypto']} ETH")
            print(f"   To: {payment_data['address']}")
            print(f"   Order: {order_id}")
            
            return {
                'domain': test_domain,
                'order_id': order_id,
                'payment_address': payment_data['address'],
                'amount_eth': payment_data['amount_crypto'],
                'callback_url': payment_data['callback_url']
            }
        else:
            print("❌ Failed to create payment")
            return None
            
    except Exception as e:
        print(f"❌ Registration simulation error: {e}")
        return None

if __name__ == "__main__":
    result = simulate_domain_registration()
    if result:
        print(f"\n✅ SIMULATION READY")
        print(f"🔄 Send payment and I'll analyze the notification flow")
    else:
        print(f"\n❌ SIMULATION FAILED")
        print(f"💡 Check payment service configuration")