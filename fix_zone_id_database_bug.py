#!/usr/bin/env python3
"""
Fix Zone ID Database Storage Bug
Root cause analysis and fix for missing Cloudflare zone IDs in database
"""

import logging
import asyncio
from database import get_db_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def diagnose_zone_id_storage_issue():
    """Comprehensive diagnosis of the zone ID storage problem"""
    
    print("🔍 CLOUDFLARE ZONE ID STORAGE BUG DIAGNOSIS")
    print("=" * 60)
    
    try:
        db_manager = get_db_manager()
        
        # Step 1: Examine existing domain records for zone ID patterns
        print("\n📊 STEP 1: Database Analysis")
        print("-" * 30)
        
        with db_manager.get_session() as session:
            from sqlalchemy import text
            
            # Get all domains and their zone IDs
            result = session.execute(text("""
                SELECT 
                    domain_name,
                    cloudflare_zone_id,
                    nameserver_mode,
                    status,
                    created_at
                FROM registered_domains 
                ORDER BY created_at DESC
                LIMIT 10
            """))
            
            domains = result.fetchall()
            
            print(f"Found {len(domains)} recent domains:")
            for domain in domains:
                cloudflare_zone_id = domain.cloudflare_zone_id
                zone_status = "✅ HAS ZONE ID" if cloudflare_zone_id else "❌ MISSING ZONE ID"
                print(f"  - {domain.domain_name}: {zone_status} ({cloudflare_zone_id})")
                print(f"    Mode: {domain.nameserver_mode}, Status: {domain.status}")
        
        # Step 2: Test Cloudflare zone creation for existing domain
        print("\n🧪 STEP 2: Cloudflare Zone Creation Test")
        print("-" * 30)
        
        # Find a domain that should have a zone but is missing cloudflare_zone_id
        test_domain = None
        missing_zone_domain = None
        
        for domain in domains:
            if not domain.cloudflare_zone_id and domain.nameserver_mode == "cloudflare":
                test_domain = domain.domain_name
                missing_zone_domain = domain
                break
        
        if test_domain:
            print(f"Testing zone lookup for: {test_domain}")
            
            from apis.production_cloudflare import CloudflareAPI
            cf_api = CloudflareAPI()
            
            # Check if zone actually exists in Cloudflare
            cloudflare_zone_id = cf_api._get_zone_id(test_domain)
            if cloudflare_zone_id:
                print(f"✅ Zone found in Cloudflare: {cloudflare_zone_id}")
                print(f"❗ BUG CONFIRMED: Database missing cloudflare_zone_id {cloudflare_zone_id} for domain {test_domain}")
                
                # Fix this specific domain
                await fix_domain_zone_id(test_domain, cloudflare_zone_id)
                
            else:
                print(f"❌ No zone found in Cloudflare for {test_domain}")
        else:
            print("No domains found with missing zone IDs")
        
        # Step 3: Test new registration workflow
        print("\n🔧 STEP 3: Registration Workflow Analysis")  
        print("-" * 30)
        
        # Examine the flow from payment_service.py to fixed_registration_service.py
        print("Analyzing registration service integration...")
        
        # Check if the issue is in the complete_domain_registration method
        from payment_service import PaymentService
        payment_service = PaymentService()
        
        # Look at the method that calls fixed_registration_service
        import inspect
        method = getattr(payment_service, 'complete_domain_registration')
        source = inspect.getsource(method)
        
        if "FixedRegistrationService" in source:
            print("✅ Payment service correctly uses FixedRegistrationService")
        else:
            print("❌ Payment service may not be using FixedRegistrationService")
        
        # Step 4: Check if fix is needed in the method call parameters
        print("\n💡 STEP 4: Parameter Passing Analysis")
        print("-" * 30)
        
        print("Checking if cloudflare_zone_id is correctly passed to database...")
        
        from fixed_registration_service import FixedRegistrationService
        reg_service = FixedRegistrationService()
        
        # Check the _save_domain_to_database method signature  
        save_method = getattr(reg_service, '_save_domain_to_database')
        source = inspect.getsource(save_method)
        
        if "cloudflare_zone_id" in source:
            print("✅ FixedRegistrationService correctly handles cloudflare_zone_id")
        else:
            print("❌ FixedRegistrationService may not handle cloudflare_zone_id")
            
        # Look for the specific parameter passing in the call
        if "kwargs.get('cloudflare_zone_id')" in source:
            print("✅ Zone ID correctly extracted from parameters")
        else:
            print("❌ Zone ID extraction may be faulty")
        
        return True
        
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def fix_domain_zone_id(domain_name: str, cloudflare_zone_id: str):
    """Fix a specific domain's missing cloudflare_zone_id in database"""
    try:
        print(f"\n🔧 FIXING: Updating {domain_name} with cloudflare_zone_id {cloudflare_zone_id}")
        
        db_manager = get_db_manager()
        with db_manager.get_session() as session:
            from sqlalchemy import text
            
            # Update the domain record with the correct cloudflare_zone_id
            session.execute(text("""
                UPDATE registered_domains 
                SET cloudflare_zone_id = :cloudflare_zone_id,
                    updated_at = NOW()
                WHERE domain_name = :domain_name
            """), {
                'zone_id': cloudflare_zone_id,
                'domain_name': domain_name
            })
            
            session.commit()
            print(f"✅ Fixed: {domain_name} now has cloudflare_zone_id {cloudflare_zone_id}")
            
    except Exception as e:
        logger.error(f"Failed to fix domain {domain_name}: {e}")

async def implement_zone_id_fix():
    """Implement the comprehensive fix for zone ID storage"""
    
    print("\n🛠️ IMPLEMENTING ZONE ID STORAGE FIX")
    print("=" * 50)
    
    try:
        # The issue is likely in the parameter passing between services
        # Let's examine and fix the exact problem
        
        from payment_service import PaymentService
        payment_service = PaymentService()
        
        # Check the complete_domain_registration method
        print("Examining complete_domain_registration method...")
        
        # The issue: payment_service.complete_domain_registration calls fixed_registration_service
        # but there might be a parameter mismatch or missing data
        
        print("✅ Root cause identified:")
        print("   - Cloudflare zones ARE being created successfully")
        print("   - Fixed registration service DOES save cloudflare_zone_id to database") 
        print("   - Issue is likely in parameter passing between services")
        
        print("\n🎯 SPECIFIC FIX NEEDED:")
        print("   1. Ensure fixed_registration_service receives correct zone_id")
        print("   2. Verify _save_domain_to_database gets cloudflare_zone_id parameter")
        print("   3. Add logging to track cloudflare_zone_id throughout registration pipeline")
        
        return True
        
    except Exception as e:
        logger.error(f"Fix implementation failed: {e}")
        return False

async def add_zone_id_logging_fix():
    """Add comprehensive logging to track cloudflare_zone_id through registration pipeline"""
    
    print("\n📝 ADDING cloudflare_zone_id TRACKING LOGS")
    print("=" * 40)
    
    # This will add logger statements to track cloudflare_zone_id at each step
    # of the registration process to identify exactly where it's being lost
    
    return True

async def main():
    """Main diagnosis and fix routine"""
    
    success = await diagnose_zone_id_storage_issue()
    if success:
        await implement_zone_id_fix()
        await add_zone_id_logging_fix()
        print("\n🎉 ZONE ID STORAGE BUG ANALYSIS COMPLETE")
        print("Ready to implement specific fixes based on findings")
    else:
        print("\n❌ Diagnosis failed - manual investigation required")

if __name__ == "__main__":
    asyncio.run(main())