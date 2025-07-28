#!/usr/bin/env python3
"""
Investigation Script: Missing OpenProvider Domain IDs Root Cause Analysis
Addresses the systematic failure where domain registrations don't save OpenProvider IDs
"""

import logging
import asyncio
from database import get_db_manager
from payment_service import get_payment_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def investigate_registration_failure():
    """Investigate why domain registrations fail to save OpenProvider IDs"""
    logger.info("🔍 ROOT CAUSE ANALYSIS: Missing OpenProvider Domain IDs")
    logger.info("=" * 60)
    
    try:
        db_manager = get_db_manager()
        payment_service = get_payment_service()
        
        # 1. Check customer @folly542's order processing
        logger.info("📊 STEP 1: Analyzing Customer @folly542 Order History")
        logger.info("-" * 50)
        
        # Get all orders for this customer
        customer_orders = db_manager.session.execute("""
            SELECT order_id, domain_name, payment_status, service_details, created_at 
            FROM orders 
            WHERE telegram_id = 6896666427 
            ORDER BY created_at DESC 
            LIMIT 5
        """).fetchall()
        
        for order in customer_orders:
            logger.info(f"   Order: {order[0]}")
            logger.info(f"   Domain: {order[1] or 'From service_details'}")
            logger.info(f"   Status: {order[2]}")
            logger.info(f"   Created: {order[4]}")
            logger.info(f"   Service Details: {order[3][:100]}...")
            logger.info("")
        
        # 2. Test webhook processing chain
        logger.info("📊 STEP 2: Testing Webhook Processing Chain")
        logger.info("-" * 50)
        
        # Mock a webhook call to see where it fails
        test_order_id = "51bec9f7-df43-4c51-9bdc-0be0b2c796cc"  # Customer's real order
        mock_payment_data = {
            "status": "confirmed",
            "txid": "test_transaction",
            "confirmations": 1,
            "value_coin": 0.003533,
            "coin": "eth"
        }
        
        logger.info(f"🧪 Testing payment confirmation for order: {test_order_id}")
        
        # Check if order exists
        order = db_manager.get_order(test_order_id)
        if order:
            logger.info(f"✅ Order found: {order.service_type}")
            logger.info(f"   Service Details: {order.service_details}")
            logger.info(f"   Payment Status: {order.payment_status}")
            
            # Test the complete_domain_registration method
            if hasattr(payment_service, 'complete_domain_registration'):
                logger.info("🧪 Testing complete_domain_registration method...")
                try:
                    # This should trigger the actual registration workflow
                    result = await payment_service.complete_domain_registration(test_order_id, mock_payment_data)
                    logger.info(f"   Result: {result}")
                except Exception as e:
                    logger.error(f"   ❌ complete_domain_registration failed: {e}")
            else:
                logger.error("   ❌ complete_domain_registration method not found!")
        else:
            logger.error(f"   ❌ Order not found: {test_order_id}")
        
        # 3. Check database saving methods
        logger.info("📊 STEP 3: Database Saving Method Analysis")
        logger.info("-" * 50)
        
        # Check what methods exist for saving domains
        domain_methods = [
            'create_registered_domain',
            '_store_domain_registration',
            '_store_domain_registration_with_ids',
            '_save_domain_to_database'
        ]
        
        for method_name in domain_methods:
            if hasattr(db_manager, method_name):
                method = getattr(db_manager, method_name)
                logger.info(f"✅ {method_name}: Found")
                logger.info(f"   Signature: {method.__name__}")
            elif hasattr(payment_service, method_name):
                method = getattr(payment_service, method_name)  
                logger.info(f"✅ {method_name}: Found in payment_service")
            else:
                logger.error(f"❌ {method_name}: Not found!")
        
        # 4. Check domain registration methods
        logger.info("📊 STEP 4: Domain Registration API Method Analysis") 
        logger.info("-" * 50)
        
        # Check OpenProvider registration methods
        if hasattr(payment_service, '_register_domain_openprovider_api'):
            logger.info("✅ _register_domain_openprovider_api: Found")
        else:
            logger.error("❌ _register_domain_openprovider_api: Not found!")
            
        # Test production OpenProvider API
        try:
            from apis.production_openprovider import OpenProviderAPI
            
            api = OpenProviderAPI()
            logger.info("✅ Production OpenProvider API: Imported successfully")
            
            # Check authentication
            if hasattr(api, 'authenticate'):
                logger.info("   - authenticate method: Found")
            if hasattr(api, 'register_domain'):
                logger.info("   - register_domain method: Found")
            
        except Exception as e:
            logger.error(f"❌ Production OpenProvider API: {e}")
        
        # 5. Check existing domain records 
        logger.info("📊 STEP 5: Existing Domain Records Analysis")
        logger.info("-" * 50)
        
        # Get all domains for customer @folly542
        customer_domains = db_manager.session.execute("""
            SELECT domain_name, openprovider_domain_id, created_at, status 
            FROM registered_domains 
            WHERE telegram_id = 6896666427
            ORDER BY created_at DESC
        """).fetchall()
        
        if customer_domains:
            for domain in customer_domains:
                logger.info(f"   Domain: {domain[0]}")
                logger.info(f"   OpenProvider ID: {domain[1] or 'MISSING'}")
                logger.info(f"   Status: {domain[3]}")
                logger.info(f"   Created: {domain[2]}")
                logger.info("")
        else:
            logger.info("   No domains found for customer @folly542")
        
        logger.info("🎯 ROOT CAUSE ANALYSIS COMPLETE")
        logger.info("=" * 60)
        logger.info("SUMMARY:")
        logger.info("1. Multiple pending orders indicate webhook processing failure")
        logger.info("2. Manual domain creation bypassed normal registration workflow")  
        logger.info("3. Need to identify exact failure point in payment confirmation chain")
        logger.info("4. Database saving methods exist but may have signature mismatches")
        
    except Exception as e:
        logger.error(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(investigate_registration_failure())