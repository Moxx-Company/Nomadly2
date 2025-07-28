#!/usr/bin/env python3
"""
Test Email Notification System for Nomadly
Tests all three email notification types:
1. Welcome email when payment is received
2. Payment confirmation email
3. Domain registration complete email
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_email_notifications():
    """Test all email notification types"""
    
    print("🧪 Testing Nomadly Email Notification System")
    print("=" * 50)
    
    # Import the email service
    from services.brevo_email_service import get_email_service
    email_service = get_email_service()
    
    # Test email address
    test_email = "test@example.com"  # Change this to your test email
    test_domain = "example.com"
    test_order_id = "ORD-TEST1"
    
    print(f"\n📧 Testing emails will be sent to: {test_email}")
    print("Note: Emails are only sent for custom emails, not cloakhost@tutamail.com")
    
    # Test 1: Welcome Email
    print("\n1️⃣ Testing Welcome Email...")
    try:
        result = await email_service.send_welcome_email(
            email=test_email,
            domain=test_domain,
            order_id=test_order_id
        )
        if result.get('success'):
            print("✅ Welcome email sent successfully!")
            print(f"   Message ID: {result.get('message_id')}")
        else:
            print(f"❌ Welcome email failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Welcome email error: {e}")
    
    # Test 2: Payment Confirmation Email
    print("\n2️⃣ Testing Payment Confirmation Email...")
    try:
        result = await email_service.send_payment_confirmation_email(
            email=test_email,
            domain=test_domain,
            order_id=test_order_id,
            amount=49.50,
            crypto_type="btc",
            crypto_amount=0.00074
        )
        if result.get('success'):
            print("✅ Payment confirmation email sent successfully!")
            print(f"   Message ID: {result.get('message_id')}")
        else:
            print(f"❌ Payment confirmation email failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Payment confirmation email error: {e}")
    
    # Test 3: Domain Registration Complete Email
    print("\n3️⃣ Testing Domain Registration Complete Email...")
    try:
        result = await email_service.send_registration_complete_email(
            email=test_email,
            domain=test_domain,
            order_id=test_order_id,
            nameservers=["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"],
            expiry_date="July 24, 2026"
        )
        if result.get('success'):
            print("✅ Registration complete email sent successfully!")
            print(f"   Message ID: {result.get('message_id')}")
        else:
            print(f"❌ Registration complete email failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Registration complete email error: {e}")
    
    print("\n" + "=" * 50)
    print("📧 Email notification tests completed!")
    print("\nNote: Check your email inbox for the test emails.")
    print("If emails are not received, check:")
    print("1. BREVO_API_KEY is configured correctly")
    print("2. Email address is valid")
    print("3. Check spam/junk folder")
    print("4. Brevo account is active and has sending credits")

async def test_integration_flow():
    """Test the complete integration flow"""
    print("\n\n🔄 Testing Complete Integration Flow")
    print("=" * 50)
    
    # Test the confirmation service integration
    from services.confirmation_service import get_confirmation_service
    confirmation_service = get_confirmation_service()
    
    print("\n📧 Testing Confirmation Service Integration...")
    
    # Test payment confirmation through confirmation service
    order_data = {
        "order_id": "ORD-FLOW1",
        "domain_name": "testflow.com",
        "amount": 49.50,
        "amount_usd": 49.50,
        "payment_method": "btc",
        "crypto_amount": 0.00074,
        "contact_email": "test@example.com",  # Change this to your test email
        "technical_email": "test@example.com"
    }
    
    print(f"\n💳 Testing payment confirmation for order {order_data['order_id']}...")
    try:
        # Mock telegram ID for testing
        telegram_id = 123456789
        result = await confirmation_service.send_payment_confirmation(telegram_id, order_data)
        if result:
            print("✅ Payment confirmation sent via confirmation service!")
        else:
            print("❌ Payment confirmation failed via confirmation service")
    except Exception as e:
        print(f"❌ Confirmation service error: {e}")
    
    # Test domain registration confirmation
    domain_data = {
        "order_id": "ORD-FLOW1",
        "domain_name": "testflow.com",
        "nameservers": ["ns1.cloudflare.com", "ns2.cloudflare.com"],
        "expiry_date": "July 24, 2026",
        "registration_status": "Active",
        "contact_email": "test@example.com",
        "technical_email": "test@example.com"
    }
    
    print(f"\n🌐 Testing domain registration confirmation...")
    try:
        result = await confirmation_service.send_domain_registration_confirmation(telegram_id, domain_data)
        if result:
            print("✅ Domain registration confirmation sent via confirmation service!")
        else:
            print("❌ Domain registration confirmation failed via confirmation service")
    except Exception as e:
        print(f"❌ Confirmation service error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Integration flow tests completed!")

async def main():
    """Run all tests"""
    # Test direct email service
    await test_email_notifications()
    
    # Test integration with confirmation service
    await test_integration_flow()

if __name__ == "__main__":
    asyncio.run(main())