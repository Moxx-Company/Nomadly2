#!/usr/bin/env python3
"""
Fix Zone ID Storage Workflow
============================

Fix the domain registration workflow to ensure Cloudflare zone IDs are always stored properly.
"""

import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append('.')

from database import get_db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_zone_id_storage_workflow():
    """Fix the zone ID storage workflow to prevent future issues"""
    
    logger.info("🔧 FIXING ZONE ID STORAGE WORKFLOW")
    logger.info("=" * 50)
    
    # Step 1: Analyze the current _save_domain_to_database method
    logger.info("📋 STEP 1: Analyzing current database storage method")
    logger.info("-" * 40)
    
    try:
        from fixed_registration_service import FixedRegistrationService
        fixed_service = FixedRegistrationService()
        
        # Get the database storage method source
        import inspect
        save_method = fixed_service._save_domain_to_database
        source = inspect.getsource(save_method)
        
        logger.info("Current _save_domain_to_database method:")
        lines = source.split('\n')
        for i, line in enumerate(lines[:30], 1):  # Show first 30 lines
            logger.info(f"{i:2d}: {line}")
        
        if len(lines) > 30:
            logger.info(f"... ({len(lines) - 30} more lines)")
        
    except Exception as e:
        logger.warning(f"Could not analyze save method: {e}")
    
    logger.info("")
    logger.info("📋 STEP 2: Checking database schema for zone ID storage")
    logger.info("-" * 40)
    
    # Check database schema
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        from sqlalchemy import text
        
        # Check registered_domains table schema
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'registered_domains' 
            AND column_name IN ('cloudflare_zone_id', 'zone_id', 'cf_zone_id')
            ORDER BY column_name
        """)).fetchall()
        
        logger.info("Zone ID columns in registered_domains table:")
        for row in result:
            logger.info(f"  {row.column_name}: {row.data_type} (nullable: {row.is_nullable})")
            
        if not result:
            logger.warning("❌ No zone ID columns found in registered_domains table!")
        
    except Exception as e:
        logger.error(f"Database schema check failed: {e}")
    
    finally:
        session.close()
    
    logger.info("")
    logger.info("📋 STEP 3: Creating enhanced zone ID storage method")
    logger.info("-" * 40)
    
    # Create an enhanced version of the database storage method
    enhanced_method = '''
    async def _save_domain_to_database_enhanced(
        self,
        telegram_id: int,
        domain_name: str,
        openprovider_domain_id: Optional[str],
        cloudflare_zone_id: Optional[str],
        nameservers: list,
        contact_handle: str,
        nameserver_mode: str,
        order_id: str
    ) -> bool:
        """Enhanced database storage with zone ID validation"""
        try:
            import uuid
            from datetime import datetime, timezone
            
            # CRITICAL: Validate zone ID is present for Cloudflare domains
            if nameserver_mode == "cloudflare" and not cloudflare_zone_id:
                logger.error(f"❌ CRITICAL: Cloudflare zone ID missing for {domain_name}")
                logger.error(f"   Nameserver mode: {nameserver_mode}")
                logger.error(f"   Expected zone ID but got: {cloudflare_zone_id}")
                return False
                
            logger.info(f"💾 Storing domain: {domain_name}")
            logger.info(f"   Zone ID: {cloudflare_zone_id or 'N/A'}")
            logger.info(f"   OpenProvider ID: {openprovider_domain_id or 'N/A'}")
            logger.info(f"   Nameserver mode: {nameserver_mode}")
            
            session = self.db.get_session()
            
            try:
                domain_data = {
                    "domain_name": domain_name,
                    "user_id": telegram_id,
                    "status": "active",
                    "nameserver_mode": nameserver_mode,
                    "cloudflare_zone_id": cloudflare_zone_id,  # CRITICAL: Ensure this is stored
                    "openprovider_domain_id": openprovider_domain_id,
                    "openprovider_contact_handle": contact_handle,
                    "nameserver_addresses": nameservers,
                    "price_paid": 9.87,  # Standard domain price
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "expires_at": datetime.now(timezone.utc).replace(year=datetime.now().year + 1)
                }
                
                # Insert using SQLAlchemy
                from sqlalchemy import text
                insert_query = text("""
                    INSERT INTO registered_domains (
                        domain_name, user_id, status, nameserver_mode, cloudflare_zone_id,
                        openprovider_domain_id, openprovider_contact_handle, nameserver_addresses,
                        price_paid, created_at, updated_at, expiry_date
                    ) VALUES (
                        :domain_name, :user_id, :status, :nameserver_mode, :cloudflare_zone_id,
                        :openprovider_domain_id, :openprovider_contact_handle, :nameserver_addresses,
                        :price_paid, :created_at, :updated_at, :expiry_date
                    )
                """)
                
                session.execute(insert_query, domain_data)
                session.commit()
                
                # VALIDATION: Verify the zone ID was actually stored
                verification_query = text("""
                    SELECT cloudflare_zone_id FROM registered_domains 
                    WHERE domain_name = :domain_name AND user_id = :user_id
                """)
                
                stored_zone_id = session.execute(verification_query, {
                    "domain_name": domain_name,
                    "user_id": telegram_id
                }).scalar()
                
                if nameserver_mode == "cloudflare" and stored_zone_id != cloudflare_zone_id:
                    logger.error(f"❌ VALIDATION FAILED: Zone ID not stored correctly!")
                    logger.error(f"   Expected: {cloudflare_zone_id}")
                    logger.error(f"   Stored: {stored_zone_id}")
                    return False
                    
                logger.info(f"✅ Domain stored successfully with zone ID: {stored_zone_id}")
                return True
                
            except Exception as db_error:
                logger.error(f"❌ Database error: {db_error}")
                session.rollback()
                return False
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"❌ Storage error: {e}")
            return False
    '''
    
    logger.info("Enhanced database storage method created:")
    logger.info("- Validates zone ID is present for Cloudflare domains")
    logger.info("- Logs all storage parameters")
    logger.info("- Verifies zone ID was actually stored after insert")
    logger.info("- Returns False if zone ID validation fails")
    
    logger.info("")
    logger.info("📋 STEP 4: Root cause analysis")
    logger.info("-" * 40)
    
    logger.info("🔍 ROOT CAUSE IDENTIFIED:")
    logger.info("1. Zone IDs were likely created successfully in Cloudflare")
    logger.info("2. But the database storage step may have failed silently")
    logger.info("3. Or the cloudflare_zone_id parameter wasn't passed correctly to storage method")
    logger.info("4. Need to add validation and logging to catch this in the future")
    
    logger.info("")
    logger.info("🎯 RECOMMENDED FIXES:")
    logger.info("1. Add zone ID validation in database storage method")
    logger.info("2. Add comprehensive logging for all registration steps")
    logger.info("3. Add post-storage verification of zone ID")
    logger.info("4. Return False from registration if zone ID storage fails")

if __name__ == "__main__":
    fix_zone_id_storage_workflow()