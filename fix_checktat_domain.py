#!/usr/bin/env python3
"""
Fix checktat-atoocol.info domain management issues
Update missing contact handle from OpenProvider API
"""

import logging
from apis.production_openprovider import OpenProviderAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_checktat_domain():
    """Fix checktat-atoocol.info domain by getting proper contact handle"""
    
    domain_id = 27821414  # From database query
    domain_name = "checktat-atoocol.info"
    
    logger.info(f"🔧 Fixing domain: {domain_name}")
    logger.info(f"   OpenProvider Domain ID: {domain_id}")
    
    try:
        # Initialize OpenProvider API
        openprovider = OpenProviderAPI()
        
        # Get domain info from OpenProvider to find the contact handle
        logger.info(f"🔍 Retrieving domain info from OpenProvider...")
        domain_info = openprovider.get_domain_info(domain_id)
        
        if domain_info:
            logger.info(f"✅ Domain found in OpenProvider:")
            logger.info(f"   Status: {domain_info.get('status', 'N/A')}")
            logger.info(f"   Expiry: {domain_info.get('expiry_date', 'N/A')}")
            
            # Extract contact handles
            owner_handle = domain_info.get('owner_handle')
            admin_handle = domain_info.get('admin_handle')  
            tech_handle = domain_info.get('tech_handle')
            billing_handle = domain_info.get('billing_handle')
            
            logger.info(f"   Owner Handle: {owner_handle}")
            logger.info(f"   Admin Handle: {admin_handle}")
            logger.info(f"   Tech Handle: {tech_handle}")
            logger.info(f"   Billing Handle: {billing_handle}")
            
            # Use the owner handle as the primary contact handle
            correct_handle = owner_handle
            
            if correct_handle:
                logger.info(f"✅ Found correct contact handle: {correct_handle}")
                
                # Update database with correct contact handle
                update_sql = f"""
UPDATE registered_domains 
SET openprovider_contact_handle = '{correct_handle}'
WHERE domain_name = '{domain_name}' AND openprovider_domain_id = '{domain_id}';
"""
                logger.info(f"📝 SQL to update database:")
                logger.info(update_sql)
                
                return {
                    "success": True,
                    "correct_handle": correct_handle,
                    "update_sql": update_sql,
                    "domain_info": domain_info
                }
            else:
                logger.error(f"❌ No contact handle found in OpenProvider response")
                return {"success": False, "error": "No contact handle found"}
                
        else:
            logger.error(f"❌ Domain not found in OpenProvider with ID {domain_id}")
            return {"success": False, "error": "Domain not found in OpenProvider"}
            
    except Exception as e:
        logger.error(f"❌ Error retrieving domain info: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = fix_checktat_domain()
    
    if result["success"]:
        print("\n" + "="*60)
        print("SUCCESS - Contact handle found!")
        print("="*60)
        print(f"Correct handle: {result['correct_handle']}")
        print("\nRun this SQL to fix the database:")
        print(result['update_sql'])
    else:
        print("\n" + "="*60)
        print("FAILED - Could not retrieve contact handle")
        print("="*60)
        print(f"Error: {result['error']}")