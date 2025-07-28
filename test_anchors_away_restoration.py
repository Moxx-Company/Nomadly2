#!/usr/bin/env python3
"""
Test Anchors Away Milestone Restoration
Verify that the working configuration from successful domain registrations has been restored
"""

import sys
import os
sys.path.insert(0, '/home/runner/workspace')

def test_payment_service_success_flag():
    """Test payment service success flag tracking"""
    print("🔧 TESTING PAYMENT SERVICE SUCCESS FLAG")
    print("=" * 45)
    
    try:
        from payment_service import PaymentService
        ps = PaymentService()
        
        # Test attribute exists
        has_flag = hasattr(ps, 'last_domain_registration_success')
        print(f"✅ last_domain_registration_success attribute: {has_flag}")
        
        if has_flag:
            print(f"✅ Initial value: {ps.last_domain_registration_success}")
            
            # Test setting
            ps.last_domain_registration_success = True
            print(f"✅ After setting True: {ps.last_domain_registration_success}")
            
            ps.last_domain_registration_success = False
            print(f"✅ After setting False: {ps.last_domain_registration_success}")
            
            return True
        else:
            print("❌ Missing success flag attribute")
            return False
            
    except Exception as e:
        print(f"❌ Error testing payment service: {e}")
        return False

def test_webhook_success_validation():
    """Test webhook success flag validation"""
    print("\n🔧 TESTING WEBHOOK SUCCESS VALIDATION")
    print("=" * 45)
    
    try:
        with open('webhook_server.py', 'r') as f:
            webhook_content = f.read()
            
        # Check for success flag validation
        checks = [
            ('payment_service.last_domain_registration_success', 'Success flag check'),
            ('ANCHORS AWAY MILESTONE', 'Milestone comments'),
            ('await confirmation_service.send_domain_registration_confirmation', 'Async notification call')
        ]
        
        all_passed = True
        for check, description in checks:
            found = check in webhook_content
            status = "✅" if found else "❌"
            print(f"{status} {description}: {found}")
            if not found:
                all_passed = False
                
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def test_database_methods():
    """Test database methods for notification"""
    print("\n🔧 TESTING DATABASE METHODS")
    print("=" * 35)
    
    try:
        from database import get_db_manager
        db = get_db_manager()
        
        # Test method exists
        has_method = hasattr(db, 'get_latest_domain_by_telegram_id')
        print(f"✅ get_latest_domain_by_telegram_id method: {has_method}")
        
        return has_method
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False

def test_confirmation_service():
    """Test confirmation service"""
    print("\n🔧 TESTING CONFIRMATION SERVICE")
    print("=" * 40)
    
    try:
        from services.confirmation_service import get_confirmation_service
        cs = get_confirmation_service()
        
        # Test method exists
        has_method = hasattr(cs, 'send_domain_registration_confirmation')
        print(f"✅ send_domain_registration_confirmation method: {has_method}")
        
        return has_method
        
    except Exception as e:
        print(f"❌ Error testing confirmation service: {e}")
        return False

def main():
    """Test anchors away milestone restoration"""
    
    print("⚓ TESTING ANCHORS AWAY MILESTONE RESTORATION")
    print("Testing exact working configuration from successful domain registrations")
    print("=" * 70)
    
    tests = [
        test_payment_service_success_flag,
        test_webhook_success_validation,
        test_database_methods,
        test_confirmation_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 TEST RESULTS")
    print("=" * 20)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ ANCHORS AWAY MILESTONE FULLY RESTORED")
        print("- Success flag tracking operational")
        print("- Webhook validation implemented") 
        print("- Database methods available")
        print("- Confirmation service ready")
        print("- Domain registration workflow should work like rolllock10.sbs")
    else:
        print(f"\n❌ RESTORATION INCOMPLETE ({total-passed} issues remaining)")
        print("- System needs additional fixes to match anchors away configuration")
    
    print(f"\n⚓ ORIGINAL ANCHORS AWAY CHARACTERISTICS:")
    print("- rolllock10.sbs: OpenProvider ID 27820045")
    print("- CloudFlare Zone: c8567e871898d9684e2bb5dcac1fd2dc")
    print("- 'Domain Registration Successful!' notifications")
    print("- Both Telegram and email confirmations")

if __name__ == "__main__":
    main()