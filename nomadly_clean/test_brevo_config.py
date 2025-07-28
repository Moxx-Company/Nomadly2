#!/usr/bin/env python3
"""
Test Brevo Email Configuration
==============================
Verify that Brevo is properly configured with noreply@cloakhost.ru
"""

import sys
sys.path.append('.')

from utils.brevo_email_service import brevo_service

def test_brevo_configuration():
    """Test Brevo email service configuration"""
    
    print("🔍 Testing Brevo Configuration")
    print("=" * 50)
    
    # Check configuration status
    print(f"✅ Brevo Service Configured: {brevo_service.is_configured}")
    print(f"📧 Sender Email: {brevo_service.sender_email}")
    print(f"🔑 API Key Present: {bool(brevo_service.api_key)}")
    print(f"🔐 SMTP Key Present: {bool(brevo_service.smtp_key)}")
    print()
    
    # Test connection
    print("🌐 Testing Connection...")
    test_result = brevo_service.test_connection()
    print(f"📊 Connection Status: {test_result['status']}")
    print(f"📝 Message: {test_result['message']}")
    print(f"🌍 API Available: {test_result['api_available']}")
    print(f"📬 SMTP Available: {test_result['smtp_available']}")
    print()
    
    # Verify sender email
    expected_email = "noreply@cloakhost.ru"
    if brevo_service.sender_email == expected_email:
        print(f"✅ Sender Email Correct: {brevo_service.sender_email}")
    else:
        print(f"❌ Sender Email Incorrect!")
        print(f"   Expected: {expected_email}")
        print(f"   Current: {brevo_service.sender_email}")
        return False
    
    # Check if ready for production
    if brevo_service.is_configured and test_result['api_available']:
        print("\n🚀 Brevo is properly configured and ready for production!")
        print("📧 Email service will use Brevo API for sending emails")
        return True
    else:
        print("\n⚠️ Brevo needs additional configuration")
        if not brevo_service.is_configured:
            print("   - Missing API keys")
        if not test_result['api_available']:
            print("   - API connection failed")
        return False

if __name__ == "__main__":
    success = test_brevo_configuration()
    sys.exit(0 if success else 1)