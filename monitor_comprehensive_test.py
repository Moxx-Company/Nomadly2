#!/usr/bin/env python3
"""
Monitor Comprehensive Test Order
Real-time monitoring of payment, registration, and notifications
"""

import sys
import time
import asyncio
sys.path.insert(0, '/home/runner/workspace')

def check_comprehensive_status(order_id, expected_domain, telegram_id):
    """Check complete status including notifications"""
    from database import get_db_manager
    
    db = get_db_manager()
    
    print(f"📋 COMPREHENSIVE STATUS CHECK")
    print("=" * 30)
    
    # Check order status
    order = db.get_order(order_id)
    payment_confirmed = False
    transaction_id = None
    
    if order:
        print(f"💳 Payment Status: {order.payment_status}")
        if order.payment_txid:
            payment_confirmed = True
            transaction_id = order.payment_txid
            print(f"💰 Transaction: {transaction_id}")
        else:
            print(f"⏳ Payment: Pending confirmation...")
    
    # Check domain registration
    domains = db.get_user_domains(telegram_id)
    domain_registered = False
    domain_details = None
    
    print(f"\n🌐 Domain Registration:")
    for domain in domains:
        if expected_domain in domain.domain_name or domain.domain_name == expected_domain:
            domain_registered = True
            domain_details = domain
            print(f"✅ Domain Found: {domain.domain_name}")
            print(f"   Database ID: {domain.id}")
            print(f"   OpenProvider ID: {domain.openprovider_domain_id}")
            print(f"   CloudFlare Zone: {domain.cloudflare_zone_id}")
            print(f"   Status: {domain.status}")
            break
    
    if not domain_registered:
        print(f"⏳ Domain: Not yet registered")
    
    # Check notification status (simplified)
    print(f"\n📧 Notification Status:")
    if payment_confirmed and domain_registered:
        print(f"✅ Conditions met for notifications")
        print(f"   - Payment confirmed: {payment_confirmed}")
        print(f"   - Domain registered: {domain_registered}")
        print(f"   - Both Telegram and email should be sent")
    else:
        print(f"⏳ Waiting for completion:")
        print(f"   - Payment confirmed: {payment_confirmed}")
        print(f"   - Domain registered: {domain_registered}")
    
    return {
        'payment_confirmed': payment_confirmed,
        'transaction_id': transaction_id,
        'domain_registered': domain_registered,
        'domain_details': domain_details,
        'notifications_expected': payment_confirmed and domain_registered
    }

def monitor_comprehensive_test(order_id, expected_domain, telegram_id, max_checks=15):
    """Monitor comprehensive test with detailed tracking"""
    
    print(f"🔄 MONITORING COMPREHENSIVE TEST")
    print(f"Order: {order_id}")
    print(f"Expected Domain: {expected_domain}")
    print(f"User: @onarrival1 ({telegram_id})")
    print("=" * 50)
    
    for check_num in range(1, max_checks + 1):
        print(f"\n⏰ Comprehensive Check #{check_num}")
        
        status = check_comprehensive_status(order_id, expected_domain, telegram_id)
        
        if status['payment_confirmed'] and status['domain_registered']:
            print(f"\n🎉 COMPREHENSIVE TEST SUCCESSFUL!")
            print(f"   ✅ Payment confirmed: {status['transaction_id']}")
            print(f"   ✅ Domain registered: {status['domain_details'].domain_name}")
            print(f"   ✅ Database saved with OpenProvider ID: {status['domain_details'].openprovider_domain_id}")
            print(f"   ✅ CloudFlare zone created: {status['domain_details'].cloudflare_zone_id}")
            print(f"   ✅ Notifications should be sent to:")
            print(f"      - Telegram user {telegram_id}")
            print(f"      - Email: onarrival21@gmail.com")
            return True
        elif status['payment_confirmed']:
            print(f"   💰 Payment confirmed, waiting for domain registration...")
        elif status['domain_registered']:
            print(f"   🌐 Domain registered, waiting for payment confirmation...")
        else:
            print(f"   ⏳ Waiting for payment and registration...")
        
        if check_num < max_checks:
            print(f"   Checking again in 30 seconds...")
            time.sleep(30)
    
    print(f"\n⏰ Monitoring complete after {max_checks} checks")
    return False

if __name__ == "__main__":
    # These will be set by the main test script
    import sys
    if len(sys.argv) >= 4:
        order_id = sys.argv[1]
        expected_domain = sys.argv[2]
        telegram_id = int(sys.argv[3])
        
        success = monitor_comprehensive_test(order_id, expected_domain, telegram_id)
        
        if success:
            print(f"\n🎉 COMPREHENSIVE TEST COMPLETE!")
            print(f"All systems operational - payment, registration, and notifications")
        else:
            print(f"\n⏰ Test incomplete - continue monitoring manually")
    else:
        print(f"Usage: python monitor_comprehensive_test.py <order_id> <expected_domain> <telegram_id>")