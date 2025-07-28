#!/usr/bin/env python3
"""
Test if checktat-atoocol.info domain management is now working
"""

import logging
from apis.production_openprovider import OpenProviderAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_domain_management():
    """Test nameserver update for checktat-atoocol.info domain"""
    domain_name = "checktat-atoocol.info"
    test_nameservers = ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]
    
    logger.info(f"🧪 Testing domain management for: {domain_name}")
    
    try:
        openprovider = OpenProviderAPI()
        
        # Test nameserver update - this should now work with correct contact handle
        logger.info(f"📝 Testing nameserver update...")
        result = openprovider.update_nameservers(domain_name, test_nameservers)
        
        if result:
            logger.info(f"✅ SUCCESS: Domain management is working!")
            logger.info(f"   Nameservers updated successfully")
            return True
        else:
            logger.error(f"❌ FAILED: Domain management still not working")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing domain management: {e}")
        return False

if __name__ == "__main__":
    success = test_domain_management()
    
    print("\n" + "="*60)
    if success:
        print("✅ DOMAIN MANAGEMENT FIXED")
        print("Customer can now manage checktat-atoocol.info")
    else:
        print("❌ DOMAIN MANAGEMENT STILL BROKEN")
        print("Further investigation needed")
    print("="*60)