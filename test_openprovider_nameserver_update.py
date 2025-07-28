#!/usr/bin/env python3
"""
Test OpenProvider Nameserver Update for letusdoit.sbs
====================================================

Test and fix the actual OpenProvider nameserver update functionality.
"""

import sys
import logging
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openprovider_nameserver_update():
    """Test the actual OpenProvider nameserver update for letusdoit.sbs"""
    
    logger.info("🧪 TESTING OPENPROVIDER NAMESERVER UPDATE")
    logger.info("=" * 60)
    
    # Step 1: Test domain lookup
    logger.info("📋 STEP 1: Test Domain Lookup in OpenProvider")
    logger.info("-" * 50)
    
    try:
        from apis.production_openprovider import OpenProviderAPI
        op_api = OpenProviderAPI()
        
        # Authenticate first
        logger.info("🔐 Authenticating with OpenProvider...")
        auth_result = await op_api._auth_request()
        
        if auth_result:
            logger.info("✅ OpenProvider authentication successful")
        else:
            logger.error("❌ OpenProvider authentication failed")
            return
        
        # Try to get domain info for letusdoit.sbs
        domain_name = "letusdoit.sbs"
        domain_id = 27824967
        
        logger.info(f"🔍 Testing domain lookup for {domain_name} (ID: {domain_id})")
        
        # Test the domain info retrieval
        try:
            # We'll test if we can make a nameserver update call
            logger.info("📡 Testing nameserver update API call...")
            
            # Get current Cloudflare nameservers for letusdoit.sbs
            from apis.production_cloudflare import CloudflareAPI
            cf_api = CloudflareAPI()
            
            cloudflare_zone_id = "a264e8e21a7938689d561ef4a2f06f3f"
            
            # Try to get nameservers properly (fixing the async issue from diagnostic)
            try:
                nameservers = await cf_api.get_nameservers(cloudflare_zone_id)
                if nameservers:
                    logger.info(f"✅ Current Cloudflare nameservers: {nameservers}")
                else:
                    # Fallback to default Cloudflare nameservers
                    nameservers = ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]
                    logger.info(f"ℹ️ Using default nameservers: {nameservers}")
            except Exception as ns_error:
                logger.warning(f"Nameserver retrieval error: {ns_error}")
                nameservers = ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]
                logger.info(f"ℹ️ Using fallback nameservers: {nameservers}")
            
            # Now test the nameserver update
            logger.info("🔄 Testing nameserver update...")
            
            success = op_api.update_domain_nameservers(domain_id, nameservers)
            
            if success:
                logger.info("✅ NAMESERVER UPDATE SUCCESSFUL!")
                logger.info("   The domain can be managed through OpenProvider")
                logger.info("   Nameserver switching should work now")
            else:
                logger.error("❌ NAMESERVER UPDATE FAILED")
                logger.error("   This explains the 'Account mismatch' error")
                
        except Exception as update_error:
            logger.error(f"❌ Nameserver update test failed: {update_error}")
            logger.error("   This is the root cause of the nameserver management issue")
        
    except Exception as e:
        logger.error(f"OpenProvider test error: {e}")
    
    # Step 2: Check the nameserver update method implementation
    logger.info("")
    logger.info("📋 STEP 2: Analyze Nameserver Update Implementation")
    logger.info("-" * 50)
    
    try:
        import inspect
        
        # Check the current implementation
        update_method = op_api.update_domain_nameservers
        source = inspect.getsource(update_method)
        
        logger.info("Current update_domain_nameservers implementation:")
        lines = source.split('\n')
        for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
            logger.info(f"{i:2d}: {line}")
            
        # Check if the method uses the correct API endpoint and format
        if "/domains/" in source and "name_servers" in source:
            logger.info("✅ Method appears to use correct API structure")
        else:
            logger.warning("⚠️ Method may use incorrect API structure")
            
    except Exception as e:
        logger.error(f"Implementation analysis error: {e}")
    
    # Step 3: Provide fix recommendations
    logger.info("")
    logger.info("📋 STEP 3: Fix Recommendations")
    logger.info("-" * 50)
    
    logger.info("🎯 RECOMMENDED FIXES:")
    logger.info("1. Verify OpenProvider API endpoint is correct")
    logger.info("2. Check domain ID format in API calls")
    logger.info("3. Ensure nameserver format matches OpenProvider requirements")
    logger.info("4. Test with exact nameserver format expected by API")
    logger.info("5. Add proper error handling for specific error codes")
    
    logger.info("")
    logger.info("💡 NEXT STEPS:")
    logger.info("✅ If update works: Remove account mismatch restriction")
    logger.info("❌ If update fails: Keep current Cloudflare-only approach")
    logger.info("🔧 Either way: Improve error messaging for users")

if __name__ == "__main__":
    asyncio.run(test_openprovider_nameserver_update())