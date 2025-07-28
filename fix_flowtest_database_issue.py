#!/usr/bin/env python3
"""
Fix flowtest36160.sbs Database Issue
Manually create database record for successful OpenProvider registration
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

def fix_flowtest_database():
    """Create database record for flowtest36160.sbs"""
    
    print("🔧 FIXING FLOWTEST DATABASE ISSUE")
    print("=" * 40)
    
    from database import get_db_manager, RegisteredDomain
    from datetime import datetime
    
    db = get_db_manager()
    
    # Domain details from successful OpenProvider registration
    domain_data = {
        'telegram_id': 5590563715,
        'domain_name': 'flowtest36160.sbs',
        'openprovider_domain_id': '27820529',  # From logs
        'cloudflare_zone_id': 'b1f4a933342ae51bd93e9dd1f164eb72',  # From logs
        'nameservers': 'anderson.ns.cloudflare.com,leanna.ns.cloudflare.com',
        'openprovider_contact_handle': 'contact_6621',  # From logs
        'nameserver_mode': 'cloudflare',
        'status': 'active',
        'registration_date': datetime.now(),
        'expiry_date': datetime.now().replace(year=datetime.now().year + 1),
        'auto_renew': True,
        'price_paid': 2.99,
        'payment_method': 'crypto_eth',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    print(f"Creating database record for: {domain_data['domain_name']}")
    print(f"OpenProvider ID: {domain_data['openprovider_domain_id']}")
    print(f"Cloudflare Zone: {domain_data['cloudflare_zone_id']}")
    
    try:
        # Create RegisteredDomain object
        domain = RegisteredDomain(**domain_data)
        
        # Save to database using correct method signature based on database.py
        saved_domain = db.create_registered_domain(
            telegram_id=domain_data['telegram_id'],
            domain_name=domain_data['domain_name'],
            nameservers=domain_data['nameservers'],
            nameserver_mode=domain_data['nameserver_mode'],
            status=domain_data['status'],
            registration_date=domain_data['registration_date'],
            expiry_date=domain_data['expiry_date'],
            auto_renew=domain_data['auto_renew'],
            price_paid=domain_data['price_paid'],
            payment_method=domain_data['payment_method'],
            # Optional fields that might be accepted
            cloudflare_zone_id=domain_data['cloudflare_zone_id'],
            contact_handle=domain_data['openprovider_contact_handle']
        )
        
        if saved_domain:
            print(f"✅ SUCCESS: Domain saved to database")
            print(f"   Database ID: {saved_domain.id}")
            print(f"   Domain: {saved_domain.domain_name}")
            print(f"   OpenProvider ID: {saved_domain.openprovider_domain_id}")
            
            # Verify by checking user domains
            user_domains = db.get_user_domains(5590563715)
            flowtest_found = False
            for domain in user_domains:
                if 'flowtest' in domain.domain_name:
                    flowtest_found = True
                    print(f"✅ VERIFIED: flowtest now available to user")
                    break
            
            if not flowtest_found:
                print(f"⚠️ WARNING: Domain saved but not found in user query")
            
            return True
        else:
            print(f"❌ FAILED: Database save returned None")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Database save failed: {e}")
        return False

def verify_fix():
    """Verify the fix worked"""
    
    print(f"\n🔍 VERIFICATION CHECK")
    print("=" * 20)
    
    from database import get_db_manager
    db = get_db_manager()
    
    domains = db.get_user_domains(5590563715)
    print(f"Total domains for user: {len(domains)}")
    
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
    success = fix_flowtest_database()
    if success:
        verify_fix()
    else:
        print(f"\n💥 FIX FAILED - Database issue persists")