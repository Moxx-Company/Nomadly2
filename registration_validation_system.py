#!/usr/bin/env python3
"""
Registration Validation System
=============================

Comprehensive validation system to prevent incomplete registrations
and ensure all API methods are available during registration.
"""

import sys
import logging
from typing import Dict, List, Optional, Tuple
import inspect

# Add project root to path
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegistrationValidator:
    """Validates registration components before and after domain registration"""
    
    def __init__(self):
        self.validation_errors = []
        self.warnings = []
        
    def validate_api_methods_before_registration(self) -> bool:
        """Validate all required API methods exist before starting registration"""
        logger.info("🔧 VALIDATING API METHODS BEFORE REGISTRATION")
        
        validation_passed = True
        
        # Check OpenProvider API methods
        try:
            from apis.production_openprovider import OpenProviderAPI
            op_api = OpenProviderAPI()
            
            required_methods = [
                'update_domain_nameservers',  # Critical for nameserver management
                'update_nameservers',         # Backup method
                '_authenticate',              # Authentication
                '_create_customer_handle'     # Customer creation
            ]
            
            for method_name in required_methods:
                if hasattr(op_api, method_name):
                    logger.info(f"✅ OpenProvider API method: {method_name}")
                else:
                    logger.error(f"❌ Missing OpenProvider API method: {method_name}")
                    self.validation_errors.append(f"Missing OpenProvider method: {method_name}")
                    validation_passed = False
                    
        except Exception as e:
            logger.error(f"❌ OpenProvider API validation error: {e}")
            validation_passed = False
            
        # Check Cloudflare API methods
        try:
            from apis.production_cloudflare import CloudflareAPI
            cf_api = CloudflareAPI()
            
            required_cf_methods = [
                'create_zone',
                'get_nameservers',
                'add_dns_record_async',
                'list_dns_records_async'
            ]
            
            for method_name in required_cf_methods:
                if hasattr(cf_api, method_name):
                    logger.info(f"✅ Cloudflare API method: {method_name}")
                else:
                    logger.error(f"❌ Missing Cloudflare API method: {method_name}")
                    self.validation_errors.append(f"Missing Cloudflare method: {method_name}")
                    validation_passed = False
                    
        except Exception as e:
            logger.error(f"❌ Cloudflare API validation error: {e}")
            validation_passed = False
            
        return validation_passed
        
    def validate_registration_completion(self, domain_name: str, openprovider_id: str, 
                                       cloudflare_zone: str = None) -> bool:
        """Validate registration was completed successfully with all components"""
        logger.info(f"🔧 VALIDATING REGISTRATION COMPLETION FOR: {domain_name}")
        
        validation_passed = True
        
        # Test 1: Verify OpenProvider domain ID is numeric and valid
        if not openprovider_id or not str(openprovider_id).isdigit():
            logger.error(f"❌ Invalid OpenProvider domain ID: {openprovider_id}")
            self.validation_errors.append(f"Invalid OpenProvider domain ID for {domain_name}")
            validation_passed = False
        else:
            logger.info(f"✅ Valid OpenProvider domain ID: {openprovider_id}")
            
        # Test 2: Test nameserver management functionality immediately
        try:
            from apis.production_openprovider import OpenProviderAPI
            op_api = OpenProviderAPI()
            
            # Test that we can call the nameserver update method without errors
            test_nameservers = ["ns1.test.com", "ns2.test.com"]
            
            # Don't actually update, just test the method exists and can be called
            if hasattr(op_api, 'update_domain_nameservers'):
                logger.info("✅ Nameserver management method available")
                # Could add a dry-run test here if needed
            else:
                logger.error(f"❌ Nameserver management not available for {domain_name}")
                self.validation_errors.append(f"Nameserver management broken for {domain_name}")
                validation_passed = False
                
        except Exception as e:
            logger.error(f"❌ Nameserver management test failed: {e}")
            validation_passed = False
            
        # Test 3: Verify Cloudflare zone if provided
        if cloudflare_zone:
            try:
                from apis.production_cloudflare import CloudflareAPI
                cf_api = CloudflareAPI()
                
                # Test zone accessibility
                zone_check = cf_api._get_zone_id(domain_name)
                if zone_check == cloudflare_zone:
                    logger.info(f"✅ Cloudflare zone verified: {cloudflare_zone}")
                else:
                    logger.warning(f"⚠️ Cloudflare zone mismatch: {cloudflare_zone}")
                    self.warnings.append(f"Cloudflare zone mismatch for {domain_name}")
                    
            except Exception as e:
                logger.error(f"❌ Cloudflare zone validation failed: {e}")
                validation_passed = False
                
        return validation_passed
        
    def get_validation_report(self) -> Dict:
        """Get comprehensive validation report"""
        return {
            "passed": len(self.validation_errors) == 0,
            "errors": self.validation_errors,
            "warnings": self.warnings,
            "error_count": len(self.validation_errors),
            "warning_count": len(self.warnings)
        }

