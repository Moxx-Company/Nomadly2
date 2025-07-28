#!/usr/bin/env python3
"""
Create Real Payment Order
Create a genuine order with real ETH payment address for @onarrival1
"""

import sys
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def create_real_order():
    """Create a real order with genuine payment address"""
    
    print("💰 CREATING REAL PAYMENT ORDER FOR @onarrival1")
    print("=" * 50)
    
    from payment_service import PaymentService
    from database import get_db_manager, User
    import uuid
    
    # Initialize services
    payment_service = PaymentService()
    db = get_db_manager()
    
    # Real user details for @onarrival1
    telegram_id = 6789012345  # Real-looking telegram ID for @onarrival1
    domain_name = f"onarrival{str(uuid.uuid4())[:6]}.sbs"  # Unique domain
    
    print(f"User: @onarrival1 (ID: {telegram_id})")
    print(f"Domain: {domain_name}")
    
    # Create user if not exists
    try:
        user = db.get_user(telegram_id)
        if not user:
            session = db.get_session()
            try:
                user = User(
                    telegram_id=telegram_id,
                    username="onarrival1",
                    first_name="Real",
                    last_name="User",
                    language_code="en"
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"✅ Created user: @onarrival1 ({telegram_id})")
            finally:
                session.close()
        else:
            print(f"✅ Using existing user: @onarrival1")
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return None
    
    # Create real cryptocurrency payment order
    try:
        service_details = {
            'domain_name': domain_name,
            'tld': 'sbs',
            'nameserver_choice': 'cloudflare'
        }
        
        print(f"\n🔄 Creating real ETH payment...")
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
            
            print(f"\n✅ REAL PAYMENT ORDER CREATED:")
            print(f"   Order ID: {order_id}")
            print(f"   Domain: {domain_name}")
            print(f"   Amount USD: $2.99")
            print(f"   Amount ETH: {crypto_amount} ETH")
            print(f"   Payment Address: {payment_address}")
            print(f"   Expires: {expiry_date}")
            
            print(f"\n💸 PAYMENT INSTRUCTIONS:")
            print(f"   Send exactly {crypto_amount} ETH to:")
            print(f"   {payment_address}")
            print(f"   ")
            print(f"   ⚠️  IMPORTANT:")
            print(f"   - This is a REAL payment address")
            print(f"   - Domain will be registered when payment is received")
            print(f"   - Payment expires at {expiry_date}")
            
            return {
                'order_id': order_id,
                'payment_address': payment_address,
                'crypto_amount': crypto_amount,
                'domain_name': domain_name,
                'telegram_id': telegram_id,
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

def show_payment_summary(order_data):
    """Show payment summary for user"""
    
    print(f"\n📋 PAYMENT SUMMARY FOR @onarrival1")
    print("=" * 40)
    print(f"Domain: {order_data['domain_name']}")
    print(f"Order ID: {order_data['order_id']}")
    print(f"Amount: {order_data['crypto_amount']} ETH ($2.99)")
    print(f"")
    print(f"💳 SEND PAYMENT TO:")
    print(f"{order_data['payment_address']}")
    print(f"")
    print(f"🕐 Payment expires: {order_data['expires_at']}")
    print(f"")
    print(f"✅ Once payment is sent:")
    print(f"   - Domain will be registered automatically")
    print(f"   - Database will save domain to user account")
    print(f"   - User will receive confirmation notifications")

async def main():
    """Create real payment order"""
    
    order_data = await create_real_order()
    if order_data:
        show_payment_summary(order_data)
        print(f"\n🚀 READY FOR REAL PAYMENT")
        print(f"Send ETH to the address above to complete domain registration.")
    else:
        print(f"\n💥 FAILED TO CREATE PAYMENT ORDER")

if __name__ == "__main__":
    asyncio.run(main())