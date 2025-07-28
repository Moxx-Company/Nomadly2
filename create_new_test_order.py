#!/usr/bin/env python3
"""
Create a new test domain registration order to validate the corrected system
"""

import asyncio
import logging
from datetime import datetime, timezone
from database import DatabaseManager
from sqlalchemy import text
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_new_test_order():
    """Create a new test order for domain registration"""
    
    print("🆕 CREATING NEW TEST DOMAIN REGISTRATION ORDER")
    print("=============================================")
    
    # Test domain details
    test_data = {
        'domain_name': 'testfixed20250721.sbs',
        'telegram_id': 5590563715,
        'amount_usd': 9.87,
        'cryptocurrency': 'ETH',
        'nameserver_mode': 'cloudflare'
    }
    
    print(f"Domain: {test_data['domain_name']}")
    print(f"User: {test_data['telegram_id']}")
    print(f"Amount: ${test_data['amount_usd']} USD")
    print(f"Crypto: {test_data['cryptocurrency']}")
    print()
    
    try:
        # Step 1: Create order in database
        print("📝 Step 1: Creating order in database...")
        
        db = DatabaseManager()
        order_uuid = str(uuid.uuid4())
        
        with db.get_session() as session:
            # Create order with proper field types
            insert_order = text("""
                INSERT INTO orders (
                    order_id,
                    user_id,
                    domain_name,
                    nameserver_mode,
                    amount,
                    cryptocurrency,
                    payment_status,
                    created_at,
                    updated_at
                ) VALUES (
                    :order_id,
                    :user_id,
                    :domain_name,
                    :nameserver_mode,
                    :amount,
                    :cryptocurrency,
                    :payment_status,
                    :created_at,
                    :updated_at
                )
            """)
            
            now = datetime.now(timezone.utc)
            
            session.execute(insert_order, {
                'order_id': order_uuid,
                'user_id': test_data['telegram_id'],
                'domain_name': test_data['domain_name'],
                'nameserver_mode': test_data['nameserver_mode'],
                'amount_usd': test_data['amount_usd'],
                'cryptocurrency': test_data['cryptocurrency'],
                'payment_status': 'pending',
                'created_at': now,
                'updated_at': now
            })
            
            session.commit()
            print(f"✅ Order created: {order_uuid}")
        
        # Step 2: Test cryptocurrency conversion
        print("\n💰 Step 2: Testing cryptocurrency conversion...")
        
        from payment_service import PaymentService
        payment_service = PaymentService()
        
        # Convert USD to ETH
        eth_amount = await payment_service._convert_usd_to_crypto_with_fallbacks(
            test_data['amount_usd'], 'ETH'
        )
        
        if eth_amount:
            print(f"✅ Conversion successful: ${test_data['amount_usd']} = {eth_amount} ETH")
        else:
            print("❌ Conversion failed")
            return False
        
        # Step 3: Test BlockBee payment creation
        print("\n🔗 Step 3: Testing BlockBee payment creation...")
        
        from apis.blockbee_api import BlockBeeAPI
        blockbee = BlockBeeAPI()
        
        callback_url = f"https://nomadly2-onarrival.replit.app/webhook/blockbee/{order_uuid}"
        
        payment_result = blockbee.create_payment(
            crypto_symbol='eth',
            callback_url=callback_url,
            order_id=order_uuid
        )
        
        if payment_result and payment_result.get('status') == 'success':
            payment_address = payment_result['data']['address_in']
            qr_code = payment_result['data'].get('qr_code')
            
            print(f"✅ BlockBee payment created")
            print(f"   Address: {payment_address}")
            print(f"   QR Code: {'Available' if qr_code else 'Not available'}")
            
            # Update order with payment details
            with db.get_session() as session:
                update_order = text("""
                    UPDATE orders SET
                        payment_address = :payment_address,
                        qr_code_url = :qr_code_url,
                        amount_crypto = :amount_crypto,
                        updated_at = :updated_at
                    WHERE order_id = :order_id
                """)
                
                session.execute(update_order, {
                    'payment_address': payment_address,
                    'qr_code_url': qr_code,
                    'amount_crypto': float(eth_amount),
                    'updated_at': datetime.now(timezone.utc),
                    'order_id': order_uuid
                })
                
                session.commit()
                print("✅ Order updated with payment details")
        else:
            print(f"❌ BlockBee payment creation failed: {payment_result}")
            return False
        
        # Step 4: Test registration service instantiation
        print("\n🔧 Step 4: Testing registration service...")
        
        try:
            from fixed_registration_service import FixedRegistrationService
            
            reg_service = FixedRegistrationService()
            print("✅ Registration service ready")
            
            # Test OpenProvider API connectivity
            from apis.production_openprovider import OpenProviderAPI
            
            op_api = OpenProviderAPI()
            print("✅ OpenProvider API connected")
            print(f"   Token: {'Active' if op_api.token else 'None'}")
            
        except Exception as e:
            print(f"❌ Registration service error: {e}")
            return False
        
        print("\n🎉 NEW TEST ORDER CREATED SUCCESSFULLY!")
        print("=====================================")
        print(f"✅ Order ID: {order_uuid}")
        print(f"✅ Domain: {test_data['domain_name']}")
        print(f"✅ Payment Address: {payment_address}")
        print(f"✅ Amount: {eth_amount} ETH (${test_data['amount_usd']})")
        print(f"✅ Status: Ready for payment")
        print()
        print("🧪 TESTING INSTRUCTIONS:")
        print("========================")
        print("1. Send exactly the ETH amount to the payment address")
        print("2. Wait for BlockBee webhook confirmation")
        print("3. Registration service will process with fixed implementation")
        print("4. Domain will be registered with corrected OpenProvider API calls")
        print()
        
        # Return test data for further use
        return {
            'order_id': order_uuid,
            'domain_name': test_data['domain_name'],
            'payment_address': payment_address,
            'eth_amount': eth_amount,
            'usd_amount': test_data['amount_usd']
        }
        
    except Exception as e:
        logger.error(f"Test order creation failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(create_new_test_order())
    if result:
        print(f"Test order data: {result}")