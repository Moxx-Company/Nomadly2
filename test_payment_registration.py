#!/usr/bin/env python3
"""Test the complete payment to registration workflow"""

import asyncio
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_registration():
    # Import required modules
    from background_payment_monitor import payment_monitor
    from domain_service import DomainService
    
    # Setup test data
    user_id = 5590563715
    domain = "claudebaby.sbs"
    payment_address = "0xE0B4D227C8df941920854b6A5b2C69aD33b9AB3E"
    
    # Create a mock bot instance with domain service
    class MockBot:
        def __init__(self):
            self.domain_service = DomainService()
            self.application = None
    
    mock_bot = MockBot()
    payment_monitor.bot_instance = mock_bot
    
    logger.info("Testing domain registration workflow...")
    
    # Test domain service directly
    try:
        result = await mock_bot.domain_service.process_domain_registration(
            telegram_id=user_id,
            domain_name=domain,
            payment_method="crypto",
            nameserver_choice="nomadly",
            crypto_currency="eth"
        )
        
        logger.info(f"Domain registration result: {result}")
        
        if result.get('success'):
            logger.info("✅ Domain registration successful!")
        else:
            logger.error(f"❌ Domain registration failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Error during domain registration test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_registration())
