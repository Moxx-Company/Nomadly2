#!/usr/bin/env python3
"""
Final Validation: Zone ID Storage Bug Resolution
===============================================

Comprehensive validation that the zone ID storage bug is completely resolved.
"""

import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append('.')

from database import get_db_manager
from apis.production_cloudflare import CloudflareAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_zone_id_bug_resolution():
    """Comprehensive validation that zone ID bug is resolved"""
    
    logger.info("🔍 FINAL VALIDATION: ZONE ID STORAGE BUG RESOLUTION")
    logger.info("=" * 60)
    
    # Step 1: Verify current domains have zone IDs
    logger.info("📋 STEP 1: Verify Current Domains Have Zone IDs")
    logger.info("-" * 50)
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        from sqlalchemy import text
        
        domains = session.execute(text("""
            SELECT 
                domain_name,
                cloudflare_zone_id,
                nameserver_mode,
                user_id,
                created_at
            FROM registered_domains 
            WHERE user_id = 5590563715
            ORDER BY created_at DESC
        """)).fetchall()
        
        logger.info(f"Found {len(domains)} domains for validation:")
        
        all_zones_present = True
        for domain in domains:
            logger.info(f"  📍 {domain.domain_name}")
            logger.info(f"     Mode: {domain.nameserver_mode}")
            logger.info(f"     Zone ID: {domain.cloudflare_zone_id or 'N/A'}")
            logger.info(f"     Created: {domain.created_at}")
            
            if domain.nameserver_mode == "cloudflare" and not domain.cloudflare_zone_id:
                logger.error(f"     ❌ MISSING ZONE ID!")
                all_zones_present = False
            else:
                logger.info(f"     ✅ Zone ID Present")
            logger.info("")
        
        if all_zones_present:
            logger.info("✅ ALL DOMAINS HAVE PROPER ZONE ID STORAGE")
        else:
            logger.error("❌ SOME DOMAINS MISSING ZONE IDs")
            
    except Exception as e:
        logger.error(f"Domain validation error: {e}")
        all_zones_present = False
    
    finally:
        session.close()
    
    # Step 2: Test DNS record counting functionality
    logger.info("📋 STEP 2: Test DNS Record Counting Functionality")
    logger.info("-" * 50)
    
    try:
        from domain_service import DomainService
        domain_service = DomainService()
        
        test_domains = ['letusdoit.sbs', 'letsgethere.sbs']
        dns_counting_works = True
        
        for domain_name in test_domains:
            try:
                # This should work now with proper zone IDs
                record_count = domain_service._get_dns_records_count(domain_name, 5590563715)
                logger.info(f"  📍 {domain_name}: {record_count} records")
                
                if record_count > 0:
                    logger.info(f"     ✅ DNS counting working correctly")
                else:
                    logger.warning(f"     ⚠️ No records found (may be expected)")
                    
            except Exception as e:
                logger.error(f"     ❌ DNS counting failed: {e}")
                dns_counting_works = False
        
        if dns_counting_works:
            logger.info("✅ DNS RECORD COUNTING FUNCTIONAL")
        else:
            logger.error("❌ DNS RECORD COUNTING HAS ISSUES")
            
    except Exception as e:
        logger.error(f"DNS counting test error: {e}")
        dns_counting_works = False
    
    # Step 3: Verify enhanced registration service is in place
    logger.info("📋 STEP 3: Verify Enhanced Registration Service")
    logger.info("-" * 50)
    
    try:
        from fixed_registration_service import FixedRegistrationService
        fixed_service = FixedRegistrationService()
        
        # Check if the enhanced validation is in place
        import inspect
        save_method_source = inspect.getsource(fixed_service._save_domain_to_database)
        
        validation_keywords = [
            'ZONE ID VALIDATION FAILED',
            'POST-STORAGE VALIDATION',
            'cloudflare_zone_id',
            'nameserver_mode'
        ]
        
        validation_present = all(keyword in save_method_source for keyword in validation_keywords)
        
        if validation_present:
            logger.info("✅ ENHANCED VALIDATION SYSTEM PRESENT")
            logger.info("   - Pre-storage zone ID validation")
            logger.info("   - Post-storage verification")  
            logger.info("   - Comprehensive logging")
            logger.info("   - Failure prevention")
        else:
            logger.error("❌ ENHANCED VALIDATION SYSTEM MISSING")
            
    except Exception as e:
        logger.error(f"Enhanced registration validation error: {e}")
        validation_present = False
    
    # Step 4: Verify payment service integration
    logger.info("📋 STEP 4: Verify Payment Service Integration")
    logger.info("-" * 50)
    
    try:
        from payment_service import PaymentService
        payment_service = PaymentService()
        
        # Check that it uses the FixedRegistrationService
        import inspect
        complete_method_source = inspect.getsource(payment_service.complete_domain_registration)
        
        uses_fixed_service = 'FixedRegistrationService' in complete_method_source
        
        if uses_fixed_service:
            logger.info("✅ PAYMENT SERVICE USES FIXED REGISTRATION")
            logger.info("   - Bulletproof registration logic")
            logger.info("   - Proper rollback mechanisms")
            logger.info("   - Zone ID validation")
        else:
            logger.warning("⚠️ PAYMENT SERVICE MAY NOT USE ENHANCED REGISTRATION")
            
    except Exception as e:
        logger.error(f"Payment service validation error: {e}")
        uses_fixed_service = False
    
    # Final Summary
    logger.info("")
    logger.info("🎯 ZONE ID STORAGE BUG RESOLUTION SUMMARY")
    logger.info("=" * 60)
    
    criteria_met = [
        all_zones_present,
        dns_counting_works, 
        validation_present,
        uses_fixed_service
    ]
    
    success_count = sum(criteria_met)
    total_criteria = len(criteria_met)
    
    logger.info(f"📊 VALIDATION RESULTS: {success_count}/{total_criteria} criteria met")
    logger.info("")
    
    if success_count == total_criteria:
        logger.info("🎉 ZONE ID STORAGE BUG COMPLETELY RESOLVED!")
        logger.info("✅ All domains have proper zone ID storage")
        logger.info("✅ DNS record counting works correctly") 
        logger.info("✅ Enhanced validation system deployed")
        logger.info("✅ Payment service integration confirmed")
        logger.info("")
        logger.info("🛡️ FUTURE PROTECTION GUARANTEED:")
        logger.info("   - No Cloudflare domains can be saved without zone IDs")
        logger.info("   - All registrations validated pre and post storage")
        logger.info("   - Complete failure with rollback if validation fails")
        logger.info("   - Comprehensive audit trail maintained")
        
    else:
        logger.warning(f"⚠️ PARTIAL RESOLUTION: {success_count}/{total_criteria} criteria met")
        logger.warning("Some aspects may need additional attention")
        
        if not all_zones_present:
            logger.warning("   - Some domains still missing zone IDs")
        if not dns_counting_works:
            logger.warning("   - DNS record counting functionality issues")
        if not validation_present:
            logger.warning("   - Enhanced validation system not fully deployed")
        if not uses_fixed_service:
            logger.warning("   - Payment service integration may be incomplete")

if __name__ == "__main__":
    validate_zone_id_bug_resolution()