#!/usr/bin/env python3
"""
OpenProvider Customer Cleanup Script
Delete all customers except JC960450-US and JC961581-US
"""

import logging
import sys
import time
from apis.production_openprovider import OpenProviderAPI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Customers to keep (DO NOT DELETE)
PROTECTED_CUSTOMERS = [
    "JC960450-US",
    "JC961581-US"
]

class OpenProviderCustomerCleanup:
    def __init__(self):
        """Initialize OpenProvider API connection"""
        try:
            self.api = OpenProviderAPI()
            logger.info("✅ OpenProvider API initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenProvider API: {e}")
            sys.exit(1)

    def list_all_customers(self):
        """Get all customers from OpenProvider account"""
        try:
            logger.info("🔍 Fetching all customers from OpenProvider...")
            
            # OpenProvider API endpoint for customers
            url = f"{self.api.base_url}/v1beta/customers"
            headers = {
                "Authorization": f"Bearer {self.api.token}",
                "Content-Type": "application/json"
            }
            
            import requests
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                customers = result.get("data", {}).get("results", [])
                logger.info(f"✅ Found {len(customers)} total customers")
                return customers
            else:
                logger.error(f"❌ Failed to fetch customers: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching customers: {e}")
            return []

    def get_customer_domains(self, customer_handle):
        """Check if customer has any domains registered"""
        try:
            url = f"{self.api.base_url}/v1beta/domains"
            headers = {
                "Authorization": f"Bearer {self.api.token}",
                "Content-Type": "application/json"
            }
            
            # Add filter for customer handle
            params = {"owner_handle": customer_handle}
            
            import requests
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                domains = result.get("data", {}).get("results", [])
                return len(domains)
            else:
                logger.warning(f"⚠️ Could not check domains for {customer_handle}")
                return -1  # Unknown domain count
                
        except Exception as e:
            logger.warning(f"⚠️ Error checking domains for {customer_handle}: {e}")
            return -1

    def delete_customer(self, customer_handle):
        """Delete a customer from OpenProvider"""
        try:
            logger.info(f"🗑️ Deleting customer: {customer_handle}")
            
            url = f"{self.api.base_url}/v1beta/customers/{customer_handle}"
            headers = {
                "Authorization": f"Bearer {self.api.token}",
                "Content-Type": "application/json"
            }
            
            import requests
            response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully deleted customer: {customer_handle}")
                return True
            elif response.status_code == 404:
                logger.info(f"ℹ️ Customer {customer_handle} not found (already deleted)")
                return True
            else:
                logger.error(f"❌ Failed to delete {customer_handle}: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting customer {customer_handle}: {e}")
            return False

    def run_cleanup(self, dry_run=True):
        """Run the customer cleanup process"""
        logger.info("🧹 STARTING OPENPROVIDER CUSTOMER CLEANUP")
        logger.info("=" * 60)
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No actual deletions will be performed")
        else:
            logger.info("⚠️ LIVE MODE - Customers will be permanently deleted!")
        
        logger.info("=" * 60)
        
        # Get all customers
        customers = self.list_all_customers()
        if not customers:
            logger.error("❌ Could not fetch customer list. Aborting cleanup.")
            return
        
        logger.info(f"📋 CUSTOMER ANALYSIS")
        logger.info("-" * 40)
        
        customers_to_delete = []
        customers_to_keep = []
        customers_with_domains = []
        
        for customer in customers:
            customer_handle = customer.get("handle", "")
            customer_name = customer.get("name", {})
            first_name = customer_name.get("first_name", "")
            last_name = customer_name.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            # Check if this is a protected customer
            if customer_handle in PROTECTED_CUSTOMERS:
                customers_to_keep.append((customer_handle, full_name, "PROTECTED"))
                logger.info(f"🛡️ KEEP: {customer_handle} ({full_name}) - PROTECTED")
                continue
            
            # Check if customer has domains
            domain_count = self.get_customer_domains(customer_handle)
            
            if domain_count > 0:
                customers_with_domains.append((customer_handle, full_name, domain_count))
                logger.info(f"⚠️ KEEP: {customer_handle} ({full_name}) - HAS {domain_count} DOMAINS")
            elif domain_count == 0:
                customers_to_delete.append((customer_handle, full_name))
                logger.info(f"🗑️ DELETE: {customer_handle} ({full_name}) - NO DOMAINS")
            else:
                # Unknown domain count - be safe and keep
                customers_to_keep.append((customer_handle, full_name, "UNKNOWN_DOMAINS"))
                logger.info(f"❓ KEEP: {customer_handle} ({full_name}) - DOMAIN CHECK FAILED")
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 CLEANUP SUMMARY")
        logger.info("-" * 40)
        logger.info(f"Total customers: {len(customers)}")
        logger.info(f"Protected customers: {len([c for c in customers_to_keep if c[2] == 'PROTECTED'])}")
        logger.info(f"Customers with domains: {len(customers_with_domains)}")
        logger.info(f"Customers to delete: {len(customers_to_delete)}")
        logger.info(f"Customers to keep (other): {len([c for c in customers_to_keep if c[2] != 'PROTECTED'])}")
        
        if customers_to_delete:
            logger.info(f"\n🗑️ CUSTOMERS TO DELETE ({len(customers_to_delete)}):")
            for handle, name in customers_to_delete:
                logger.info(f"  • {handle} ({name})")
        
        if customers_with_domains:
            logger.info(f"\n⚠️ CUSTOMERS WITH DOMAINS ({len(customers_with_domains)}) - WILL KEEP:")
            for handle, name, count in customers_with_domains:
                logger.info(f"  • {handle} ({name}) - {count} domains")
        
        # Execute deletions if not dry run
        if not dry_run and customers_to_delete:
            logger.info("\n" + "=" * 60)
            logger.info("🗑️ EXECUTING DELETIONS")
            logger.info("-" * 40)
            
            deleted_count = 0
            failed_count = 0
            
            for customer_handle, full_name in customers_to_delete:
                logger.info(f"\n🗑️ Deleting: {customer_handle} ({full_name})")
                
                success = self.delete_customer(customer_handle)
                if success:
                    deleted_count += 1
                    logger.info(f"✅ Deleted successfully")
                else:
                    failed_count += 1
                    logger.error(f"❌ Deletion failed")
                
                # Rate limiting - wait between deletions
                time.sleep(1)
            
            logger.info(f"\n" + "=" * 60)
            logger.info("📊 DELETION RESULTS")
            logger.info("-" * 40)
            logger.info(f"Successfully deleted: {deleted_count}")
            logger.info(f"Failed deletions: {failed_count}")
            logger.info(f"Total processed: {len(customers_to_delete)}")
        
        logger.info(f"\n✅ CLEANUP COMPLETE")
        if dry_run:
            logger.info("🔍 This was a dry run. Run with dry_run=False to execute deletions.")

def main():
    """Main function"""
    cleanup = OpenProviderCustomerCleanup()
    
    # First run in dry run mode to see what would be deleted
    print("=" * 80)
    print("🔍 RUNNING DRY RUN FIRST - NO ACTUAL DELETIONS")
    print("=" * 80)
    cleanup.run_cleanup(dry_run=True)
    
    # Ask user for confirmation
    print("\n" + "=" * 80)
    response = input("Do you want to proceed with actual deletions? (yes/no): ").strip().lower()
    
    if response == "yes":
        print("\n" + "=" * 80)
        print("⚠️ EXECUTING LIVE DELETIONS")
        print("=" * 80)
        cleanup.run_cleanup(dry_run=False)
    else:
        print("❌ Cleanup cancelled by user")

if __name__ == "__main__":
    main()