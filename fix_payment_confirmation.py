#!/usr/bin/env python3
"""
Fix payment confirmation for nomadly30.sbs
Manually complete the domain registration for the successful payment
"""

import asyncio
import json
from payment_service import PaymentService

async def fix_payment_confirmation():
    """Fix the payment confirmation for order 55c162cf-fc38-47d3-8e5e-7f3b7018db61"""
    
    order_id = "55c162cf-fc38-47d3-8e5e-7f3b7018db61"
    
    print(f"🔧 Fixing payment confirmation for order: {order_id}")
    print("💰 Payment details: 0.0037 ETH ($2.99) - CONFIRMED")
    print("🌐 Domain: nomadly30.sbs")
    
    # Create webhook data for manual processing
    webhook_data = {
        'uuid': '6867b1f7-5960-4035-879e-3d0ddf5018d2',
        'address_in': '0x95bfDd53D4546Ba38e954c7F3782dEEAaD644b1A',
        'address_out': '0x9a7221b5e32d5f99e8da95585835442e29afb38f',
        'confirmations': '3',
        'txid_in': '0xdec2f9f7111acfc5d75f8e29dbf4cf969e56726a41b85d8fab560407682ef2a1',
        'txid_out': '0x1d3570e01d1e798f25d6d350d04a99bcb30403c8e96b53c46c76a1bdd4328c98',
        'value': '3700000000000000',
        'value_coin': '0.0037',
        'coin': 'eth',
        'result': 'sent',
        'pending': '0'
    }
    
    try:
        payment_service = PaymentService()
        
        print("🔄 Attempting domain registration completion...")
        success = await payment_service.complete_domain_registration(order_id, webhook_data)
        
        if success:
            print("✅ Domain registration completed successfully!")
            print("📧 User should receive confirmation notification")
            print("🎉 nomadly30.sbs is now registered and configured")
        else:
            print("❌ Domain registration completion failed")
            print("📝 Check logs for detailed error information")
            
    except Exception as e:
        print(f"❌ Error during manual fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_payment_confirmation())