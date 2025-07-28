#!/usr/bin/env python3
"""
Investigate Zone ID Storage Bug
===============================

Analyze why Cloudflare zone IDs weren't stored during domain registration.
"""

import sys
import logging
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append('.')

from database import get_db_manager
from apis.production_cloudflare import CloudflareAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def investigate_zone_id_storage_bug():
    """Investigate why zone IDs weren't stored during registration"""
    
    logger.info("🔍 INVESTIGATING ZONE ID STORAGE BUG")
    logger.info("=" * 50)
    
    # Get database manager
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        # Get the registered domains with their registration timeline
        from sqlalchemy import text
        
        domains = session.execute(text("""
            SELECT 
                rd.domain_name,
                rd.cloudflare_zone_id,
                rd.nameserver_mode,
                rd.created_at,
                rd.openprovider_domain_id
            FROM registered_domains rd
            WHERE rd.user_id = 5590563715
            ORDER BY rd.created_at DESC
        """)).fetchall()
        
        logger.info(f"Found {len(domains)} domains for analysis:")
        logger.info("")
        
        for domain in domains:
            logger.info(f"📍 Domain: {domain.domain_name}")
            logger.info(f"   Zone ID: {domain.cloudflare_zone_id or 'MISSING'}")
            logger.info(f"   Nameserver Mode: {domain.nameserver_mode}")
            logger.info(f"   Domain Created: {domain.created_at}")
            logger.info(f"   OpenProvider ID: {domain.openprovider_domain_id or 'MISSING'}")
            if domain.order_id:
                logger.info(f"   Order ID: {domain.order_id}")
                logger.info(f"   Order Created: {domain.order_created}")
                logger.info(f"   Payment Status: {domain.payment_status}")
            logger.info("")
        
        # Now let's check if zones exist in Cloudflare for domains that are missing zone IDs
        cf_api = CloudflareAPI()
        
        logger.info("🔍 CHECKING CLOUDFLARE FOR EXISTING ZONES")
        logger.info("-" * 40)
        
        for domain in domains:
            if not domain.cloudflare_zone_id and domain.nameserver_mode == "cloudflare":
                logger.info(f"Checking Cloudflare for: {domain.domain_name}")
                
                # Check if zone exists in Cloudflare
                cloudflare_zone_id = cf_api._get_zone_id(domain.domain_name)
                if cloudflare_zone_id:
                    logger.warning(f"   ❌ BUG CONFIRMED: Zone {cloudflare_zone_id} exists but not stored in DB!")
                    
                    # Get zone creation date from Cloudflare
                    zone_info = cf_api._get_zone_info(cloudflare_zone_id)
                    if zone_info:
                        created_on = zone_info.get('created_on')
                        logger.info(f"   Zone Created: {created_on}")
                        logger.info(f"   Domain Registered: {domain.created_at}")
                        
                        # Compare timestamps to understand timing
                        if created_on:
                            zone_time = datetime.fromisoformat(created_on.replace('Z', '+00:00'))
                            domain_time = domain.created_at
                            
                            if zone_time < domain_time:
                                logger.info(f"   ✅ Zone created BEFORE domain registration - should have been stored")
                            else:
                                logger.info(f"   ⚠️ Zone created AFTER domain registration - timing issue")
                else:
                    logger.info(f"   ✅ No zone found in Cloudflare - expected for missing zone_id")
        
        # Check the current registration workflow
        logger.info("")
        logger.info("🔧 ANALYZING REGISTRATION WORKFLOW")
        logger.info("-" * 40)
        
        # Check what registration service is currently being used
        from payment_service import PaymentService
        payment_service = PaymentService()
        
        # Look at the complete_domain_registration method
        import inspect
        registration_method = payment_service.complete_domain_registration
        source = inspect.getsource(registration_method)
        
        logger.info("Current registration method source:")
        logger.info(source[:500] + "..." if len(source) > 500 else source)
        
        # Check if fixed_registration_service exists and what it does
        try:
            from fixed_registration_service import FixedRegistrationService
            fixed_service = FixedRegistrationService()
            
            if hasattr(fixed_service, 'complete_domain_registration_bulletproof'):
                method = fixed_service.complete_domain_registration_bulletproof
                fixed_source = inspect.getsource(method)
                logger.info("")
                logger.info("Fixed registration service method:")
                logger.info(fixed_source[:500] + "..." if len(fixed_source) > 500 else fixed_source)
            
        except ImportError:
            logger.warning("❌ FixedRegistrationService not found")
        
        logger.info("")
        logger.info("🎯 ROOT CAUSE ANALYSIS COMPLETE")
        logger.info("-" * 40)
        
    except Exception as e:
        logger.error(f"Investigation failed: {e}")
        
    finally:
        session.close()

if __name__ == "__main__":
    investigate_zone_id_storage_bug()