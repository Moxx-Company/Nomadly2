#!/usr/bin/env python3
"""
Test Nameserver Update Fix for letusdoit.sbs
===========================================

Test the newly added update_domain_nameservers method.
"""

import sys
import logging
import asyncio

# Add project root to path
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_nameserver_update_fix():
    """Test the newly added update_domain_nameservers method"""
    
    logger.info("🧪 TESTING NAMESERVER UPDATE FIX")
    logger.info("=" * 50)
    
    try:
        from apis.production_openprovider import OpenProviderAPI
        op_api = OpenProviderAPI()
        
        # Test the new method exists
        if hasattr(op_api, 'update_domain_nameservers'):
            logger.info("✅ update_domain_nameservers method found!")
            
            # Test with letusdoit.sbs domain ID and current nameservers
            domain_id = 27824967
            nameservers = ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]
            
            logger.info(f"Testing nameserver update for domain ID: {domain_id}")
            logger.info(f"Nameservers: {nameservers}")
            
            # Test the method
            success = op_api.update_domain_nameservers(domain_id, nameservers)
            
            if success:
                logger.info("🎉 NAMESERVER UPDATE SUCCESSFUL!")
                logger.info("✅ The 'Account mismatch' error should be resolved")
                logger.info("✅ Users can now update nameservers for letusdoit.sbs")
            else:
                logger.error("❌ Nameserver update failed")
                logger.error("   Need to investigate API response details")
                
        else:
            logger.error("❌ update_domain_nameservers method not found")
            logger.error("   Method was not added correctly")
            
    except Exception as e:
        logger.error(f"Test error: {e}")
    
    logger.info("")
    logger.info("🎯 NEXT STEPS:")
    logger.info("1. If successful: Remove account mismatch restrictions")
    logger.info("2. Update error messaging to be more specific")
    logger.info("3. Test with real user to confirm fix works")

if __name__ == "__main__":
    asyncio.run(test_nameserver_update_fix())