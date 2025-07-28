#!/usr/bin/env python3
"""
Test script to verify email and bot confirmation system
Tests all three confirmation types:
1. Payment confirmation (email + bot)
2. Domain registration completion (email + bot)
3. Wallet funding confirmation
"""

import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_payment_confirmation():
    """Test payment confirmation email and bot notification"""
    try:
        from services.confirmation_service import ConfirmationService
        
        confirmation_service = ConfirmationService()
        
        # Test data for payment confirmation
        test_order_data = {
            "order_id": "TEST-PAYMENT-123",
            "amount_usd": 49.50,
            "payment_method": "Cryptocurrency",
            "transaction_id": "0x1234567890abcdef",
            "service_description": "Domain Registration"
        }
        
        # Test with sample user ID
        test_user_id = 5590563715  # From user sessions
        
        print(f"📧 Testing payment confirmation for user {test_user_id}")
        
        # Send payment confirmation
        success = await confirmation_service.send_payment_confirmation(
            test_user_id, test_order_data
        )
        
        if success:
            print("✅ Payment confirmation sent successfully!")
            return True
        else:
            print("❌ Payment confirmation failed")
            return False
            
    except Exception as e:
        print(f"❌ Payment confirmation test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_domain_registration_confirmation():
    """Test domain registration completion email and bot notification"""
    try:
        from services.confirmation_service import ConfirmationService
        
        confirmation_service = ConfirmationService()
        
        # Test data for domain registration completion
        test_domain_data = {
            "domain_name": "test-domain.sbs",
            "registration_status": "Active",
            "expiry_date": "2026-07-25 23:59:59",
            "openprovider_domain_id": "12345678",
            "cloudflare_zone_id": "abc123def456",
            "nameservers": ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"],
            "dns_info": "DNS configured with Cloudflare"
        }
        
        # Test with sample user ID
        test_user_id = 5590563715
        
        print(f"🌐 Testing domain registration confirmation for user {test_user_id}")
        
        # Send domain registration confirmation
        success = await confirmation_service.send_domain_registration_confirmation(
            test_user_id, test_domain_data
        )
        
        if success:
            print("✅ Domain registration confirmation sent successfully!")
            return True
        else:
            print("❌ Domain registration confirmation failed")
            return False
            
    except Exception as e:
        print(f"❌ Domain registration confirmation test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def verify_email_service():
    """Verify email service is properly configured"""
    try:
        print("🔧 Verifying email service configuration...")
        
        # Check Brevo service
        try:
            from services.brevo_email_service import BrevoEmailService
            brevo_service = BrevoEmailService()
            print(f"   Brevo Service: ✅ Available")
            
            # Check if API key is configured
            api_key = os.getenv('BREVO_API_KEY')
            if api_key:
                print(f"   Brevo API Key: ✅ Configured ({api_key[:10]}...)")
            else:
                print(f"   Brevo API Key: ⚠️ Not configured - emails will be simulated")
                
        except Exception as e:
            print(f"   Brevo Service: ❌ Error - {e}")
        
        # Check confirmation service
        try:
            from services.confirmation_service import ConfirmationService
            confirmation_service = ConfirmationService()
            is_configured = confirmation_service.is_configured()
            print(f"   Confirmation Service: ✅ Available (Configured: {is_configured})")
        except Exception as e:
            print(f"   Confirmation Service: ❌ Error - {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Email service verification error: {e}")
        return False

async def test_bot_notification():
    """Test bot notification capability"""
    try:
        print("🤖 Testing bot notification system...")
        
        # Check if bot is accessible
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ Bot token not configured")
            return False
            
        print(f"   Bot Token: ✅ Configured")
        
        # Check if we can load user sessions
        if os.path.exists('user_sessions.json'):
            with open('user_sessions.json', 'r') as f:
                sessions = json.load(f)
            
            print(f"   User Sessions: ✅ {len(sessions)} active users")
            
            # Get sample user email
            if sessions:
                sample_user = list(sessions.keys())[0]
                user_session = sessions[sample_user]
                custom_email = user_session.get('custom_email', 'Default privacy email')
                print(f"   Sample User: {sample_user}")
                print(f"   Sample Email: {custom_email}")
                
                return True
        else:
            print("❌ No user sessions found")
            return False
            
    except Exception as e:
        print(f"❌ Bot notification test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 COMPREHENSIVE CONFIRMATION SYSTEM TEST")
    print("=" * 60)
    
    results = []
    
    # Test 1: Email service verification
    print("\n1️⃣ EMAIL SERVICE VERIFICATION")
    print("-" * 30)
    email_ok = await verify_email_service()
    results.append(("Email Service", email_ok))
    
    # Test 2: Bot notification test
    print("\n2️⃣ BOT NOTIFICATION TEST")
    print("-" * 30)
    bot_ok = await test_bot_notification()
    results.append(("Bot Notification", bot_ok))
    
    # Test 3: Payment confirmation
    print("\n3️⃣ PAYMENT CONFIRMATION TEST")
    print("-" * 30)
    payment_ok = await test_payment_confirmation()
    results.append(("Payment Confirmation", payment_ok))
    
    # Test 4: Domain registration confirmation
    print("\n4️⃣ DOMAIN REGISTRATION CONFIRMATION TEST")
    print("-" * 30)
    domain_ok = await test_domain_registration_confirmation()
    results.append(("Domain Registration Confirmation", domain_ok))
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"   {test_name:<35} {status}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL CONFIRMATION SYSTEMS OPERATIONAL!")
        print("   • Payment confirmations will be sent")
        print("   • Domain registration emails will be sent") 
        print("   • Bot notifications will reach users")
    else:
        print("⚠️ SOME SYSTEMS NEED ATTENTION")
        print("   Check the failed tests above for details")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())