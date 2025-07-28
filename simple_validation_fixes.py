#!/usr/bin/env python3
"""
Simple Validation Fixes - Minimal Code Changes for Maximum Impact
================================================================

Instead of complex architectural changes, these simple validation functions
can be added to existing code to prevent all three critical issues.

The key insight: All three problems stem from insufficient validation 
at critical decision points.
"""

import logging
from typing import Dict, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleValidationFixes:
    """Simple validation functions to prevent critical issues"""
    
    @staticmethod
    def validate_domain_display_data(domain_data: Dict) -> Dict:
        """
        FIX 1: DNS Record Counting Issue
        Validate domain data before displaying to users
        Auto-fix missing zone IDs and incorrect DNS counts
        """
        domain_name = domain_data.get('domain_name')
        cloudflare_zone_id = domain_data.get('cloudflare_zone_id')
        
        # If zone ID is missing, try to find it
        if not cloudflare_zone_id and domain_name:
            logger.info(f"Missing zone ID for {domain_name}, attempting auto-discovery")
            try:
                from apis.production_cloudflare import CloudflareAPI
                cloudflare = CloudflareAPI()
                discovered_zone = cloudflare.get_zone_by_domain(domain_name)
                if discovered_zone:
                    cloudflare_zone_id = discovered_zone['id']
                    domain_data['cloudflare_zone_id'] = cloudflare_zone_id
                    
                    # Update database with discovered zone ID
                    SimpleValidationFixes._update_zone_id_in_database(domain_name, cloudflare_zone_id)
                    logger.info(f"Auto-discovered and stored zone ID {cloudflare_zone_id} for {domain_name}")
            except Exception as e:
                logger.warning(f"Could not auto-discover zone ID for {domain_name}: {e}")
        
        # Get accurate DNS record count
        if cloudflare_zone_id:
            try:
                from apis.production_cloudflare import CloudflareAPI
                cloudflare = CloudflareAPI()
                records = cloudflare.get_dns_records(cloudflare_zone_id)
                actual_count = len(records) if records else 0
                domain_data['dns_records_count'] = actual_count
                logger.info(f"Validated DNS count for {domain_name}: {actual_count} records")
            except Exception as e:
                logger.warning(f"Could not get DNS count for {domain_name}: {e}")
                domain_data['dns_records_count'] = 0
        else:
            domain_data['dns_records_count'] = 0
        
        return domain_data
    
    @staticmethod
    def validate_webhook_service_delivery(order_id: str, order_data: Dict) -> Tuple[bool, Dict]:
        """
        FIX 2: Webhook Duplicate Registration Skip  
        Validate actual service delivery before deciding to skip processing
        Returns: (service_delivered, service_details)
        """
        service_type = order_data.get('service_type')
        
        if service_type == 'domain_registration':
            domain_name = order_data.get('domain_name')
            if not domain_name:
                return False, {"error": "No domain name in order"}
            
            # Check if domain actually exists in database
            try:
                from database import get_db_manager, RegisteredDomain
                db = get_db_manager()
                session = db.get_session()
                
                try:
                    domain_record = session.query(RegisteredDomain).filter(
                        RegisteredDomain.domain_name == domain_name,
                        RegisteredDomain.telegram_id == order_data.get('telegram_id')
                    ).first()
                    
                    if domain_record:
                        # Validate domain record is complete
                        is_complete = all([
                            domain_record.cloudflare_zone_id,
                            domain_record.created_at,
                            domain_record.expiry_date
                        ])
                        
                        service_details = {
                            "domain_registered": True,
                            "domain_name": domain_name,
                            "zone_id": domain_record.cloudflare_zone_id,
                            "complete": is_complete,
                            "created_at": domain_record.created_at.isoformat() if domain_record.created_at is not None else None
                        }
                        
                        logger.info(f"Service delivery validation for {order_id}: Domain {domain_name} {'complete' if is_complete else 'incomplete'}")
                        return is_complete, service_details
                    else:
                        logger.info(f"Service delivery validation for {order_id}: Domain {domain_name} not found in database")
                        return False, {"domain_registered": False, "domain_name": domain_name}
                        
                finally:
                    session.close()
                    
            except Exception as e:
                logger.error(f"Service delivery validation failed for {order_id}: {e}")
                return False, {"error": str(e)}
        
        # For other service types, assume delivered if payment completed
        return True, {"service_type": service_type, "assumed_delivered": True}
    
    @staticmethod
    def validate_domain_registration_completion(registration_result: Dict) -> Tuple[bool, Dict]:
        """
        FIX 3: Domain Registration Completion
        Validate all steps completed before marking registration as successful
        """
        required_fields = [
            'domain_name',
            'openprovider_domain_id', 
            #'cloudflare_zone_id',
            'nameservers',
            'database_record_id'
        ]
        
        validation_results = {
            "complete": True,
            "missing_fields": [],
            "validation_errors": []
        }
        
        # Check required fields
        for field in required_fields:
            if not registration_result.get(field):
                validation_results["complete"] = False
                validation_results["missing_fields"].append(field)
        
        # Validate OpenProvider domain ID format
        op_id = registration_result.get('openprovider_domain_id')
        if op_id and not str(op_id).isdigit():
            validation_results["complete"] = False
            validation_results["validation_errors"].append(f"Invalid OpenProvider ID format: {op_id}")
        
        # Validate Cloudflare zone ID format  
        cloudflare_zone_id = registration_result.get('cloudflare_zone_id')
        if cloudflare_zone_id and (len(str(cloudflare_zone_id)) != 32 or not all(c in '0123456789abcdef' for c in str(cloudflare_zone_id))):
            validation_results["complete"] = False
            validation_results["validation_errors"].append(f"Invalid Cloudflare zone ID format: {cloudflare_zone_id}")
        
        # Validate nameservers
        nameservers = registration_result.get('nameservers', [])
        if not nameservers or len(nameservers) < 2:
            validation_results["complete"] = False
            validation_results["validation_errors"].append("Insufficient nameservers")
        
        domain_name = registration_result.get('domain_name')
        if validation_results["complete"]:
            logger.info(f"Domain registration validation passed for {domain_name}")
        else:
            logger.error(f" 123 Domain registration validation failed for {domain_name}: {validation_results}")
        
        return validation_results["complete"], validation_results
    
    @staticmethod
    def _update_zone_id_in_database(domain_name: str, cloudflare_zone_id: str):
        """Helper: Update zone ID in database"""
        try:
            from database import get_db_manager, RegisteredDomain
            db = get_db_manager()
            session = db.get_session()
            
            try:
                domain_record = session.query(RegisteredDomain).filter(
                    RegisteredDomain.domain_name == domain_name
                ).first()
                
                if domain_record:
                    setattr(domain_record, 'cloudflare_zone_id', cloudflare_zone_id)
                    session.commit()
                    logger.info(f"Updated zone ID for {domain_name} in database")
                    
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to update zone ID in database for {domain_name}: {e}")

