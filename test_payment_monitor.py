#!/usr/bin/env python3
"""Test script to check payment monitor functionality"""

import asyncio
import logging
from background_payment_monitor import payment_monitor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_payment_check():
    """Test the payment monitoring system"""
    logger.info("🧪 Testing payment monitor...")
    
    # Check active payments
    logger.info(f"Active payments: {len(payment_monitor.active_payments)}")
    for address, info in payment_monitor.active_payments.items():
        logger.info(f"Monitoring: {address[:20]}... for {info['domain']}")
    
    # Trigger immediate check
    logger.info("Triggering immediate payment check...")
    await payment_monitor.check_pending_payments()
    
    logger.info("✅ Test complete")

if __name__ == "__main__":
    asyncio.run(test_payment_check())