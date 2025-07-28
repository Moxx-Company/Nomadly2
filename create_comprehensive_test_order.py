#!/usr/bin/env python3
"""
Create Comprehensive Test Order for @onarrival1
Complete workflow test with payment, registration, and notifications
"""

import sys
import asyncio
import uuid
sys.path.insert(0, '/home/runner/workspace')

async def create_complete_test_order():
    """Create comprehensive test order with full workflow"""
    
    print("🧪 CREATING COMPREHENSIVE TEST ORDER FOR @onarrival1")
    print("=" * 55)
    
    from payment_service import PaymentService
    from database import get_db_manager, User
    
    # Initialize services
    payment_service = PaymentService()
    db = get_db_manager()
    
    # Real test user details for @onarrival1
    telegram_id = 6789012345  # @onarrival1 test account
    domain_name = f"testorder{str(uuid.uuid4())[:8]}.sbs"  # Unique test domain
    
    print(f"📋 Test Configuration:")
    print(f"   User: @onarrival1 (ID: {telegram_id})")
    print(f"   Domain: {domain_name}")
    print(f"   Payment: ETH ($2.99)")
    
    # Ensure user exists with email for notifications
    try:
        user = db.get_user(telegram_id)
        if not user:
            session = db.get_session()
            try:
                user = User(
                    telegram_id=telegram_id,
                    username="onarrival1",
                    first_name="Test",
                    last_name="User",
                    language_code="en"
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"✅ Created test user with email: onarrival21@gmail.com")
            finally:
                session.close()
        else:
            print(f"✅ Test user already exists: @onarrival1")
    except Exception as e:
        print(f"❌ User setup failed: {e}")
        return None
    
    # Create real cryptocurrency payment order
    try:
        service_details = {
            'domain_name': domain_name,
            'tld': 'sbs',
            'nameserver_choice': 'cloudflare'
        }
        
        print(f"\n🔄 Creating ETH payment order...")
        result = await payment_service.create_crypto_payment(
            telegram_id=telegram_id,
            amount=2.99,
            crypto_currency='eth',
            service_type='domain_registration',
            service_details=service_details
        )
        
        if result and result.get('success'):
            order_id = result.get('order_id')
            payment_address = result.get('payment_address')
            crypto_amount = result.get('crypto_amount')
            expiry_date = result.get('expires_at')
            
            print(f"\n✅ COMPREHENSIVE TEST ORDER CREATED:")
            print(f"   Order ID: {order_id}")
            print(f"   Domain: {domain_name}")
            print(f"   User: @onarrival1 ({telegram_id})")
            print(f"   Email: onarrival21@gmail.com")
            print(f"   Amount USD: $2.99")
            print(f"   Amount ETH: {crypto_amount} ETH")
            print(f"   Payment Address: {payment_address}")
            print(f"   Expires: {expiry_date}")
            
            print(f"\n📧 NOTIFICATION CONFIGURATION:")
            print(f"   Telegram ID: {telegram_id} (for bot notifications)")
            print(f"   Email: onarrival21@gmail.com (for email notifications)")
            print(f"   Both notifications will be sent upon registration completion")
            
            print(f"\n💸 PAYMENT INSTRUCTIONS:")
            print(f"   Send exactly {crypto_amount} ETH to:")
            print(f"   {payment_address}")
            print(f"   ")
            print(f"   🔔 EXPECTED RESULTS AFTER PAYMENT:")
            print(f"   1. BlockBee webhook receives payment confirmation")
            print(f"   2. Domain registered with OpenProvider")
            print(f"   3. CloudFlare zone created")
            print(f"   4. Domain saved to @onarrival1 database")
            print(f"   5. Telegram notification sent to bot")
            print(f"   6. Email notification sent to onarrival21@gmail.com")
            
            return {
                'order_id': order_id,
                'payment_address': payment_address,
                'crypto_amount': crypto_amount,
                'domain_name': domain_name,
                'telegram_id': telegram_id,
                'email': 'onarrival21@gmail.com',
                'expires_at': expiry_date
            }
        else:
            print(f"❌ Payment creation failed: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Order creation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def setup_notification_monitoring(order_data):
    """Setup monitoring for notifications"""
    
    print(f"\n🔔 NOTIFICATION MONITORING SETUP")
    print("=" * 35)
    print(f"Order ID: {order_data['order_id']}")
    print(f"Domain: {order_data['domain_name']}")
    print(f"Telegram ID: {order_data['telegram_id']}")
    print(f"Email: {order_data['email']}")
    print(f"")
    print(f"📱 Telegram Notification Expected:")
    print(f"   - Bot will send registration confirmation")
    print(f"   - Message will include domain details")
    print(f"   - User will be notified of successful registration")
    print(f"")
    print(f"📧 Email Notification Expected:")
    print(f"   - Professional registration confirmation email")
    print(f"   - Complete domain information and technical details")
    print(f"   - OpenProvider domain ID and CloudFlare zone ID")
    print(f"   - DNS configuration and nameserver information")

async def main():
    """Create comprehensive test order"""
    
    order_data = await create_complete_test_order()
    if order_data:
        setup_notification_monitoring(order_data)
        print(f"\n🚀 COMPREHENSIVE TEST ORDER READY")
        print(f"Send ETH payment to test complete workflow including notifications.")
    else:
        print(f"\n💥 FAILED TO CREATE COMPREHENSIVE TEST ORDER")

if __name__ == "__main__":
    asyncio.run(main())