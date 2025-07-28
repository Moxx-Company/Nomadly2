#!/usr/bin/env python3
"""
Simple OpenProvider Customer Cleanup Script
Delete all customers except JC960450-US and JC961581-US
"""

import logging
import sys
import requests
from apis.production_openprovider import OpenProviderAPI

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Customers to keep (DO NOT DELETE)
PROTECTED_CUSTOMERS = [
    "JC960450-US",
    "JC961581-US"
]

def cleanup_customers(dry_run=True):
    """Simple customer cleanup without domain checking"""
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
        
        # Analyze customers
        to_delete = []
        to_keep = []
        
        for customer in customers:
            handle = customer.get("handle", "")
            name = customer.get("name", {})
            full_name = f"{name.get('first_name', '')} {name.get('last_name', '')}".strip()
            
            if handle in PROTECTED_CUSTOMERS:
                to_keep.append((handle, full_name, "PROTECTED"))
                logger.info(f"KEEP: {handle} ({full_name}) - PROTECTED")
            else:
                to_delete.append((handle, full_name))
                if dry_run:
                    logger.info(f"DELETE: {handle} ({full_name})")
        
        logger.info(f"\nSUMMARY:")
        logger.info(f"Total customers: {len(customers)}")
        logger.info(f"Protected customers: {len(to_keep)}")
        logger.info(f"Customers to delete: {len(to_delete)}")
        
        if not dry_run and to_delete:
            logger.info(f"\nExecuting deletions...")
            deleted = 0
            failed = 0
            
            for handle, name in to_delete:
                try:
                    delete_url = f"{api.base_url}/v1beta/customers/{handle}"
                    delete_response = requests.delete(delete_url, headers=headers, timeout=15)
                    
                    if delete_response.status_code in [200, 204, 404]:
                        logger.info(f"✓ Deleted: {handle}")
                        deleted += 1
                    else:
                        logger.error(f"✗ Failed to delete {handle}: {delete_response.status_code}")
                        failed += 1
                except Exception as e:
                    logger.error(f"✗ Error deleting {handle}: {e}")
                    failed += 1
            
            logger.info(f"\nRESULTS:")
            logger.info(f"Successfully deleted: {deleted}")
            logger.info(f"Failed deletions: {failed}")
        
        elif dry_run:
            logger.info(f"\nThis is a dry run. Run with dry_run=False to execute deletions.")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

if __name__ == "__main__":
    print("=== OpenProvider Customer Cleanup ===")
    print("Protected customers: JC960450-US, JC961581-US")
    print()
    
    # First show what would be deleted
    print("DRY RUN - Showing what would be deleted:")
    print("-" * 50)
    cleanup_customers(dry_run=True)
    
    print("\n" + "=" * 50)
    response = input("Proceed with actual deletions? (type 'DELETE' to confirm): ")
    
    if response == "DELETE":
        print("\nExecuting deletions...")
        print("-" * 50)
        cleanup_customers(dry_run=False)
    else:
        print("Cancelled by user")