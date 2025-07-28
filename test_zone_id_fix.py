#!/usr/bin/env python3
"""
Test Zone ID Fix - Validate that domain service now includes cloudflare_zone_id information
This tests the fix for the "❌ No zone information available" issue
"""

import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from domain_service import get_domain_service
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_zone_id_fix():
    """Test that domain service now includes cloudflare_zone_id information"""
    
    print("🔧 TESTING cloudflare_zone_id FIX")
    print("=" * 50)
    
    # Get domain service
    domain_service = get_domain_service()
    
    # Test user ID - from monitoring logs showing user 5590563715 has domains
    test_user_id = 5590563715
    
    print(f"📊 Testing get_user_domains for user: {test_user_id}")
    
    try:
        # Get user domains using the fixed method
        user_domains = domain_service.get_user_domains(test_user_id)
        
        print(f"✅ Found {len(user_domains)} domains")
        
        if not user_domains:
            print("⚠️  No domains found for test user")
            return False
            
        # Check each domain for cloudflare_zone_id information
        all_tests_passed = True
        
        for i, domain in enumerate(user_domains, 1):
            print(f"\n📋 DOMAIN {i}: {domain.get('domain_name', 'Unknown')}")
            print(f"   🔑 ID: {domain.get('id', 'Missing')}")
            print(f"   📅 Registered: {domain.get('registered_at', 'Missing')}")
            print(f"   ⏰ Expires: {domain.get('expires_at', 'Missing')}")
            print(f"   🌐 Nameserver Mode: {domain.get('nameserver_mode', 'Missing')}")
            print(f"   📊 Status: {domain.get('status', 'Missing')}")
            
            # Critical test: Check for cloudflare_zone_id
            cloudflare_zone_id = domain.get('cloudflare_zone_id', None)
            if cloudflare_zone_id:
                print(f"   ✅ Zone ID: {cloudflare_zone_id}")
                print(f"   ✅ Zone information available - DNS management should work!")
            else:
                print(f"   ❌ Zone ID: None - DNS management will show 'No zone information available'")
                all_tests_passed = False
        
        print("\n" + "=" * 50)
        
        if all_tests_passed:
            print("🎉 cloudflare_zone_id FIX VALIDATION: SUCCESS")
            print("✅ All domains now include cloudflare_zone_id information")
            print("✅ DNS management interface should work correctly")
            print("✅ No more '❌ No zone information available' errors")
        else:
            print("❌ cloudflare_zone_id FIX VALIDATION: FAILED") 
            print("❌ Some domains still missing cloudflare_zone_id information")
            print("❌ DNS management may still show errors")
            
        return all_tests_passed
        
    except Exception as e:
        print(f"❌ ERROR testing cloudflare_zone_id fix: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

def verify_database_zone_ids():
    """Verify that zone_ids actually exist in database"""
    
    print("\n🔍 VERIFYING DATABASE ZONE_IDS")
    print("=" * 50)
    
    try:
        db = get_db_manager()
        
        # Direct database query to verify zone_ids
        with db.get_session() as session:
            from models import RegisteredDomain
            
            domains = session.query(RegisteredDomain).filter(
                RegisteredDomain.telegram_id == 5590563715
            ).all()
            
            print(f"📊 Database shows {len(domains)} domains for user 5590563715")
            
            for i, domain in enumerate(domains, 1):
                print(f"\n📋 DATABASE DOMAIN {i}:")
                print(f"   🌐 Domain: {domain.domain_name}")
                print(f"   🔑 ID: {domain.id}")
                print(f"   ☁️  Zone ID: {domain.cloudflare_zone_id or 'None'}")
                print(f"   🌍 Nameserver Mode: {domain.nameserver_mode or 'None'}")
                
    except Exception as e:
        print(f"❌ ERROR verifying database: {e}")

if __name__ == "__main__":
    # Run both tests
    verify_database_zone_ids()
    success = test_zone_id_fix()
    
    if success:
        print("\n🚀 CONCLUSION: Zone ID fix is working correctly!")
        print("   The domain service now includes cloudflare_zone_id information.")
        print("   DNS management interfaces should work properly.")
    else:
        print("\n⚠️  CONCLUSION: Zone ID fix needs additional work.")
        print("   Some domains may still show 'No zone information available'.")
    
    sys.exit(0 if success else 1)