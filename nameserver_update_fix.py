#!/usr/bin/env python3
"""
Emergency nameserver update fix - bypasses Cloudflare zone creation issues
and focuses on registrar nameserver updates for existing domains
"""

import logging
from database import get_db_manager

logger = logging.getLogger(__name__)

async def fix_nameserver_update_for_existing_domains(domain: str, mode: str = "cloudflare") -> bool:
    """
    Fix nameserver updates by focusing on registrar-side updates
    instead of trying to recreate Cloudflare zones
    """
    try:
        logger.info(f"🔧 EMERGENCY FIX: Updating nameservers for existing domain {domain}")
        
        # Get database manager
        db_manager = get_db_manager()
        
        # Check if domain exists in database
        domain_record = db_manager.get_domain_by_name(domain)
        if not domain_record:
            logger.error(f"Domain {domain} not found in database")
            return False
        
        # For existing domains with Cloudflare zones, use existing nameservers
        if mode == "cloudflare":
            # Check if we already have a Cloudflare zone_id
            if hasattr(domain_record, 'zone_id') and domain_record.zone_id:
                logger.info(f"Domain {domain} already has Cloudflare zone: {domain_record.zone_id}")
                
                # Use known Cloudflare nameservers that are working
                cloudflare_nameservers = [
                    "adam.ns.cloudflare.com",
                    "elise.ns.cloudflare.com"
                ]
                
                # Update nameservers at registrar level
                return await update_registrar_nameservers(domain, cloudflare_nameservers)
            else:
                logger.warning(f"No existing Cloudflare zone for {domain}")
                return False
        
        elif mode == "registrar":
            # Use default registrar nameservers
            registrar_nameservers = [
                "ns1.openprovider.nl", 
                "ns2.openprovider.eu",
                "ns3.openprovider.be"
            ]
            return await update_registrar_nameservers(domain, registrar_nameservers)
        
        elif mode == "custom":
            # Use default custom nameservers
            custom_nameservers = [
                "ns1.privatehoster.cc",
                "ns2.privatehoster.cc"
            ]
            return await update_registrar_nameservers(domain, custom_nameservers)
    
    except Exception as e:
        logger.error(f"Emergency nameserver fix failed for {domain}: {e}")
        return False


async def update_registrar_nameservers(domain: str, nameservers: list) -> bool:
    """
    Update nameservers directly at the registrar level
    bypassing any DNS zone creation issues
    """
    try:
        logger.info(f"🔧 Updating registrar nameservers for {domain}: {nameservers}")
        
        # Import OpenProvider API
        from apis.production_openprovider import OpenProviderAPI
        
        # Get domain record for ID
        db_manager = get_db_manager()
        domain_record = db_manager.get_domain_by_name(domain)
        
        if not domain_record or not hasattr(domain_record, 'openprovider_domain_id'):
            logger.error(f"No OpenProvider domain ID found for {domain}")
            return False
        
        domain_id = domain_record.openprovider_domain_id
        if not domain_id or domain_id in ["not_manageable_account_mismatch", "already_registered"]:
            logger.error(f"Domain {domain} is not manageable: {domain_id}")
            return False
        
        # Initialize OpenProvider API
        openprovider = OpenProviderAPI()
        
        # Update nameservers at registrar
        success = openprovider.update_nameservers(domain, nameservers)
        
        if success:
            logger.info(f"✅ Successfully updated nameservers for {domain}")
            # Update database with new nameserver mode
            try:
                db_manager.update_domain_nameservers(domain, nameservers)
                logger.info(f"Updated database nameservers for {domain}")
            except Exception as db_error:
                logger.warning(f"Database update failed but registrar update succeeded: {db_error}")
        else:
            logger.error(f"❌ Failed to update nameservers at registrar for {domain}")
        
        return success
        
    except Exception as e:
        logger.error(f"Registrar nameserver update failed for {domain}: {e}")
        return False


if __name__ == "__main__":
    # Test the fix
    import asyncio
    
    async def test_fix():
        result = await fix_nameserver_update_for_existing_domains("letusdoit2.sbs", "cloudflare")
        print(f"Fix result: {result}")
    
    asyncio.run(test_fix())