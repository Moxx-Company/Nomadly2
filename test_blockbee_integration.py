#!/usr/bin/env python3
"""
Test BlockBee API Integration
Verifies that the bot can generate real payment addresses
"""

import os
import asyncio
import logging
from nomadly_clean.apis.blockbee import BlockBeeAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_blockbee_integration():
    """Test BlockBee API integration"""
    try:
        # Check if API key exists
        api_key = os.getenv('BLOCKBEE_API_KEY')
        if not api_key:
            logger.error("❌ BLOCKBEE_API_KEY not found in environment")
            return False
        
        logger.info(f"✅ BLOCKBEE_API_KEY found: {api_key[:8]}...")
        
        # Initialize BlockBee API
        blockbee = BlockBeeAPI(api_key)
        
        # Test creating a payment address
        test_cryptos = ['btc', 'eth', 'ltc', 'doge']
        
        for crypto in test_cryptos:
            logger.info(f"\n🔍 Testing {crypto.upper()} address generation...")
            
            try:
                result = blockbee.create_payment_address(
                    cryptocurrency=crypto,
                    callback_url=f"https://nomadly2-onarrival.replit.app/webhook/blockbee/test_{crypto}",
                    amount=10.0  # $10 test amount
                )
                
                if result.get('status') == 'success':
                    address = result.get('address_in')
                    logger.info(f"✅ {crypto.upper()} address: {address}")
                else:
                    logger.error(f"❌ {crypto.upper()} failed: {result}")
                    
            except Exception as e:
                logger.error(f"❌ {crypto.upper()} error: {e}")
        
        logger.info("\n✅ BlockBee integration test complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_blockbee_integration())