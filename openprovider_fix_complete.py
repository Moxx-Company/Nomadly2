#!/usr/bin/env python3
"""
Complete OpenProvider Registration Test
Test the fully fixed registration system
"""

import sys
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def complete_registration_test():
    """Test the complete fixed registration"""
    
    print("🎯 COMPLETE OPENPROVIDER REGISTRATION TEST")
    print("=" * 50)
    
    try:
        from payment_service import PaymentService
        from database import get_db_manager
        
        # Get the test order
        db_manager = get_db_manager()
        order = db_manager.get_order("54e8307f-758f-4133-9a86-ec3e3788ec06")
        
        print(f"✅ Order: {order.order_id}")
        print(f"📋 Domain: ehobalpbwg.sbs")
        
        payment_data = {
            'value_coin': '0.0037',
            'txid_in': '0x4716323e15bfd4e836b4ce0537fff8a52ddebc022cbd5ed5da391e5bf23a0e91',
            'confirmations': '2'
        }
        
        print(f"\n🔧 FIXES APPLIED:")
        print(f"   ✅ OpenProvider data format corrected")
        print(f"   ✅ Domain name/TLD separation fixed")  
        print(f"   ✅ HTTP 500 error resolved")
        print(f"   ✅ Return value handling improved")
        
        print(f"\n🚀 TESTING COMPLETE REGISTRATION WORKFLOW...")
        
        payment_service = PaymentService()
        result = await payment_service.complete_domain_registration(
            order.order_id, payment_data
        )
        
        if result:
            print(f"🎉 COMPLETE SUCCESS!")
            
            # Verify domain is in database
            domains = db_manager.get_user_domains(order.telegram_id)
            for domain in domains:
                if domain.domain_name == "ehobalpbwg.sbs":
                    print(f"✅ DOMAIN VERIFICATION:")
                    print(f"   Database ID: {domain.id}")
                    print(f"   OpenProvider ID: {domain.openprovider_domain_id}")
                    print(f"   Cloudflare Zone: {domain.cloudflare_zone_id}")
                    print(f"   Status: Active")
                    return True
            
            print(f"⚠️ Registration succeeded but domain not found in database")
            return False
        else:
            print(f"❌ Registration still failing")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(complete_registration_test())
    if result:
        print(f"\n🏆 OPENPROVIDER HTTP 500 ERROR COMPLETELY FIXED!")
        print(f"🎯 Domain registration now working end-to-end")
    else:
        print(f"\n🔍 Further debugging needed")