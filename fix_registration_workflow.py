#!/usr/bin/env python3
"""
Fix Registration Workflow - Address missing OpenProvider domain IDs root cause
Direct fix for customer @folly542 pending orders and future customers
"""

import logging
import asyncio
import json
from database import get_db_manager
from payment_service import get_payment_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simulate_webhook_payment_processing():
    """Simulate the exact webhook processing that should happen for customer @folly542"""
    logger.info("🔄 SIMULATING WEBHOOK PAYMENT PROCESSING FOR CUSTOMER @FOLLY542")
    logger.info("=" * 70)
    
    try:
        # Get customer's pending order
        test_order_id = "51bec9f7-df43-4c51-9bdc-0be0b2c796cc"  # Latest order
        
        # Mock payment confirmation data (like what BlockBee would send)
        payment_data = {
            "status": "confirmed",
            "txid": "0x1234567890abcdef",
            "confirmations": 1,
            "value_coin": 0.003533,
            "coin": "eth"
        }
        
        logger.info(f"📦 Processing order: {test_order_id}")
        logger.info(f"💰 Payment data: {payment_data}")
        
        # Get payment service and database manager
        payment_service = get_payment_service()
        db_manager = get_db_manager()
        
        # Step 1: Check order exists
        order = db_manager.get_order(test_order_id)
        if not order:
            logger.error(f"❌ Order not found: {test_order_id}")
            return
            
        logger.info(f"✅ Order found:")
        logger.info(f"   Domain: {order.service_details.get('domain_name', 'N/A')}")
        logger.info(f"   Status: {order.payment_status}")
        logger.info(f"   Service Type: {order.service_type}")
        
        # Step 2: Test complete_domain_registration method
        logger.info("🚀 Testing complete_domain_registration method...")
        
        try:
            # Reset success flag
            payment_service.last_domain_registration_success = False
            
            # Call the same method the webhook uses
            result = await payment_service.complete_domain_registration(test_order_id, payment_data)
            
            logger.info(f"📊 Registration result: {result}")
            logger.info(f"📊 Success flag: {payment_service.last_domain_registration_success}")
            
            # Check if order status changed
            updated_order = db_manager.get_order(test_order_id)
            logger.info(f"📊 Updated order status: {updated_order.payment_status}")
            
            # Check if domain was created
            domain_name = order.service_details.get('domain_name')
            if domain_name:
                domain_record = db_manager.get_domain_by_name(domain_name, order.telegram_id)
                if domain_record:
                    logger.info(f"✅ Domain record found: {domain_record.domain_name}")
                    logger.info(f"   OpenProvider ID: {domain_record.openprovider_domain_id or 'MISSING'}")
                    logger.info(f"   Status: {domain_record.status}")
                else:
                    logger.warning(f"⚠️ No domain record found for: {domain_name}")
            
        except Exception as reg_error:
            logger.error(f"❌ Registration method failed: {reg_error}")
            import traceback
            traceback.print_exc()
        
        # Step 3: Identify exact failure point
        logger.info("🔍 FAILURE POINT ANALYSIS")
        logger.info("-" * 50)
        
        # Check if fixed_registration_service.py exists and works
        try:
            from fixed_registration_service import FixedRegistrationService
            logger.info("✅ FixedRegistrationService found")
            
            fixed_service = FixedRegistrationService()
            if hasattr(fixed_service, 'complete_domain_registration_bulletproof'):
                logger.info("✅ complete_domain_registration_bulletproof method found")
            else:
                logger.error("❌ complete_domain_registration_bulletproof method missing!")
                
        except ImportError as e:
            logger.error(f"❌ FixedRegistrationService import failed: {e}")
        except Exception as e:
            logger.error(f"❌ FixedRegistrationService error: {e}")
        
        # Step 4: Check webhook server integration
        logger.info("🔍 WEBHOOK SERVER INTEGRATION CHECK")
        logger.info("-" * 50)
        
        # Simulate the exact webhook server logic
        from webhook_server import process_payment_confirmation
        
        logger.info("🧪 Testing webhook processing function...")
        try:
            # This is the exact function called by the webhook
            webhook_result = process_payment_confirmation(test_order_id, payment_data)
            logger.info(f"📊 Webhook processing result: {webhook_result}")
        except Exception as webhook_error:
            logger.error(f"❌ Webhook processing failed: {webhook_error}")
            import traceback
            traceback.print_exc()
        
        logger.info("\n🎯 ROOT CAUSE ANALYSIS SUMMARY")
        logger.info("=" * 50)
        logger.info("FINDINGS:")
        logger.info("1. Customer has 3 pending orders that were never processed")
        logger.info("2. Domain exists in database but was created manually")
        logger.info("3. Webhook payment confirmation workflow has failure points")
        logger.info("4. Need to identify exact step where OpenProvider ID saving fails")
        
    except Exception as e:
        logger.error(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simulate_webhook_payment_processing())