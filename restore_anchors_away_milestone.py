#!/usr/bin/env python3
"""
Restore Anchors Away Milestone
Restore the exact working configuration that achieved successful domain registrations
"""

import sys
import os
sys.path.insert(0, '/home/runner/workspace')

def restore_working_webhook_configuration():
    """Restore webhook server to working anchors away configuration"""
    
    print("🔧 RESTORING WORKING WEBHOOK CONFIGURATION")
    print("=" * 45)
    
    # Key components from anchors away milestone:
    # 1. Proper async/await in webhook notification calls
    # 2. Success flag validation (payment_service.last_domain_registration_success)
    # 3. Both Telegram and email notifications
    # 4. Domain data retrieval for notifications
    
    webhook_fix = """
# Add to webhook_server.py - proper notification logic
if payment_service.last_domain_registration_success:
    # Get domain details for notification
    try:
        latest_domain = db.get_latest_domain_by_telegram_id(telegram_id)
        if latest_domain:
            domain_data = {
                "domain_name": latest_domain.domain_name,
                "registration_status": "Active",
                "expiry_date": latest_domain.expiry_date or "2026-07-21 23:59:59",
                "openprovider_domain_id": latest_domain.openprovider_domain_id,
                "cloudflare_zone_id": latest_domain.cloudflare_zone_id,
                "nameservers": "anderson.ns.cloudflare.com,leanna.ns.cloudflare.com",
                "dns_info": f"DNS configured with Cloudflare Zone ID: {latest_domain.cloudflare_zone_id}"
            }
            
            # Send both notifications (CRITICAL: await this call)
            await confirmation_service.send_domain_registration_confirmation(
                telegram_id, domain_data
            )
            
    except Exception as e:
        logger.error(f"Notification error: {e}")
"""
    
    print("✅ Webhook notification logic identified")
    print("   - Success flag validation")
    print("   - Domain data retrieval")
    print("   - Async notification calls")
    print("   - Both Telegram and email")
    
    return webhook_fix

def restore_payment_service_success_flag():
    """Restore payment service success flag tracking"""
    
    print("\n🔧 RESTORING PAYMENT SERVICE SUCCESS FLAG")
    print("=" * 45)
    
    payment_service_fix = """
# Add to payment_service.py - success flag tracking
class PaymentService:
    def __init__(self):
        self.last_domain_registration_success = False
        
    async def complete_domain_registration(self, order_id, transaction_id):
        try:
            # Reset success flag
            self.last_domain_registration_success = False
            
            # 1. DNS Infrastructure (CloudFlare zone)
            # 2. Domain Registration (OpenProvider)
            # 3. Database Storage
            
            # Only set success flag if ALL steps complete
            self.last_domain_registration_success = True
            
        except Exception as e:
            self.last_domain_registration_success = False
            raise
"""
    
    print("✅ Payment service success flag identified")
    print("   - Success flag reset at start")
    print("   - Success flag set only on complete success")
    print("   - Success flag cleared on any error")
    
    return payment_service_fix

def restore_database_methods():
    """Restore missing database methods"""
    
    print("\n🔧 RESTORING DATABASE METHODS")
    print("=" * 35)
    
    database_fix = """
# Add to database.py - missing methods
def get_latest_domain_by_telegram_id(self, telegram_id):
    '''Get the most recently created domain for a user'''
    session = self.get_session()
    try:
        domain = session.query(RegisteredDomain).filter_by(
            telegram_id=telegram_id
        ).order_by(RegisteredDomain.created_at.desc()).first()
        return domain
    finally:
        session.close()
"""
    
    print("✅ Database methods identified")
    print("   - get_latest_domain_by_telegram_id method")
    print("   - Proper session management")
    
    return database_fix

def check_current_configuration():
    """Check current system configuration"""
    
    print("\n🔍 CHECKING CURRENT CONFIGURATION")
    print("=" * 40)
    
    # Check webhook server
    webhook_issues = []
    try:
        with open('webhook_server.py', 'r') as f:
            webhook_content = f.read()
            
        if 'await confirmation_service.send_domain_registration_confirmation' not in webhook_content:
            webhook_issues.append("Missing async notification call")
            
        if 'payment_service.last_domain_registration_success' not in webhook_content:
            webhook_issues.append("Missing success flag validation")
            
    except Exception as e:
        webhook_issues.append(f"Cannot read webhook_server.py: {e}")
    
    # Check payment service
    payment_issues = []
    try:
        with open('payment_service.py', 'r') as f:
            payment_content = f.read()
            
        if 'last_domain_registration_success' not in payment_content:
            payment_issues.append("Missing success flag tracking")
            
    except Exception as e:
        payment_issues.append(f"Cannot read payment_service.py: {e}")
    
    # Check database
    database_issues = []
    try:
        with open('database.py', 'r') as f:
            database_content = f.read()
            
        if 'get_latest_domain_by_telegram_id' not in database_content:
            database_issues.append("Missing get_latest_domain_by_telegram_id method")
            
    except Exception as e:
        database_issues.append(f"Cannot read database.py: {e}")
    
    print(f"Webhook Issues: {len(webhook_issues)}")
    for issue in webhook_issues:
        print(f"   - {issue}")
        
    print(f"Payment Issues: {len(payment_issues)}")
    for issue in payment_issues:
        print(f"   - {issue}")
        
    print(f"Database Issues: {len(database_issues)}")
    for issue in database_issues:
        print(f"   - {issue}")
    
    return webhook_issues, payment_issues, database_issues

def main():
    """Restore anchors away milestone configuration"""
    
    print("⚓ RESTORING ANCHORS AWAY MILESTONE")
    print("Restoring exact working configuration from successful domain registrations")
    print("=" * 70)
    
    # Analyze working configuration
    webhook_fix = restore_working_webhook_configuration()
    payment_fix = restore_payment_service_success_flag()
    database_fix = restore_database_methods()
    
    # Check current system
    webhook_issues, payment_issues, database_issues = check_current_configuration()
    
    total_issues = len(webhook_issues) + len(payment_issues) + len(database_issues)
    
    print(f"\n📊 RESTORATION ANALYSIS")
    print("=" * 25)
    print(f"Total Issues Found: {total_issues}")
    
    if total_issues == 0:
        print("✅ System appears to match anchors away configuration")
    else:
        print("❌ System needs restoration to anchors away configuration")
        print("\n🔧 FIXES NEEDED:")
        print("1. Webhook async notification calls")
        print("2. Payment service success flag tracking")
        print("3. Database method implementation")
    
    print(f"\n⚓ ANCHORS AWAY MILESTONE CHARACTERISTICS:")
    print("- Domain registration confirmation system 100% operational")
    print("- Payment received → domain registered → confirmation sent")
    print("- Both Telegram and email notifications")
    print("- rolllock10.sbs example: OpenProvider ID 27820045")
    print("- CloudFlare Zone: c8567e871898d9684e2bb5dcac1fd2dc")
    print("- 'Domain Registration Successful!' notifications")

if __name__ == "__main__":
    main()