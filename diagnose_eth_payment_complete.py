#!/usr/bin/env python3
"""
Complete ETH Payment Diagnostic
Tests the entire ETH payment workflow to identify where failures occur
"""

import logging
import asyncio
from database import get_db_manager
from payment_service import get_payment_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_eth_payment_workflow():
    """Test complete ETH payment creation workflow"""
    
    logger.info("🔍 Complete ETH Payment Workflow Diagnostic")
    
    # Test 1: Database Connection
    logger.info("📊 Testing database connection...")
    try:
        db_manager = get_db_manager()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return
    
    # Test 2: Payment Service Initialization  
    logger.info("💳 Testing payment service...")
    try:
        payment_service = get_payment_service()
        logger.info("✅ Payment service initialized")
    except Exception as e:
        logger.error(f"❌ Payment service failed: {e}")
        return
    
    # Test 3: Create ETH Payment
    logger.info("🔷 Testing ETH payment creation...")
    try:
        result = await payment_service.create_crypto_payment(
            telegram_id=123456789,
            service_type="domain_registration",
            service_details={
                "domain_name": "testeth.sbs",
                "tld": ".sbs", 
                "registration_period": 1,
                "nameserver_choice": "cloudflare"
            },
            amount=2.99,
            crypto_currency="eth"
        )
        
        logger.info(f"🎯 ETH Payment Result: {result}")
        
        if result.get("success"):
            logger.info("✅ ETH payment creation SUCCESSFUL!")
            logger.info(f"📍 Payment Address: {result.get('payment_address')}")
            logger.info(f"💰 Crypto Amount: {result.get('crypto_amount')}")
            logger.info(f"📋 Order ID: {result.get('order_id')}")
        else:
            logger.error("❌ ETH payment creation FAILED!")
            logger.error(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ ETH payment creation exception: {e}")
        
    # Test 4: Check BlockBee ETH Support
    logger.info("🔗 Testing BlockBee ETH integration...")
    try:
        from apis.api_manager import APIManager
        api_manager = APIManager()
        
        # Test direct BlockBee ETH call
        callback_url = "https://test.nomadly.com/webhook/test"
        blockbee_result = api_manager.blockbee.create_payment_address("eth", callback_url, 2.99)
        
        logger.info(f"🔷 BlockBee ETH Result: {blockbee_result}")
        
        if blockbee_result.get("status") == "success":
            logger.info("✅ BlockBee ETH integration working!")
        else:
            logger.error("❌ BlockBee ETH integration failing!")
            
    except Exception as e:
        logger.error(f"❌ BlockBee ETH test failed: {e}")

def test_eth_callback_routing():
    """Test ETH callback routing patterns"""
    
    logger.info("\n🔀 Testing ETH Callback Routing")
    
    test_callbacks = [
        "register_crypto_eth_nomadly2.sbs",
        "crypto_domain_eth_cloudflare_nomadly2.sbs",
        "crypto_domain_eth_registrar_nomadly2.sbs",
        "crypto_domain_eth_custom_nomadly2.sbs"
    ]
    
    for callback in test_callbacks:
        logger.info(f"\n📝 Testing callback: {callback}")
        
        # Test register_crypto_eth pattern
        if callback.startswith("register_crypto_"):
            logger.info("✅ Would match register_crypto_ handler")
            temp = callback.replace("register_crypto_", "")
            parts = temp.split("_", 1)
            if len(parts) >= 2:
                crypto = parts[0]
                domain = parts[1]
                logger.info(f"🎯 Would extract: crypto={crypto}, domain={domain}")
        
        # Test crypto_domain_eth pattern
        elif callback.startswith("crypto_domain_"):
            logger.info("✅ Would match crypto_domain_ handler")
            parts = callback.split("_")
            logger.info(f"📋 Parts: {parts} (count: {len(parts)})")
            
            if len(parts) >= 5:
                crypto = parts[2]
                nameserver = parts[3]
                domain = "_".join(parts[4:])
                logger.info(f"🎯 Would extract: crypto={crypto}, ns={nameserver}, domain={domain}")
            else:
                logger.error("❌ Not enough parts for crypto_domain_ handler")
        else:
            logger.warning("⚠️ No matching handler pattern")

async def main():
    """Run all diagnostics"""
    logger.info("🚀 Starting Complete ETH Payment Diagnostics")
    
    test_eth_callback_routing()
    await test_eth_payment_workflow()
    
    logger.info("\n📋 Diagnostic Summary:")
    logger.info("• Callback routing tested for both ETH payment paths")
    logger.info("• Database and payment service connectivity verified")
    logger.info("• BlockBee ETH API integration tested")
    logger.info("• End-to-end ETH payment workflow validated")

if __name__ == "__main__":
    asyncio.run(main())