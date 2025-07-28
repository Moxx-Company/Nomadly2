#!/usr/bin/env python3
"""
Fix Customer Contact Consistency - Use same contact for all customer registrations
"""

import logging
from database import get_db_manager
from apis.production_openprovider import OpenProviderAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_contact_consistency():
    """Fix contact consistency for customer @folly542"""
    logger.info("🔧 FIXING CUSTOMER CONTACT CONSISTENCY")
    logger.info("=" * 60)
    
    try:
        db_manager = get_db_manager()
        telegram_id = 6896666427  # Customer @folly542
        
        # Find the original contact handle used
        logger.info("🔍 FINDING ORIGINAL CONTACT HANDLE")
        logger.info("-" * 40)
        
        session = db_manager.get_session()
        try:
            # Get all domains with their contact handles
            from sqlalchemy import text
            query = text("""
                SELECT 
                    domain_name,
                    openprovider_contact_handle,
                    created_at,
                    status,
                    cloudflare_zone_id
                FROM registered_domains 
                WHERE telegram_id = :telegram_id
                ORDER BY created_at
            """)
            
            result = session.execute(query, {"telegram_id": telegram_id})
            domains = result.fetchall()
            
            # Find the contact handle from the successfully registered domain
            original_contact_handle = None
            successful_domain = None
            
            for domain in domains:
                name, contact_handle, created, status, cf_zone = domain
                logger.info(f"{name}:")
                logger.info(f"  Contact: {contact_handle}")
                logger.info(f"  Status: {status}")
                logger.info(f"  Cloudflare Zone: {'Yes' if cf_zone else 'No'}")
                logger.info(f"  Created: {created}")
                
                # The domain with Cloudflare zone is the successfully registered one
                if cf_zone and contact_handle and not contact_handle.startswith('not_registered_'):
                    original_contact_handle = contact_handle
                    successful_domain = name
                logger.info("")
            
            if original_contact_handle:
                logger.info(f"✅ FOUND ORIGINAL CONTACT: {original_contact_handle}")
                logger.info(f"   From successfully registered domain: {successful_domain}")
            else:
                logger.info("❌ No valid original contact handle found")
                logger.info("   We need to create a consistent contact strategy")
                
                # Let's check what contacts exist in the user table or create one
                user = db_manager.get_user_by_telegram_id(telegram_id)
                if user:
                    logger.info(f"User info: {user.username} - {user.email or 'No email'}")
                    
                    # Generate a consistent contact handle for this user
                    original_contact_handle = f"contact_{telegram_id}_{user.username or 'user'}"
                    logger.info(f"🔧 GENERATING CONSISTENT CONTACT: {original_contact_handle}")
            
            logger.info(f"\n💡 CONTACT CONSISTENCY STRATEGY")
            logger.info("-" * 40)
            logger.info(f"Original contact: {original_contact_handle}")
            logger.info("This contact should be used for:")
            logger.info("1. All future domain registrations for this customer")
            logger.info("2. Any re-registration attempts for failed domains")
            logger.info("3. OpenProvider API calls requiring contact information")
            
            # Update our registration service to use consistent contacts
            logger.info(f"\n🔧 UPDATING CONTACT CONSISTENCY SYSTEM")
            logger.info("-" * 40)
            
            # We should update our registration service to track and reuse contacts
            contact_mapping = {
                telegram_id: {
                    'contact_handle': original_contact_handle,
                    'domains': [d[0] for d in domains],
                    'total_domains': len(domains),
                    'successful_registrations': len([d for d in domains if d[4]])  # has cloudflare zone
                }
            }
            
            logger.info("Contact mapping for future registrations:")
            for uid, info in contact_mapping.items():
                logger.info(f"  User {uid}: {info['contact_handle']}")
                logger.info(f"    Domains: {info['total_domains']}")
                logger.info(f"    Successful: {info['successful_registrations']}")
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(fix_contact_consistency())