#!/usr/bin/env python3
"""
Execute OpenProvider Customer Cleanup
Delete all customers except JC960450-US and JC961581-US
"""

import logging
import requests
from apis.production_openprovider import OpenProviderAPI

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Customers to keep (DO NOT DELETE)
PROTECTED_CUSTOMERS = [
    "JC960450-US",
    "JC961581-US"
]

def execute_cleanup():
    """Execute customer cleanup - LIVE DELETIONS"""
    try:
        # Initialize API
        api = OpenProviderAPI()
        logger.info("Connected to OpenProvider API")
        
        # Get all customers
        url = f"{api.base_url}/v1beta/customers"
        headers = {
            "Authorization": f"Bearer {api.token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to get customers: {response.status_code}")
            return
        
        result = response.json()
        customers = result.get("data", {}).get("results", [])
        
        logger.info(f"Found {len(customers)} total customers")
        logger.info(f"Protected customers: {PROTECTED_CUSTOMERS}")
        
        # Execute deletions
        deleted = 0
        failed = 0
        skipped = 0
        
        logger.info("Starting deletions...")
        
        for customer in customers:
            handle = customer.get("handle", "")
            name = customer.get("name", {})
            full_name = f"{name.get('first_name', '')} {name.get('last_name', '')}".strip()
            
            if handle in PROTECTED_CUSTOMERS:
                logger.info(f"SKIP: {handle} ({full_name}) - PROTECTED")
                skipped += 1
                continue
            
            try:
                delete_url = f"{api.base_url}/v1beta/customers/{handle}"
                delete_response = requests.delete(delete_url, headers=headers, timeout=15)
                
                if delete_response.status_code in [200, 204, 404]:
                    logger.info(f"✓ DELETED: {handle} ({full_name})")
                    deleted += 1
                else:
                    logger.error(f"✗ FAILED: {handle} - HTTP {delete_response.status_code}")
                    failed += 1
            except Exception as e:
                logger.error(f"✗ ERROR: {handle} - {e}")
                failed += 1
        
        logger.info("")
        logger.info("=== CLEANUP RESULTS ===")
        logger.info(f"Total customers processed: {len(customers)}")
        logger.info(f"Successfully deleted: {deleted}")
        logger.info(f"Protected (skipped): {skipped}")
        logger.info(f"Failed deletions: {failed}")
        
        if failed == 0:
            logger.info("✅ CLEANUP COMPLETED SUCCESSFULLY")
        else:
            logger.warning(f"⚠️ CLEANUP COMPLETED WITH {failed} FAILURES")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

if __name__ == "__main__":
    print("=== EXECUTING OPENPROVIDER CUSTOMER CLEANUP ===")
    print("This will DELETE all customers except:")
    print("- JC960450-US")
    print("- JC961581-US")
    print("")
    execute_cleanup()