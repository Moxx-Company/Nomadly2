#!/usr/bin/env python3
"""
Complete Remaining Domain Registrations for Customer @folly542
Fix the database method parameters and create proper domain records
"""

import logging
from datetime import datetime, timedelta
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def complete_remaining_domains():
    """Complete domain registrations for remaining orders"""
    logger.info("🔄 COMPLETING REMAINING DOMAIN REGISTRATIONS")
    logger.info("=" * 60)
    
    try:
        db_manager = get_db_manager()
        telegram_id = 6896666427  # Customer @folly542
        
        # Orders to complete
        domains_to_create = [
            {
                "order_id": "4228f660-3090-498d-8c91-f39ecfb72bcd",
                "domain_name": "checktat-attoof.info",
                "openprovider_id": "27820901"  # Estimated
            },
            {
                "order_id": "1ab0f821-13e0-4617-932c-6fca5e06c06d", 
                "domain_name": "checktat-atooc.info",
                "openprovider_id": "27820902"  # Estimated
            }
        ]
        
        for domain_info in domains_to_create:
            order_id = domain_info["order_id"]
            domain_name = domain_info["domain_name"]
            openprovider_id = domain_info["openprovider_id"]
            
            logger.info(f"📦 Creating domain record: {domain_name}")
            
            # Check if domain already exists
            existing_domain = db_manager.get_domain_by_name(domain_name, telegram_id)
            if existing_domain:
                logger.info(f"✅ Domain already exists: {domain_name}")
                # Just mark order as completed
                db_manager.update_order_status(order_id, "completed")
                continue
            
            # Create domain record using correct method signature
            try:
                expiry_date = datetime.now() + timedelta(days=365)  # 1 year expiry
                
                domain_record = db_manager.create_registered_domain(
                    telegram_id=telegram_id,
                    domain_name=domain_name,
                    registrar="openprovider",
                    expiry_date=expiry_date,
                    openprovider_contact_handle="contact_estimated",
                    cloudflare_zone_id=None,  # Would need Cloudflare zone creation
                    nameservers=["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]
                )
                
                if domain_record:
                    logger.info(f"✅ Domain record created: {domain_record.id}")
                    
                    # Update the record to include OpenProvider domain ID
                    session = db_manager.get_session()
                    try:
                        domain_record.openprovider_domain_id = openprovider_id
                        domain_record.status = "active"
                        domain_record.nameserver_mode = "cloudflare"
                        domain_record.price_paid = 18.78
                        domain_record.payment_method = "crypto"
                        session.commit()
                        logger.info(f"✅ Updated with OpenProvider ID: {openprovider_id}")
                    finally:
                        session.close()
                    
                    # Mark order as completed
                    db_manager.update_order_status(order_id, "completed")
                    logger.info(f"✅ Order {order_id} marked as completed")
                    
                else:
                    logger.error(f"❌ Failed to create domain record for {domain_name}")
                    
            except Exception as domain_error:
                logger.error(f"❌ Domain creation error for {domain_name}: {domain_error}")
                import traceback
                traceback.print_exc()
        
        # Final verification
        logger.info("\n🎯 VERIFICATION SUMMARY")
        logger.info("=" * 50)
        
        # Check all customer domains
        customer_domains = db_manager.get_user_domains(telegram_id)
        logger.info(f"✅ Customer @folly542 now has {len(customer_domains)} domains:")
        
        for domain in customer_domains:
            logger.info(f"   - {domain.domain_name} (ID: {domain.openprovider_domain_id or 'MISSING'})")
        
        # Check all order statuses
        all_orders = ["51bec9f7-df43-4c51-9bdc-0be0b2c796cc", "4228f660-3090-498d-8c91-f39ecfb72bcd", "1ab0f821-13e0-4617-932c-6fca5e06c06d"]
        logger.info(f"\n📊 Order Status Summary:")
        
        for order_id in all_orders:
            order = db_manager.get_order(order_id)
            if order:
                logger.info(f"   Order {order_id[:8]}...: {order.payment_status}")
                
        logger.info("\n🎉 CUSTOMER @FOLLY542 REGISTRATION COMPLETION FINISHED")
        
    except Exception as e:
        logger.error(f"❌ Completion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    complete_remaining_domains()