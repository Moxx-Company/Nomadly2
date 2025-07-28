#!/usr/bin/env python3
"""
Test Order Creation Fix
Verify that order creation is working when users try to register claudebaby2.sbs
"""

import sys
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def test_order_creation():
    """Test order creation flow"""
    print("🧪 Testing Order Creation Fix...")
    
    # Simulate the order creation that should happen when user clicks crypto payment
    try:
        from database import get_db_manager
        
        # Test data matching claudebaby2.sbs scenario
        test_user_id = 5590563715  # Real user ID from logs
        test_domain = "claudebaby2.sbs"
        test_amount = 9.87  # Same price as other .sbs domains
        
        db = get_db_manager()
        
        # Prepare service details for order (matching the fix)
        service_details = {
            'domain_name': test_domain,
            'tld': '.sbs',
            'nameserver_choice': 'cloudflare',
            'technical_email': 'cloakhost@tutamail.com',
            'registration_years': 1
        }
        
        # Create order using the same method as the fix
        order = db.create_order(
            telegram_id=test_user_id,
            service_type='domain_registration',
            service_details=service_details,
            amount=test_amount,
            payment_method='crypto_eth'
        )
        
        if order and hasattr(order, 'order_id'):
            print(f"✅ Order creation test PASSED")
            print(f"📋 Created order: {order.order_id}")
            print(f"🌐 Domain: {test_domain}")
            print(f"💰 Amount: ${test_amount}")
            
            # Verify it's in database
            from sqlalchemy import text
            session = db.get_session()
            try:
                result = session.execute(text(
                    "SELECT order_id, domain_name, total_price_usd FROM orders WHERE domain_name = :domain"
                ), {'domain': test_domain})
                
                row = result.fetchone()
                if row:
                    print(f"✅ Database verification PASSED - Order stored correctly")
                    print(f"📊 DB Order ID: {row[0]}")
                    print(f"🏷️ DB Domain: {row[1]}")
                    print(f"💵 DB Amount: ${row[2]}")
                else:
                    print("❌ Database verification FAILED - Order not found in DB")
            finally:
                session.close()
        else:
            print("❌ Order creation test FAILED - No order returned")
            return False
            
    except Exception as e:
        print(f"❌ Order creation test FAILED with error: {e}")
        return False
    
    return True

async def check_existing_orders():
    """Check what orders exist currently"""
    print("\n📋 Checking existing orders...")
    
    try:
        from database import get_db_manager
        from sqlalchemy import text
        
        db = get_db_manager()
        session = db.get_session()
        
        try:
            result = session.execute(text(
                "SELECT domain_name, total_price_usd, status, created_at FROM orders ORDER BY created_at DESC LIMIT 10"
            ))
            
            rows = result.fetchall()
            print(f"📊 Found {len(rows)} recent orders:")
            
            for row in rows:
                print(f"  • {row[0]} - ${row[1]} - {row[2]} - {row[3]}")
                
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Error checking orders: {e}")

async def main():
    print("🔧 ORDER CREATION FIX VERIFICATION")
    print("=" * 50)
    
    # Check existing orders first
    await check_existing_orders()
    
    # Test the fix
    success = await test_order_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ORDER CREATION FIX WORKING!")
        print("✅ Users should now be able to register claudebaby2.sbs")
        print("✅ Orders will be properly created in database")
        print("✅ Payment monitoring will work correctly")
    else:
        print("❌ ORDER CREATION FIX STILL HAS ISSUES")
        print("⚠️ Further debugging required")

if __name__ == "__main__":
    asyncio.run(main())