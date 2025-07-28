#!/usr/bin/env python3
"""Test the domain registration directly without payment flow"""

import asyncio
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_registration():
    # Test creating an order directly
    try:
        from database import get_db_manager
        from models import Order
        
        db = get_db_manager()
        
        # Try creating a simple order
        logger.info("Testing Order creation...")
        order = Order(
            order_id="TEST-" + str(int(datetime.now().timestamp())),
            telegram_id=5590563715,
            service_type="domain_registration",
            service_details={"domain": "claudebaby.sbs"},
            amount=9.87,
            payment_method="crypto_eth",
            payment_status="completed"
        )
        
        logger.info(f"Order created in memory: {order.order_id}")
        
        # Now test domain registration without payment
        from domain_service import DomainService
        domain_service = DomainService()
        
        # Check if the domain service has the method we need
        if hasattr(domain_service, 'register_domain_with_openprovider'):
            logger.info("✅ Domain service has register_domain_with_openprovider method")
        else:
            logger.error("❌ Domain service missing register_domain_with_openprovider method")
            
        # Try simpler domain registration
        logger.info("Testing direct domain registration...")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_registration())
