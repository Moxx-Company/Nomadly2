#!/usr/bin/env python3
"""
Test Email Notification System
Send test payment confirmation email for order 54e8307f-758f-4133-9a86-ec3e3788ec06
"""

import sys
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def test_email_notification():
    """Test email notification system directly"""
    
    print("🧪 TESTING EMAIL NOTIFICATION SYSTEM")
    print("=" * 45)
    
    try:
        from services.confirmation_service import ConfirmationService
        from database import get_db_manager
        
        # Create confirmation service
        confirmation_service = ConfirmationService()
        
        print(f"📧 Email service configured: {confirmation_service.is_configured()}")
        print(f"📋 API Key available: {bool(confirmation_service.brevo_api_key)}")
        print(f"📋 SMTP Key available: {bool(confirmation_service.brevo_smtp_key)}")
        print(f"📋 From email: {confirmation_service.from_email}")
        
        # Get order details
        db_manager = get_db_manager()
        order = db_manager.get_order("54e8307f-758f-4133-9a86-ec3e3788ec06")
        
        if not order:
            print("❌ Order not found")
            return
            
        print(f"✅ Order found: {order.order_id}")
        print(f"👤 User ID: {order.telegram_id}")
        print(f"💰 Amount: ${order.amount}")
        
        # Prepare order data for email
        order_data = {
            "order_id": order.order_id,
            "amount_usd": order.amount,
            "payment_method": "Ethereum (ETH)",
            "service_type": order.service_type,
            "transaction_id": "0x4716323e15bfd4e836b4ce0537fff8a52ddebc022cbd5ed5da391e5bf23a0e91",
            "domain_name": order.service_details.get("domain_name", "ehobalpbwg.sbs") if hasattr(order, 'service_details') and order.service_details else "ehobalpbwg.sbs",
            "contact_email": "onarrival21@gmail.com"
        }
        
        print(f"\n📧 SENDING TEST EMAIL NOTIFICATION")
        print(f"   To: onarrival21@gmail.com")
        print(f"   Domain: {order_data['domain_name']}")
        print(f"   Transaction: {order_data['transaction_id'][:20]}...")
        
        # Send payment confirmation email
        success = await confirmation_service.send_payment_confirmation(
            order.telegram_id, order_data
        )
        
        if success:
            print(f"✅ EMAIL NOTIFICATION SENT SUCCESSFULLY")
        else:
            print(f"❌ EMAIL NOTIFICATION FAILED")
            
        return success
        
    except Exception as e:
        print(f"❌ Email test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_email_notification())
    if result:
        print(f"\n🎉 EMAIL NOTIFICATION TEST PASSED")
    else:
        print(f"\n💥 EMAIL NOTIFICATION TEST FAILED")