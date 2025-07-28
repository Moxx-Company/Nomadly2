#!/usr/bin/env python3
"""
Debug script to identify callback handling errors
"""

import logging
from database_manager import get_db_manager
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_copy_address_error():
    """Debug copy address functionality"""
    print("🔍 DEBUGGING COPY ADDRESS ERROR")
    print("=" * 50)
    
    db_manager = get_db_manager()
    
    # Get recent orders
    try:
        # Get all orders from user 5590563715
        user_id = 5590563715
        user_orders = db_manager.get_user_orders(user_id)
        
        print(f"📊 Found {len(user_orders)} orders for user {user_id}")
        
        for i, order in enumerate(user_orders[:5]):  # Show first 5 orders
            print(f"\n📋 Order {i+1}:")
            print(f"   ID: {getattr(order, 'order_id', 'No ID')}")
            print(f"   Status: {getattr(order, 'payment_status', 'No Status')}")
            print(f"   Amount: ${getattr(order, 'amount_usd', 0.00):.2f}")
            print(f"   Service: {getattr(order, 'service_details', 'No Service')}")
            
            # Check for payment address
            payment_address = getattr(order, 'payment_address', None)
            crypto_currency = getattr(order, 'crypto_currency', None)
            
            print(f"   Payment Address: {payment_address or 'MISSING'}")
            print(f"   Crypto Currency: {crypto_currency or 'MISSING'}")
            
            if payment_address:
                print(f"   ✅ Address Available for Copy")
            else:
                print(f"   ❌ NO ADDRESS - This would cause copy error")
                
    except Exception as e:
        print(f"❌ Database Error: {e}")

def debug_switch_payment_error():
    """Debug switch payment functionality"""
    print("\n🔄 DEBUGGING SWITCH PAYMENT ERROR")
    print("=" * 50)
    
    # Test order lookup logic
    test_order_ids = ["86acda5f", "c693ac04", "6416829b", "84178e26"]
    
    db_manager = get_db_manager()
    user_id = 5590563715
    
    for order_id in test_order_ids:
        print(f"\n🔍 Testing order lookup: {order_id}")
        
        # Try direct lookup
        try:
            order = db_manager.get_order(order_id)
            if order:
                print(f"   ✅ Direct lookup SUCCESS")
                print(f"   Amount: ${getattr(order, 'amount_usd', 0.00):.2f}")
                print(f"   Status: {getattr(order, 'payment_status', 'Unknown')}")
            else:
                print(f"   ❌ Direct lookup FAILED - order not found")
        except Exception as e:
            print(f"   ❌ Direct lookup ERROR: {e}")
            
        # Try partial match (8 chars)
        if len(order_id) == 8:
            try:
                user_orders = db_manager.get_user_orders(user_id)
                found = False
                for o in user_orders:
                    if hasattr(o, "order_id") and str(o.order_id).startswith(order_id):
                        found = True
                        print(f"   ✅ Partial match SUCCESS: {str(o.order_id)}")
                        break
                
                if not found:
                    print(f"   ❌ Partial match FAILED - no matching order")
                    
            except Exception as e:
                print(f"   ❌ Partial match ERROR: {e}")

def main():
    """Run all debug checks"""
    print(f"🚀 CALLBACK ERROR DIAGNOSTICS - {datetime.now()}")
    print("=" * 60)
    
    debug_copy_address_error()
    debug_switch_payment_error()
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNOSTICS COMPLETE")

if __name__ == "__main__":
    main()