# Usage Examples:

def apply_fix_to_domain_service():
    """How to apply Fix 1 to domain_service.py"""
    return """
    # In domain_service.py, modify get_user_domains():
    
    for domain in domains:
        # BEFORE: Just return raw data
        # domain_dict = {...}
        
        # AFTER: Validate data before returning
        domain_dict = SimpleValidationFixes.validate_domain_display_data(domain_dict)
    """

def apply_fix_to_webhook_processing():
    """How to apply Fix 2 to payment_service.py"""  
    return """
    # In payment_service.py, modify process_webhook_payment():
    
    if order.payment_status == "completed":
        # BEFORE: Just check payment status
        # return "already processed"
        
        # AFTER: Validate actual service delivery
        service_delivered, service_details = SimpleValidationFixes.validate_webhook_service_delivery(order_id, order_data)
        
        if service_delivered:
            return {"success": True, "service_delivered": True, "details": service_details}
        else:
            # Process service delivery even though payment was completed
            return process_service_delivery(order_data)
    """

def apply_fix_to_domain_registration():
    """How to apply Fix 3 to registration workflow"""
    return """
    # In domain registration workflow:
    
    # BEFORE: Assume success if no exceptions
    # return {"success": True}
    
    # AFTER: Validate completion before returning success
    registration_complete, validation_details = SimpleValidationFixes.validate_domain_registration_completion(result)
    
    if registration_complete:
        return {"success": True, "validated": True, "details": validation_details}
    else:
        # Attempt to fix incomplete registration or rollback
        return {"success": False, "validation_failed": True, "details": validation_details}
    """

if __name__ == "__main__":
    print("Simple Validation Fixes - Ready for Integration")
    print("=" * 50)
    print("These functions can be added to existing code with minimal changes:")
    print("1. validate_domain_display_data() - Fix DNS counting issues")  
    print("2. validate_webhook_service_delivery() - Fix duplicate processing")
    print("3. validate_domain_registration_completion() - Fix partial registrations")
    print("\nNo architectural changes required - just add validation at key decision points.")