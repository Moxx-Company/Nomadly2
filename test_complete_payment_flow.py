#!/usr/bin/env python3
"""
Test the complete payment flow end-to-end to verify fixes
"""

import os
import sys
import logging
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_complete_payment_workflow():
    """Test the complete payment workflow including order creation and BlockBee integration"""
    print("🚀 Testing Complete Payment Workflow")
    print("=" * 60)
    
    # Step 1: Test database connection and order creation
    print("\n📊 Step 1: Testing Database Order Creation...")
    try:
        from database import get_db_manager
        from sqlalchemy import text
        
        db = get_db_manager()
        
        # Use existing user ID from database
        test_user_id = 5590563715  # Your user ID
        test_domain = "test-payment-fix.sbs"
        test_amount = 9.87
        
        service_details = {
            'domain_name': test_domain,
            'tld': 'sbs',
            'nameserver_choice': 'cloudflare',
            'technical_email': 'test@example.com',
            'registration_years': 1
        }
        
        order = db.create_order(
            telegram_id=test_user_id,
            service_type='domain_registration', 
            service_details=service_details,
            amount=test_amount,
            payment_method='crypto_eth'
        )
        
        if order and hasattr(order, 'order_id'):
            print(f"   ✅ Order created successfully: {order.order_id}")
            test_order_id = order.order_id
        else:
            print(f"   ❌ Order creation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    # Step 2: Test BlockBee payment address generation
    print("\n💳 Step 2: Testing BlockBee Payment Address Generation...")
    try:
        from apis.blockbee import BlockBeeAPI
        
        api_key = os.getenv('BLOCKBEE_API_KEY')
        if not api_key:
            print("   ❌ BLOCKBEE_API_KEY not found")
            return False
            
        blockbee = BlockBeeAPI(api_key)
        
        # Create callback URL like the bot does
        callback_url = f"https://nomadly2-onarrival.replit.app/webhook/blockbee/{test_order_id}"
        
        address_response = blockbee.create_payment_address(
            cryptocurrency='eth',
            callback_url=callback_url,
            amount=test_amount
        )
        
        if address_response.get('status') == 'success' and address_response.get('address_in'):
            payment_address = address_response['address_in']
            print(f"   ✅ Payment address generated: {payment_address}")
        else:
            print(f"   ❌ Payment address generation failed: {address_response}")
            return False
            
    except Exception as e:
        print(f"   ❌ BlockBee error: {e}")
        return False
    
    # Step 3: Test database update with payment address
    print("\n💾 Step 3: Testing Database Payment Address Update...")
    try:
        with db.get_session() as db_session:
            update_query = text("""
                UPDATE orders SET 
                    crypto_address = :crypto_address,
                    crypto_currency = :crypto_currency
                WHERE order_id = :order_id AND telegram_id = :telegram_id
            """)
            db_session.execute(update_query, {
                'crypto_address': payment_address,
                'crypto_currency': 'eth',
                'order_id': test_order_id,
                'telegram_id': test_user_id
            })
            db_session.commit()
            print(f"   ✅ Order updated with payment address")
            
    except Exception as e:
        print(f"   ❌ Database update error: {e}")
        return False
    
    # Step 4: Verify the complete order in database
    print("\n🔍 Step 4: Verifying Complete Order in Database...")
    try:
        with db.get_session() as db_session:
            verify_query = text("""
                SELECT order_id, domain_name, total_price_usd, crypto_address, crypto_currency, status
                FROM orders 
                WHERE order_id = :order_id AND telegram_id = :telegram_id
            """)
            result = db_session.execute(verify_query, {
                'order_id': test_order_id,
                'telegram_id': test_user_id
            }).fetchone()
            
            if result:
                print(f"   ✅ Order verification successful:")
                print(f"      Order ID: {result[0]}")
                print(f"      Domain: {result[1]}")
                print(f"      Amount: ${result[2]}")
                print(f"      Payment Address: {result[3]}")
                print(f"      Crypto Currency: {result[4]}")
                print(f"      Status: {result[5]}")
            else:
                print(f"   ❌ Order not found in database")
                return False
                
    except Exception as e:
        print(f"   ❌ Database verification error: {e}")
        return False
    
    # Step 5: Clean up test data
    print("\n🧹 Step 5: Cleaning Up Test Data...")
    try:
        with db.get_session() as db_session:
            cleanup_query = text("DELETE FROM orders WHERE telegram_id = :telegram_id")
            db_session.execute(cleanup_query, {'telegram_id': test_user_id})
            db_session.commit()
            print(f"   ✅ Test data cleaned up")
            
    except Exception as e:
        print(f"   ⚠️ Cleanup warning: {e}")
    
    return True

if __name__ == "__main__":
    print("🧪 COMPLETE PAYMENT FLOW TEST")
    print("=" * 50)
    
    success = test_complete_payment_workflow()
    
    print("\n📊 TEST RESULTS:")
    print("=" * 30)
    
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Order creation working")
        print("✅ BlockBee API integration working") 
        print("✅ Payment address generation working")
        print("✅ Database updates working")
        print("✅ Complete payment workflow operational")
        print("\n💡 Your transaction failures should now be resolved!")
    else:
        print("❌ TESTS FAILED!")
        print("⚠️ Payment workflow still has issues that need attention")