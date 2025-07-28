#!/usr/bin/env python3
"""
Monitor Payment Status
Real-time monitoring of payment confirmation and registration process
"""

import sys
import time
import asyncio
sys.path.insert(0, '/home/runner/workspace')

def check_payment_status(order_id):
    """Check current payment and registration status"""
    from database import get_db_manager
    
    db = get_db_manager()
    
    print(f"📋 ORDER STATUS CHECK")
    print("=" * 25)
    
    # Check order
    order = db.get_order(order_id)
    if order:
        print(f"Order ID: {order.order_id}")
        print(f"Payment Status: {order.payment_status}")
        print(f"Transaction ID: {order.payment_txid or 'Pending confirmation...'}")
        print(f"Domain: onarrivale1722e.sbs")
        print(f"Amount: $2.99")
        
        # Check if domain was created
        domains = db.get_user_domains(order.telegram_id)
        domain_found = False
        
        print(f"\n📊 USER DOMAINS ({len(domains)} total):")
        for domain in domains:
            print(f"   - {domain.domain_name}")
            if 'onarrival' in domain.domain_name:
                domain_found = True
                print(f"     ✅ NEW DOMAIN FOUND!")
                print(f"     Database ID: {domain.id}")
                print(f"     OpenProvider ID: {domain.openprovider_domain_id}")
                print(f"     CloudFlare Zone: {domain.cloudflare_zone_id}")
                print(f"     Status: {domain.status}")
        
        return {
            'order_status': order.payment_status,
            'transaction_id': order.payment_txid,
            'domain_registered': domain_found
        }
    else:
        print("❌ Order not found")
        return None

def monitor_continuously(order_id, max_checks=20):
    """Monitor payment status with continuous checking"""
    
    print(f"🔄 MONITORING PAYMENT FOR @onarrival1")
    print(f"Order: {order_id}")
    print(f"Domain: onarrivale1722e.sbs")
    print("=" * 50)
    
    for check_num in range(1, max_checks + 1):
        print(f"\n⏰ Check #{check_num}")
        
        status = check_payment_status(order_id)
        
        if status:
            if status['transaction_id']:
                print(f"\n🎉 PAYMENT CONFIRMED!")
                print(f"   Transaction: {status['transaction_id']}")
                
                if status['domain_registered']:
                    print(f"   ✅ Domain registered and saved to database")
                    print(f"   🎯 DATABASE SAVING BUG RESOLUTION VERIFIED!")
                    return True
                else:
                    print(f"   ⏳ Domain registration in progress...")
            else:
                print(f"   ⏳ Waiting for payment confirmation...")
        
        if check_num < max_checks:
            print(f"   Checking again in 30 seconds...")
            time.sleep(30)
    
    print(f"\n⏰ Monitoring complete after {max_checks} checks")
    return False

if __name__ == "__main__":
    order_id = "f932345f-d975-4781-8024-a26c3c54c48e"
    
    # Initial check
    initial_status = check_payment_status(order_id)
    
    if initial_status and initial_status['transaction_id']:
        print(f"\n✅ Payment already confirmed!")
    else:
        print(f"\n🔄 Starting continuous monitoring...")
        print(f"Will check every 30 seconds for up to 10 minutes...")
        
        success = monitor_continuously(order_id)
        
        if success:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print(f"Payment confirmed and domain registered successfully.")
        else:
            print(f"\n⏰ Payment not yet confirmed.")
            print(f"Continue monitoring or check payment status manually.")