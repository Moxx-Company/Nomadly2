#!/usr/bin/env python3
"""
Complete Domain Ownership Fix
Transfer domain and update OpenProvider ID properly
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

def fix_complete_ownership():
    """Complete fix of domain ownership issue"""
    
    print("🔧 COMPLETE DOMAIN OWNERSHIP FIX")
    print("=" * 40)
    
    from database import get_db_manager
    
    db = get_db_manager()
    
    # Real IDs and domain
    test_user_id = 6789012345  # @onarrival1 (test account)
    real_user_id = 5590563715  # @onarrival (your real account)
    domain_name = "onarrivale1722e.sbs"
    openprovider_id = "27820621"  # From logs
    
    print(f"Domain: {domain_name}")
    print(f"Moving from test user {test_user_id} to real user {real_user_id}")
    print(f"OpenProvider ID: {openprovider_id}")
    
    try:
        session = db.get_session()
        
        # Find domain record
        from database import RegisteredDomain
        domain_record = session.query(RegisteredDomain).filter_by(
            domain_name=domain_name,
            telegram_id=test_user_id
        ).first()
        
        if not domain_record:
            print(f"❌ Domain record not found")
            return False
        
        print(f"\n✅ Found domain record (ID: {domain_record.id})")
        
        # Update ownership and OpenProvider ID
        domain_record.telegram_id = real_user_id
        domain_record.openprovider_domain_id = openprovider_id
        
        session.commit()
        
        print(f"✅ Domain ownership transferred to user {real_user_id}")
        print(f"✅ OpenProvider ID updated to {openprovider_id}")
        
        # Verify the fix
        updated_domain = session.query(RegisteredDomain).filter_by(
            domain_name=domain_name,
            telegram_id=real_user_id
        ).first()
        
        if updated_domain:
            print(f"\n✅ VERIFICATION SUCCESSFUL:")
            print(f"   Domain: {updated_domain.domain_name}")
            print(f"   User ID: {updated_domain.telegram_id}")
            print(f"   OpenProvider ID: {updated_domain.openprovider_domain_id}")
            print(f"   CloudFlare Zone: {updated_domain.cloudflare_zone_id}")
            print(f"   Status: {updated_domain.status}")
            
            session.close()
            return True
        else:
            print(f"❌ Verification failed")
            session.close()
            return False
            
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

def verify_user_domains():
    """Verify domain is now in your account"""
    
    print(f"\n📊 DOMAIN VERIFICATION")
    print("=" * 25)
    
    from database import get_db_manager
    db = get_db_manager()
    
    real_user_id = 5590563715
    domains = db.get_user_domains(real_user_id)
    
    print(f"Your domains ({len(domains)} total):")
    
    for domain in domains:
        print(f"   - {domain.domain_name}")
        if "onarrival" in domain.domain_name:
            print(f"     ✅ NEWLY ADDED! (Database ID: {domain.id})")
            print(f"     OpenProvider ID: {domain.openprovider_domain_id}")
            print(f"     CloudFlare Zone: {domain.cloudflare_zone_id}")

if __name__ == "__main__":
    print("🚨 CRITICAL ISSUE IDENTIFIED:")
    print("   Payment made by real user but domain registered to test account")
    print("   Fixing ownership and OpenProvider ID...\n")
    
    success = fix_complete_ownership()
    
    if success:
        verify_user_domains()
        print(f"\n🎉 COMPLETE FIX SUCCESSFUL!")
        print(f"   Domain now properly assigned to your account")
        print(f"   OpenProvider ID correctly updated")
        print(f"   You should now see the domain in your bot account")
    else:
        print(f"\n💥 FIX FAILED - Manual intervention needed")