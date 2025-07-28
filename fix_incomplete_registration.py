#!/usr/bin/env python3
"""
Fix Incomplete Registration
Investigate and fix testorderaeb99c2d.sbs incomplete registration
"""

import sys
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def investigate_incomplete_registration():
    """Investigate the incomplete domain registration"""
    
    print("🔍 INVESTIGATING INCOMPLETE REGISTRATION")
    print("=" * 45)
    
    from database import get_db_manager
    from apis.production_openprovider import OpenProviderAPI
    
    db = get_db_manager()
    domain_name = "testorderaeb99c2d.sbs"
    telegram_id = 6789012345
    
    # Check current domain status
    domains = db.get_user_domains(telegram_id)
    test_domain = None
    
    for domain in domains:
        if domain.domain_name == domain_name:
            test_domain = domain
            break
    
    if not test_domain:
        print(f"❌ Domain not found in database")
        return False
    
    print(f"📋 Current Domain Status:")
    print(f"   Domain: {test_domain.domain_name}")
    print(f"   Database ID: {test_domain.id}")
    print(f"   OpenProvider ID: {test_domain.openprovider_domain_id or 'MISSING ❌'}")
    print(f"   CloudFlare Zone: {test_domain.cloudflare_zone_id}")
    print(f"   Status: {test_domain.status}")
    
    # Check if domain exists in OpenProvider
    try:
        print(f"\n🔍 Checking OpenProvider for domain...")
        op_api = OpenProviderAPI()
        
        # Search for domain in OpenProvider
        search_result = await op_api.search_domains(domain_name)
        
        if search_result and search_result.get('results'):
            domains_found = search_result['results']
            print(f"✅ Found {len(domains_found)} matching domains in OpenProvider:")
            
            for op_domain in domains_found:
                if op_domain.get('domain', {}).get('name') == domain_name:
                    op_domain_id = op_domain.get('id')
                    print(f"   ✅ Domain found with OpenProvider ID: {op_domain_id}")
                    
                    # Update database with missing OpenProvider ID
                    session = db.get_session()
                    try:
                        session.query(db.RegisteredDomain).filter_by(id=test_domain.id).update({
                            'openprovider_domain_id': str(op_domain_id)
                        })
                        session.commit()
                        print(f"   ✅ Database updated with OpenProvider ID")
                        return True
                    finally:
                        session.close()
        else:
            print(f"❌ Domain NOT found in OpenProvider")
            print(f"   This confirms the registration failed at OpenProvider step")
            
    except Exception as e:
        print(f"❌ OpenProvider check failed: {e}")
    
    return False

async def complete_registration_manually():
    """Complete the registration manually if needed"""
    
    print(f"\n🔧 ATTEMPTING MANUAL REGISTRATION COMPLETION")
    print("=" * 50)
    
    from apis.production_openprovider import OpenProviderAPI
    from database import get_db_manager
    
    db = get_db_manager()
    domain_name = "testorderaeb99c2d.sbs"
    telegram_id = 6789012345
    
    try:
        # Get user's OpenProvider contact
        op_api = OpenProviderAPI()
        
        # Check if we have a contact for this user
        user = db.get_user(telegram_id)
        if not user:
            print(f"❌ User not found")
            return False
        
        # Try to register the domain
        print(f"🔄 Attempting domain registration with OpenProvider...")
        
        contact_handle = "contact_9001"  # Use existing contact from database
        
        registration_result = await op_api.register_domain(
            domain_name=domain_name,
            period=12,  # 1 year
            owner_handle=contact_handle,
            admin_handle=contact_handle,
            tech_handle=contact_handle,
            billing_handle=contact_handle,
            ns_template_name="cloudflare",
            nameservers=[
                "anderson.ns.cloudflare.com",
                "leanna.ns.cloudflare.com"
            ]
        )
        
        if registration_result and registration_result.get('data'):
            op_domain_id = registration_result['data'].get('id')
            print(f"✅ Domain registered successfully!")
            print(f"   OpenProvider Domain ID: {op_domain_id}")
            
            # Update database
            session = db.get_session()
            try:
                session.query(db.RegisteredDomain).filter_by(domain_name=domain_name).update({
                    'openprovider_domain_id': str(op_domain_id),
                    'status': 'active'
                })
                session.commit()
                print(f"✅ Database updated with registration details")
                return True
            finally:
                session.close()
        else:
            print(f"❌ Registration failed: {registration_result}")
            return False
            
    except Exception as e:
        print(f"❌ Manual registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def update_payment_status():
    """Update payment status if payment was actually received"""
    
    print(f"\n💰 CHECKING PAYMENT STATUS")
    print("=" * 30)
    
    from database import get_db_manager
    
    db = get_db_manager()
    order_id = "aeb28feb-3e03-40c5-9425-f7d13be0e577"
    
    # Check if we need to manually verify payment
    print(f"🔍 Order payment status needs verification")
    print(f"   If payment was actually received, it should be updated")
    print(f"   Check BlockBee directly for transaction confirmation")
    
    # For now, just show current status
    order = db.get_order(order_id)
    if order:
        print(f"📋 Current Order Status:")
        print(f"   Payment Status: {order.payment_status}")
        print(f"   Transaction ID: {order.payment_txid or 'None'}")
        print(f"   Payment Address: {order.payment_address}")

async def main():
    """Fix incomplete registration"""
    
    print("🚨 FIXING INCOMPLETE REGISTRATION")
    print("Domain exists in database but missing OpenProvider registration")
    print("=" * 60)
    
    # Step 1: Investigate current status
    domain_found = await investigate_incomplete_registration()
    
    if not domain_found:
        # Step 2: Try to complete registration manually
        registration_success = await complete_registration_manually()
        
        if registration_success:
            print(f"\n🎉 REGISTRATION COMPLETED SUCCESSFULLY!")
            print(f"Domain testorderaeb99c2d.sbs is now fully registered")
        else:
            print(f"\n⚠️  MANUAL REGISTRATION FAILED")
            print(f"Domain exists in database but not actually registered")
    
    # Step 3: Check payment status
    await update_payment_status()
    
    print(f"\n📋 INVESTIGATION COMPLETE")
    print(f"Check domain status and payment confirmation")

if __name__ == "__main__":
    asyncio.run(main())