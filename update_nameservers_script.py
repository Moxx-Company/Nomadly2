#!/usr/bin/env python3
"""
Script to update nameservers for claudeb.sbs to use Cloudflare nameservers
"""

import logging
from apis.production_openprovider import OpenProviderAPI
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_domain_nameservers():
    """Update nameservers for claudeb.sbs"""
    domain = "claudeb.sbs"
    new_nameservers = [
        "anderson.ns.cloudflare.com",
        "leanna.ns.cloudflare.com"
    ]
    
    try:
        # Get domain record from database
        db_manager = get_db_manager()
        domain_record = db_manager.get_domain_by_name(domain)
        
        if not domain_record:
            logger.error(f"Domain {domain} not found in database")
            return False
            
        if not domain_record.openprovider_domain_id:
            logger.error(f"No OpenProvider domain ID for {domain}")
            return False
            
        logger.info(f"Found domain {domain} with OpenProvider ID: {domain_record.openprovider_domain_id}")
        
        # Initialize OpenProvider API
        api = OpenProviderAPI()
        
        # Update nameservers via OpenProvider
        logger.info(f"Updating nameservers for {domain} to: {new_nameservers}")
        success = api.update_nameservers(domain, new_nameservers)
        
        if success:
            logger.info(f"✅ Successfully updated nameservers for {domain}")
            
            # Update database record
            try:
                import json
                nameservers_json = json.dumps(new_nameservers)
                db_manager.execute_sql(
                    "UPDATE registered_domains SET nameservers = %s WHERE domain_name = %s",
                    (nameservers_json, domain)
                )
                logger.info(f"✅ Updated database with new nameservers")
            except Exception as e:
                logger.warning(f"Database update failed: {e}")
                
            return True
        else:
            logger.error(f"❌ Failed to update nameservers for {domain}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating nameservers: {e}")
        return False

if __name__ == "__main__":
    success = update_domain_nameservers()
    if success:
        print("✅ Nameserver update completed successfully")
    else:
        print("❌ Nameserver update failed")