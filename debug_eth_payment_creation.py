#!/usr/bin/env python3
"""
Debug ETH Payment Creation Issue
Test crypto payment creation to identify the root cause of the error
"""

import asyncio
import logging
from payment_service import PaymentService
from fix_callback_database_queries import get_order_details_for_switch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_eth_payment_creation():
    """Test ETH payment creation with real order data"""
    try:
        # Test order ID from recent activity
        test_order_id = "ffc3fe5f"  # Use recent completed order for reference
        
        # Get order details
        order_details = get_order_details_for_switch(test_order_id, 5590563715)
        logger.info(f"Order details: {order_details}")
        
        if not order_details:
            logger.error("❌ No order details found")
            return
            
        # Test PaymentService creation
        payment_service = PaymentService()
        logger.info("✅ PaymentService created successfully")
        
        # Test crypto payment creation
        payment_result = await payment_service.create_crypto_payment(
            telegram_id=5590563715,
            amount=9.87,
            crypto_currency="eth",
            service_type="domain_registration", 
            service_details={
                "domain": "letsgethere.sbs",
                "type": "domain_registration"
            }
        )
        
        logger.info(f"Payment result: {payment_result}")
        
        if payment_result and payment_result.get("payment_address"):
            logger.info("✅ ETH payment creation successful!")
            logger.info(f"Payment address: {payment_result['payment_address']}")
            logger.info(f"Crypto amount: {payment_result.get('crypto_amount')}")
            logger.info(f"Order ID: {payment_result.get('order_id')}")
        else:
            logger.error("❌ ETH payment creation failed - no payment address returned")
            
    except Exception as e:
        logger.error(f"❌ ETH payment creation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_eth_payment_creation())