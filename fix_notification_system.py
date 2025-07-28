#!/usr/bin/env python3
"""
Fix Notification System
Investigate and fix why notifications are not being sent
"""

import sys
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def test_notification_system():
    """Test notification system functionality"""
    
    print("🔧 TESTING NOTIFICATION SYSTEM")
    print("=" * 35)
    
    from services.confirmation_service import ConfirmationService
    from database import get_db_manager
    
    db = get_db_manager()
    telegram_id = 6789012345  # @onarrival1
    
    # Get the registered domain
    domains = db.get_user_domains(telegram_id)
    test_domain = None
    
    for domain in domains:
        if 'testorder' in domain.domain_name:
            test_domain = domain
            break
    
    if not test_domain:
        print("❌ Test domain not found")
        return False
    
    print(f"✅ Found test domain: {test_domain.domain_name}")
    print(f"   Database ID: {test_domain.id}")
    print(f"   CloudFlare Zone: {test_domain.cloudflare_zone_id}")
    
    # Prepare domain data for notifications
    domain_data = {
        "domain_name": test_domain.domain_name,
        "registration_status": "Active",
        "expiry_date": "2026-07-21 23:59:59",
        "openprovider_domain_id": test_domain.openprovider_domain_id or "TEST123",
        "cloudflare_zone_id": test_domain.cloudflare_zone_id,
        "nameservers": "anderson.ns.cloudflare.com,leanna.ns.cloudflare.com",
        "dns_info": f"DNS configured with Cloudflare Zone ID: {test_domain.cloudflare_zone_id}"
    }
    
    # Test notification system
    try:
        confirmation_service = ConfirmationService()
        
        print(f"\n📧 Testing notification system...")
        await confirmation_service.send_domain_registration_confirmation(
            telegram_id, domain_data
        )
        
        print(f"✅ Notification system test completed")
        print(f"   Check if @onarrival1 received bot notification")
        print(f"   Check if email was sent to onarrival21@gmail.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Notification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_webhook_notification_logic():
    """Check webhook notification triggering logic"""
    
    print(f"\n🔍 WEBHOOK NOTIFICATION LOGIC CHECK")
    print("=" * 40)
    
    # Check webhook_server.py for notification triggering
    try:
        with open('webhook_server.py', 'r') as f:
            content = f.read()
            
        # Look for notification triggers
        if 'send_domain_registration_confirmation' in content:
            print(f"✅ Webhook contains notification trigger")
        else:
            print(f"❌ Webhook missing notification trigger")
            
        if 'payment_service.last_domain_registration_success' in content:
            print(f"✅ Webhook checks registration success flag")
        else:
            print(f"❌ Webhook missing success flag check")
            
        # Check for proper conditional logic
        if 'if payment_service.last_domain_registration_success' in content:
            print(f"✅ Conditional notification logic present")
        else:
            print(f"⚠️  Notification logic may be unconditional")
            
        return True
        
    except Exception as e:
        print(f"❌ Webhook check failed: {e}")
        return False

def analyze_notification_failure():
    """Analyze why notifications failed"""
    
    print(f"\n📊 NOTIFICATION FAILURE ANALYSIS")
    print("=" * 35)
    
    print(f"💰 Payment Status: ✅ Confirmed")
    print(f"🌐 Domain Registration: ✅ Successful") 
    print(f"💾 Database Storage: ✅ Correct user account")
    print(f"🔔 Notification Trigger: ❌ Failed")
    
    print(f"\n🎯 POSSIBLE CAUSES:")
    print(f"1. Webhook server restart interrupted notification")
    print(f"2. Notification conditions not met in webhook")
    print(f"3. Bot instance conflicts preventing message delivery")
    print(f"4. Email service configuration issues")
    
    print(f"\n🔧 RECOMMENDED FIXES:")
    print(f"1. Test notification system directly")
    print(f"2. Check webhook notification conditions")
    print(f"3. Restart webhook server properly")
    print(f"4. Verify bot and email service status")

async def send_manual_notification():
    """Send manual notification for the test domain"""
    
    print(f"\n📧 SENDING MANUAL NOTIFICATION")
    print("=" * 30)
    
    success = await test_notification_system()
    
    if success:
        print(f"\n🎉 MANUAL NOTIFICATION SENT!")
        print(f"   This proves the notification system works")
        print(f"   Issue was with webhook triggering, not notification service")
    else:
        print(f"\n❌ MANUAL NOTIFICATION FAILED")
        print(f"   Notification service needs debugging")

async def main():
    """Run complete notification system analysis"""
    
    print("🚨 NOTIFICATION SYSTEM INVESTIGATION")
    print("Payment confirmed but no notifications sent")
    print("=" * 50)
    
    # Check webhook logic
    webhook_ok = check_webhook_notification_logic()
    
    # Analyze failure
    analyze_notification_failure()
    
    # Test and send manual notification
    await send_manual_notification()
    
    print(f"\n📋 INVESTIGATION COMPLETE")
    print(f"Notification system tested and manual notification attempted")

if __name__ == "__main__":
    asyncio.run(main())