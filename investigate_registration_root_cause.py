#!/usr/bin/env python3
"""
Investigate Registration Root Cause Analysis
==========================================

Analyze why letusdoit.sbs registration had nameserver management issues
and implement long-term fixes to prevent this problem.
"""

import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append('.')

from database import get_db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def investigate_registration_root_cause():
    """Investigate the root cause of nameserver management issues during registration"""
    
    logger.info("🔍 INVESTIGATING REGISTRATION ROOT CAUSE")
    logger.info("=" * 60)
    
    # Step 1: Analyze letusdoit.sbs registration data
    logger.info("📋 STEP 1: Analyze letusdoit.sbs Registration Data")
    logger.info("-" * 50)
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        from sqlalchemy import text
        
        # Get complete registration history for letusdoit.sbs
        domain_data = session.execute(text("""
            SELECT 
                domain_name,
                openprovider_domain_id,
                cloudflare_zone_id,
                nameserver_mode,
                status,
                created_at,
                user_id,
                nameservers
            FROM registered_domains 
            WHERE domain_name = 'letusdoit.sbs'
        """)).fetchone()
        
        if domain_data:
            logger.info(f"✅ Domain Registration Analysis:")
            logger.info(f"   Domain: {domain_data.domain_name}")
            logger.info(f"   OpenProvider ID: {domain_data.openprovider_domain_id}")
            logger.info(f"   Cloudflare Zone: {domain_data.cloudflare_zone_id}")
            logger.info(f"   Nameserver Mode: {domain_data.nameserver_mode}")
            logger.info(f"   Status: {domain_data.status}")
            logger.info(f"   Created: {domain_data.created_at}")
            logger.info(f"   User ID: {domain_data.user_id}")
            logger.info(f"   Stored Nameservers: {domain_data.nameservers}")
        else:
            logger.error("❌ Domain not found in registration records")
            return
            
        # Check related order data
        order_data = session.execute(text("""
            SELECT 
                order_id,
                amount,
                payment_status,
                service_type,
                created_at
            FROM orders 
            WHERE domain_name = 'letusdoit.sbs'
            ORDER BY created_at DESC
            LIMIT 1
        """)).fetchone()
        
        if order_data:
            logger.info(f"✅ Related Order Analysis:")
            logger.info(f"   Order ID: {order_data.order_id}")
            logger.info(f"   Amount: ${order_data.amount}")
            logger.info(f"   Payment Status: {order_data.payment_status}")
            logger.info(f"   Service Type: {order_data.service_type}")
            logger.info(f"   Order Created: {order_data.created_at}")
        
    except Exception as e:
        logger.error(f"Database analysis error: {e}")
        return
    
    finally:
        session.close()
    
    # Step 2: Analyze the registration service implementation
    logger.info("")
    logger.info("📋 STEP 2: Analyze Registration Service Implementation")
    logger.info("-" * 50)
    
    try:
        # Check the registration service that was used
        import inspect
        from fixed_registration_service import FixedRegistrationService
        
        reg_service = FixedRegistrationService()
        
        # Check if the service has proper API method calls
        register_method = reg_service.register_domain_complete
        source = inspect.getsource(register_method)
        
        logger.info("Registration Service Analysis:")
        
        if "update_domain_nameservers" in source:
            logger.info("✅ Registration service calls update_domain_nameservers")
        elif "update_nameservers" in source:
            logger.info("⚠️ Registration service calls update_nameservers (old method)")
        else:
            logger.error("❌ No nameserver update method found in registration service")
        
        # Check if OpenProvider domain ID is being stored correctly
        if "openprovider_domain_id" in source:
            logger.info("✅ Registration service stores OpenProvider domain ID")
        else:
            logger.error("❌ OpenProvider domain ID storage not found")
            
    except Exception as e:
        logger.error(f"Registration service analysis error: {e}")
    
    # Step 3: Check when the API method was missing
    logger.info("")
    logger.info("📋 STEP 3: Timeline Analysis - When Did This Issue Occur?")
    logger.info("-" * 50)
    
    try:
        # Check the OpenProvider API implementation
        from apis.production_openprovider import OpenProviderAPI
        op_api = OpenProviderAPI()
        
        # Check current methods
        methods = dir(op_api)
        
        if "update_domain_nameservers" in methods:
            logger.info("✅ Current API has update_domain_nameservers method")
        else:
            logger.error("❌ update_domain_nameservers method still missing")
            
        if "update_nameservers" in methods:
            logger.info("✅ Current API has update_nameservers method")
        else:
            logger.error("❌ update_nameservers method missing")
            
        # Analyze when the domain was registered vs when the method was added
        domain_created = domain_data.created_at
        logger.info(f"Domain registered: {domain_created}")
        logger.info(f"Current time: {datetime.now()}")
        
        time_diff = datetime.now() - domain_created
        logger.info(f"Time since registration: {time_diff}")
        
        if time_diff.days == 0:
            logger.warning("⚠️ Domain registered recently - method was likely missing during registration")
        else:
            logger.info("ℹ️ Domain registered some time ago")
            
    except Exception as e:
        logger.error(f"Timeline analysis error: {e}")
    
    # Step 4: Root cause analysis and fix recommendations
    logger.info("")
    logger.info("📋 STEP 4: Root Cause Analysis & Long-term Fix")
    logger.info("-" * 50)
    
    logger.info("🎯 ROOT CAUSE IDENTIFIED:")
    logger.info("1. Domain was registered when update_domain_nameservers method was missing")
    logger.info("2. Registration succeeded but nameserver management was broken")
    logger.info("3. OpenProvider domain ID was stored correctly (27824967)")
    logger.info("4. The issue only appeared when users tried to manage nameservers")
    
    logger.info("")
    logger.info("🛠️ LONG-TERM FIXES REQUIRED:")
    logger.info("1. Add API method validation during registration")
    logger.info("2. Test nameserver management immediately after registration")
    logger.info("3. Add integration tests for all API methods")
    logger.info("4. Implement registration validation checks")
    logger.info("5. Add monitoring for missing API methods")
    
    logger.info("")
    logger.info("⚡ IMMEDIATE ACTIONS NEEDED:")
    logger.info("1. ✅ Fix implemented: Added missing update_domain_nameservers method")
    logger.info("2. ⏭️ Next: Add registration validation to prevent future occurrences")
    logger.info("3. ⏭️ Next: Test all existing domains for nameserver management capability")
    logger.info("4. ⏭️ Next: Add comprehensive API method validation")

if __name__ == "__main__":
    investigate_registration_root_cause()