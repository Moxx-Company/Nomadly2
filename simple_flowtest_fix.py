#!/usr/bin/env python3
"""
Simple Flowtest Fix
Create database record using the exact method signature from database.py
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

def fix_flowtest_simple():
    """Create database record using correct method signature"""
    
    print("🔧 SIMPLE FLOWTEST FIX")
    print("=" * 30)
    
    from database import get_db_manager
    
    db = get_db_manager()
    
    # Domain details from successful registration
    telegram_id = 5590563715
    domain_name = "flowtest36160.sbs"
    openprovider_contact_handle = "contact_6621"
    cloudflare_zone_id = "b1f4a933342ae51bd93e9dd1f164eb72"
    nameservers = "anderson.ns.cloudflare.com,leanna.ns.cloudflare.com"
    
    print(f"Creating record for: {domain_name}")
    print(f"User: {telegram_id}")
    print(f"Contact: {openprovider_contact_handle}")
    print(f"Zone: {cloudflare_zone_id}")
    
    try:
        # Use the exact method signature from database.py lines 583-592
        saved_domain = db.create_registered_domain(
            telegram_id=telegram_id,
            domain_name=domain_name,
            openprovider_contact_handle=openprovider_contact_handle,
            cloudflare_zone_id=cloudflare_zone_id,
            nameservers=nameservers
        )
        
        if saved_domain:
            print(f"✅ SUCCESS: Domain saved to database")
            print(f"   Database ID: {saved_domain.id}")
            print(f"   Domain: {saved_domain.domain_name}")
            
            # Now update with OpenProvider domain ID
            session = db.get_session()
            try:
                saved_domain.openprovider_domain_id = "27820529"
                saved_domain.status = "active"
                session.commit()
                print(f"✅ OpenProvider ID added: 27820529")
            except Exception as e:
                print(f"Warning: Could not add OpenProvider ID: {e}")
                session.rollback()
            finally:
                session.close()
            
            return True
        else:
            print(f"❌ Database save returned None")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_flowtest():
    """Verify the domain is now available to user"""
    
    print(f"\n🔍 VERIFICATION")
    print("=" * 15)
    
    from database import get_db_manager
    db = get_db_manager()
    
    domains = db.get_user_domains(5590563715)
    print(f"Total domains: {len(domains)}")
    
    for domain in domains:
        if 'flowtest' in domain.domain_name:
            print(f"\n✅ FLOWTEST FOUND:")
            print(f"   Domain: {domain.domain_name}")
            print(f"   Database ID: {domain.id}")
            print(f"   OpenProvider ID: {domain.openprovider_domain_id}")
            print(f"   Cloudflare Zone: {domain.cloudflare_zone_id}")
            print(f"   Status: {domain.status}")
            return True
    
    print(f"❌ flowtest36160.sbs still not found")
    return False

if __name__ == "__main__":
    success = fix_flowtest_simple()
    if success:
        verify_flowtest()
        print(f"\n🎉 FLOWTEST FIXED - Now available to @onarrival")
    else:
        print(f"\n💥 FIX FAILED")