#!/usr/bin/env python3
"""
Fix callback database queries by using direct SQL queries instead of ORM
"""

import os
import psycopg2
import logging

logger = logging.getLogger(__name__)

def get_order_payment_address_by_partial_id(partial_order_id, telegram_id):
    """
    Get payment address for order using direct SQL query
    """
    try:
        db_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Query for orders that start with the partial ID for this user
        query = """
            SELECT order_id, payment_address, crypto_currency 
            FROM orders 
            WHERE telegram_id = %s 
            AND order_id LIKE %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        cursor.execute(query, (telegram_id, f"{partial_order_id}%"))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            order_id, payment_address, crypto_currency = result
            logger.info(f"✅ Found order {order_id[:8]}... with address {payment_address[:20] if payment_address else 'Missing'}...")
            return {
                'order_id': order_id,
                'payment_address': payment_address,
                'crypto_currency': crypto_currency
            }
        else:
            logger.warning(f"❌ No order found for partial ID: {partial_order_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Database error getting payment address: {e}")
        return None

def get_order_details_for_switch(partial_order_id, telegram_id):
    """
    Get order details for switching payment method
    """
    try:
        db_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Query for order details
        query = """
            SELECT order_id, service_details, amount_usd, payment_status
            FROM orders 
            WHERE telegram_id = %s 
            AND order_id LIKE %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        cursor.execute(query, (telegram_id, f"{partial_order_id}%"))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            order_id, service_details, amount, payment_status = result
            logger.info(f"✅ Found order {order_id[:8]}... for switch: ${amount} {payment_status}")
            return {
                'order_id': order_id,
                'service_details': service_details,
                'amount_usd': float(amount) if amount else 0.0,
                'payment_status': payment_status
            }
        else:
            logger.warning(f"❌ No order found for switching: {partial_order_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Database error getting order for switch: {e}")
        return None

def test_callback_database_fixes():
    """
    Test the direct database queries
    """
    print("🔧 TESTING CALLBACK DATABASE FIXES")
    print("=" * 50)
    
    telegram_id = 5590563715
    test_order_ids = ["86acda5f", "c693ac04", "6416829b", "84178e26"]
    
    for order_id in test_order_ids:
        print(f"\n📋 Testing copy address for: {order_id}")
        result = get_order_payment_address_by_partial_id(order_id, telegram_id)
        if result:
            print(f"   ✅ Address: {result['payment_address']}")
            print(f"   ✅ Crypto: {result['crypto_currency']}")
        else:
            print(f"   ❌ No address found")
            
        print(f"\n🔄 Testing switch payment for: {order_id}")
        result = get_order_details_for_switch(order_id, telegram_id)
        if result:
            print(f"   ✅ Amount: ${result['amount_usd']}")
            print(f"   ✅ Status: {result['payment_status']}")
        else:
            print(f"   ❌ No order details found")
    
    print("\n" + "=" * 50)
    print("🏁 TESTING COMPLETE")

if __name__ == "__main__":
    test_callback_database_fixes()