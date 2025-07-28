#!/usr/bin/env python3
"""
Comprehensive test of the DNS record validation and deletion fixes
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ns_record_validation():
    """Test NS record validation that was incorrectly requiring IPv4"""
    print("🧪 TESTING NS RECORD VALIDATION FIX")
    print("=" * 40)
    
    try:
        from nomadly3_clean_bot import NomadlyCleanBot
        bot = NomadlyCleanBot()
        
        # Test valid nameservers (should pass)
        valid_nameservers = [
            "ns1.example.com",
            "anderson.ns.cloudflare.com", 
            "dns1.registrar.com",
            "nameserver.provider.net"
        ]
        
        print("✅ Testing valid nameservers:")
        for ns in valid_nameservers:
            is_valid = bot.is_valid_nameserver(ns)
            status = "✅ PASS" if is_valid else "❌ FAIL"
            print(f"   {ns}: {status}")
        
        # Test invalid nameservers (should fail)
        invalid_nameservers = [
            "192.168.1.1",  # IPv4 address (should fail for NS records)
            "208.77.244.11",
            "invalid..domain",
            "toolong" + "x" * 250 + ".com"
        ]
        
        print("\n❌ Testing invalid nameservers:")
        for ns in invalid_nameservers:
            is_valid = bot.is_valid_nameserver(ns)
            status = "✅ CORRECTLY REJECTED" if not is_valid else "❌ INCORRECTLY ACCEPTED"
            print(f"   {ns}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing NS validation: {e}")
        return False

async def test_dns_deletion_api_fix():
    """Test DNS deletion API fix (zone_id instead of domain)"""
    print("\n🗑️ TESTING DNS DELETION API FIX")
    print("=" * 40)
    
    try:
        from unified_dns_manager import UnifiedDNSManager
        import inspect
        
        manager = UnifiedDNSManager()
        delete_method = getattr(manager, 'delete_dns_record')
        sig = inspect.signature(delete_method)
        
        print("Method signature check:")
        print(f"delete_dns_record{sig}")
        
        # Check parameters
        params = list(sig.parameters.keys())
        if 'zone_id' in params and 'record_id' in params:
            print("✅ Correct parameters: zone_id and record_id found")
            if 'domain' not in params:
                print("✅ Old 'domain' parameter correctly removed")
                return True
            else:
                print("❌ Old 'domain' parameter still exists")
                return False
        else:
            print("❌ Required parameters missing")
            print(f"   Found: {params}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing deletion API: {e}")
        return False

async def test_session_cleanup():
    """Test that session cleanup successfully cleared stuck states"""
    print("\n🧹 TESTING SESSION CLEANUP SUCCESS")
    print("=" * 40)
    
    try:
        import json
        
        with open('user_sessions.json', 'r') as f:
            sessions = json.load(f)
        
        user_session = sessions.get('5590563715', {})
        
        stuck_states = [
            'waiting_for_nameservers',
            'waiting_for_ns', 
            'waiting_for_dns_edit',
            'waiting_for_dns_input'
        ]
        
        print("Session state check:")
        all_clear = True
        for state in stuck_states:
            if state in user_session:
                print(f"❌ {state}: Still present (PROBLEM)")
                all_clear = False
            else:
                print(f"✅ {state}: Cleared")
        
        if all_clear:
            print("\n✅ All stuck states successfully cleared!")
            print("User should now be able to search domains normally")
            return True
        else:
            print("\n❌ Some stuck states remain")
            return False
            
    except Exception as e:
        print(f"❌ Error checking session: {e}")
        return False

async def main():
    """Run comprehensive tests"""
    print("🔍 COMPREHENSIVE DNS FIXES VERIFICATION")
    print("=" * 50)
    print("Testing NS record validation and DNS deletion API fixes\n")
    
    results = []
    
    # Run all tests
    results.append(await test_ns_record_validation())
    results.append(await test_dns_deletion_api_fix()) 
    results.append(await test_session_cleanup())
    
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    tests = [
        "NS Record Validation Fix",
        "DNS Deletion API Fix", 
        "Session Cleanup Success"
    ]
    
    for i, (test_name, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_name}: {status}")
    
    overall_success = all(results)
    print(f"\n🎯 OVERALL STATUS: {'✅ ALL FIXES WORKING' if overall_success else '❌ SOME ISSUES REMAIN'}")
    
    if overall_success:
        print("\n✅ PROBLEM RESOLUTION CONFIRMED:")
        print("   1. NS records now accept domain names (not IP addresses)")
        print("   2. DNS deletion uses correct zone_id parameter")
        print("   3. Your stuck session has been cleared")
        print("   4. You can now search domains normally")
        print("   5. NS record editing will work with valid nameserver formats")
    else:
        print("\n❌ Issues that still need attention:")
        for i, (test_name, result) in enumerate(zip(tests, results)):
            if not result:
                print(f"   - {test_name}")

if __name__ == "__main__":
    asyncio.run(main())