#!/usr/bin/env python3
"""
Manual Flowtest Completion
Complete the flowtest36160.sbs registration manually using payment service methods
"""

import sys
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def complete_flowtest_registration():
    """Complete flowtest registration manually using existing service methods"""
    
    print("🔧 MANUAL FLOWTEST COMPLETION")
    print("=" * 40)
    
    from payment_service import PaymentService
    from database import get_db_manager
    
    # Initialize services
    payment_service = PaymentService()
    db = get_db_manager()
    
    # Domain registration details from logs
    order_id = "2884d40b-4b2e-40a5-927b-d41f43400c19"
    telegram_id = 5590563715
    domain_name = "flowtest36160.sbs"
    openprovider_domain_id = "27820529"  # Successfully registered
    cloudflare_zone_id = "b1f4a933342ae51bd93e9dd1f164eb72"  # Created successfully
    contact_handle = "contact_6621"  # Created successfully
    
    print(f"Completing registration for: {domain_name}")
    print(f"OpenProvider Domain ID: {openprovider_domain_id}")
    print(f"Cloudflare Zone ID: {cloudflare_zone_id}")
    print(f"Contact Handle: {contact_handle}")
    
    try:
        # Update order status to completed first
        order = db.get_order(order_id)
        if order:
            print(f"Current order status: {order.payment_status}")
            
            # Manually update order
            session = db.get_session()
            try:
                order.payment_status = "completed"
                order.payment_txid = "0x1234567890abcdef1234567890abcdef12345678"  # Test tx
                session.commit()
                print(f"✅ Order updated to completed status")
            except Exception as e:
                print(f"❌ Order update failed: {e}")
                session.rollback()
            finally:
                session.close()
        
        # Complete domain registration using payment service method
        result = await payment_service.complete_domain_registration(
            order_id=order_id,
            domain_name=domain_name,
            telegram_id=telegram_id,
            nameserver_choice="cloudflare"
        )
        
        if result:
            print(f"✅ Domain registration completed successfully")
            
            # Verify by checking user domains
            domains = db.get_user_domains(telegram_id)
            for domain in domains:
                if domain.domain_name == domain_name:
                    print(f"✅ VERIFIED: {domain_name} now available to user")
                    print(f"   Database ID: {domain.id}")
                    print(f"   OpenProvider ID: {domain.openprovider_domain_id}")
                    print(f"   Cloudflare Zone: {domain.cloudflare_zone_id}")
                    return True
            
            print(f"⚠️ Domain completed but not found in user query")
            return False
        else:
            print(f"❌ Domain registration completion failed")
            return False
            
    except Exception as e:
        print(f"❌ Manual completion error: {e}")
        return False

async def main():
    """Run manual completion"""
    success = await complete_flowtest_registration()
    if success:
        print(f"\n🎉 MANUAL COMPLETION SUCCESSFUL")
        print(f"flowtest36160.sbs is now available to user @onarrival")
    else:
        print(f"\n💥 MANUAL COMPLETION FAILED")

if __name__ == "__main__":
    asyncio.run(main())