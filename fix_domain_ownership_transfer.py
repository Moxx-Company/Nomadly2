#!/usr/bin/env python3
"""
Fix Domain Ownership Transfer
Transfer onarrivale1722e.sbs from test account to real user account
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

def transfer_domain_ownership():
    """Transfer domain from test user to real user"""
    
    print("🔧 FIXING DOMAIN OWNERSHIP ISSUE")
    print("=" * 40)
    
    from database import get_db_manager
    
    db = get_db_manager()
    
    # IDs
    test_user_id = 6789012345  # @onarrival1 (test account)
    real_user_id = 5590563715  # @onarrival (your real account)
    domain_name = "onarrivale1722e.sbs"
    
    print(f"Domain: {domain_name}")
    print(f"From: Test User {test_user_id} (@onarrival1)")
    print(f"To: Real User {real_user_id} (@onarrival)")
    
    # Find the domain in test account
    test_domains = db.get_user_domains(test_user_id)
    target_domain = None
    
    for domain in test_domains:
        if domain.domain_name == domain_name:
            target_domain = domain
            break
    
    if not target_domain:
        print(f"❌ Domain {domain_name} not found in test account")
        return False
    
    print(f"\n✅ Found domain in test account:")
    print(f"   Database ID: {target_domain.id}")
    print(f"   OpenProvider ID: {target_domain.openprovider_domain_id}")
    print(f"   CloudFlare Zone: {target_domain.cloudflare_zone_id}")
    print(f"   Status: {target_domain.status}")
    
    # Transfer ownership
    try:
        session = db.get_session()
        target_domain.telegram_id = real_user_id
        session.commit()
        session.close()
        
        print(f"\n✅ DOMAIN OWNERSHIP TRANSFERRED")
        print(f"   Domain {domain_name} now belongs to user {real_user_id}")
        
        # Verify transfer
        real_domains = db.get_user_domains(real_user_id)
        found_in_real = any(d.domain_name == domain_name for d in real_domains)
        
        if found_in_real:
            print(f"✅ Verification: Domain now visible in real user account")
            return True
        else:
            print(f"❌ Verification failed: Domain not found in real user account")
            return False
            
    except Exception as e:
        print(f"❌ Transfer failed: {e}")
        return False

def send_proper_notifications():
    """Send proper notifications to real user"""
    
    print(f"\n📧 SENDING PROPER NOTIFICATIONS")
    print("=" * 35)
    
    import asyncio
    from services.confirmation_service import ConfirmationService
    from database import get_db_manager
    
    async def send_notifications():
        confirmation_service = ConfirmationService()
        db = get_db_manager()
        
        real_user_id = 5590563715
        domain_name = "onarrivale1722e.sbs"
        
        # Get domain details
        domain = db.get_domain_by_name(domain_name, real_user_id)
        if not domain:
            print(f"❌ Domain not found for real user")
            return False
        
        # Prepare domain data
        domain_data = {
            "domain_name": domain.domain_name,
            "registration_status": "Active",
            "expiry_date": "2026-07-21 23:59:59",
            "openprovider_domain_id": domain.openprovider_domain_id or "27820621",
            "cloudflare_zone_id": domain.cloudflare_zone_id,
            "nameservers": "anderson.ns.cloudflare.com,leanna.ns.cloudflare.com",
            "dns_info": f"DNS configured with Cloudflare Zone ID: {domain.cloudflare_zone_id}"
        }
        
        try:
            await confirmation_service.send_domain_registration_confirmation(
                real_user_id, domain_data
            )
            print(f"✅ Registration confirmation sent to real user")
            return True
        except Exception as e:
            print(f"❌ Notification failed: {e}")
            return False
    
    return asyncio.run(send_notifications())

if __name__ == "__main__":
    print("🚨 ISSUE: Domain registered to wrong user account")
    print("💰 Payment was made by real user but domain went to test account")
    print("🔧 Fixing ownership and notifications...\n")
    
    # Step 1: Transfer ownership
    transfer_success = transfer_domain_ownership()
    
    if transfer_success:
        # Step 2: Send proper notifications
        notification_success = send_proper_notifications()
        
        if notification_success:
            print(f"\n🎉 COMPLETE FIX SUCCESSFUL")
            print(f"   Domain now in your real account")
            print(f"   Proper notifications sent")
        else:
            print(f"\n⚠️  Domain transferred but notifications failed")
    else:
        print(f"\n💥 TRANSFER FAILED")
        print(f"Domain ownership could not be corrected")