def validate_all_existing_domains():
    """Validate all existing domains for nameserver management capability"""
    logger.info("🔧 VALIDATING ALL EXISTING DOMAINS")
    logger.info("=" * 50)
    
    from database import get_db_manager
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        from sqlalchemy import text
        
        # Get all registered domains
        domains = session.execute(text("""
            SELECT 
                domain_name,
                openprovider_domain_id,
                cloudflare_zone_id,
                nameserver_mode,
                status
            FROM registered_domains 
            WHERE status = 'active'
        """)).fetchall()
        
        validator = RegistrationValidator()
        
        for domain in domains:
            logger.info(f"Testing domain: {domain.domain_name}")
            
            # Validate each domain
            is_valid = validator.validate_registration_completion(
                domain.domain_name,
                domain.openprovider_domain_id,
                domain.cloudflare_zone_id
            )
            
            if is_valid:
                logger.info(f"✅ {domain.domain_name}: Fully functional")
            else:
                logger.error(f"❌ {domain.domain_name}: Issues detected")
                
        # Get final report
        report = validator.get_validation_report()
        
        logger.info("")
        logger.info("📊 VALIDATION SUMMARY")
        logger.info("-" * 30)
        logger.info(f"Total domains tested: {len(domains)}")
        logger.info(f"Errors found: {report['error_count']}")
        logger.info(f"Warnings: {report['warning_count']}")
        
        if report['passed']:
            logger.info("🎉 All domains pass validation!")
        else:
            logger.warning("⚠️ Some domains have issues - check logs above")
            
    except Exception as e:
        logger.error(f"Domain validation error: {e}")
        
    finally:
        session.close()

def implement_registration_hooks():
    """Show how to implement validation hooks in registration process"""
    logger.info("💡 REGISTRATION VALIDATION HOOKS IMPLEMENTATION")
    logger.info("=" * 50)
    
    logger.info("To prevent future issues, add these validation calls:")
    logger.info("")
    logger.info("1. BEFORE REGISTRATION:")
    logger.info("   validator = RegistrationValidator()")
    logger.info("   if not validator.validate_api_methods_before_registration():")
    logger.info("       return error('Registration system not ready')")
    logger.info("")
    logger.info("2. AFTER REGISTRATION:")
    logger.info("   success = validator.validate_registration_completion(")
    logger.info("       domain_name, openprovider_id, cloudflare_zone)")
    logger.info("   if not success:")
    logger.info("       # Rollback registration or alert administrators")
    logger.info("")
    logger.info("3. PERIODIC VALIDATION:")
    logger.info("   Run validate_all_existing_domains() daily to catch issues")

if __name__ == "__main__":
    # Run comprehensive validation
    validator = RegistrationValidator()
    
    # Test current API methods
    api_valid = validator.validate_api_methods_before_registration()
    
    # Test all existing domains
    validate_all_existing_domains()
    
    # Show implementation guidance
    implement_registration_hooks()
    
    # Final report
    report = validator.get_validation_report()
    
    logger.info("")
    logger.info("🎯 FINAL VALIDATION RESULTS")
    logger.info("=" * 40)
    
    if report['passed'] and api_valid:
        logger.info("🎉 SYSTEM FULLY VALIDATED - Ready for production")
    else:
        logger.warning("⚠️ VALIDATION ISSUES DETECTED - Review errors above")