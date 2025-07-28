#!/usr/bin/env python3
"""
Test Fixed OpenProvider Registration
Create a test payment to verify the registration fix works
"""

import sys
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def test_fixed_registration():
    """Test the fixed OpenProvider registration"""
    
    print("🧪 TESTING FIXED OPENPROVIDER REGISTRATION")
    print("=" * 50)
    
    try:
        from payment_service import PaymentService
        from database import get_db_manager
        
        # Get existing order details
        db_manager = get_db_manager()
        order = db_manager.get_order("54e8307f-758f-4133-9a86-ec3e3788ec06")
        
        if not order:
            print("❌ Test order not found")
            return False
            
        print(f"✅ Found test order: {order.order_id}")
        print(f"📋 Domain: ehobalpbwg.sbs")
        print(f"👤 User: {order.telegram_id}")
        
        # Create payment data for testing
        payment_data = {
            'value_coin': '0.0037',
            'txid_in': '0x4716323e15bfd4e836b4ce0537fff8a52ddebc022cbd5ed5da391e5bf23a0e91',
            'confirmations': '2'
        }
        
        print(f"\n🔧 TESTING FIXED REGISTRATION WITH CORRECTED API FORMAT")
        print(f"   Fixed: domain name/TLD separation")
        print(f"   Fixed: contact handle vs TLD confusion")
        
        # Test registration
        payment_service = PaymentService()
        
        print(f"\n🚀 ATTEMPTING DOMAIN REGISTRATION...")
        result = await payment_service.complete_domain_registration(
            order.order_id, payment_data
        )
        
        if result:
            print(f"✅ REGISTRATION SUCCESS!")
            
            # Check if domain was stored
            domains = db_manager.get_user_domains(order.telegram_id)
            for domain in domains:
                if domain.domain_name == "ehobalpbwg.sbs":
                    print(f"✅ Domain found in database:")
                    print(f"   Domain ID: {domain.id}")
                    print(f"   OpenProvider ID: {domain.openprovider_domain_id}")
                    print(f"   Cloudflare Zone: {domain.cloudflare_zone_id}")
                    break
            
            return True
        else:
            print(f"❌ REGISTRATION FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_fixed_registration())
    if result:
        print(f"\n🎉 OPENPROVIDER REGISTRATION FIX SUCCESSFUL")
    else:
        print(f"\n💥 REGISTRATION STILL FAILING - NEEDS MORE INVESTIGATION")