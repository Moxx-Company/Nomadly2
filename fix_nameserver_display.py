#!/usr/bin/env python3
"""
Fix Nameserver Display for letusdoit.sbs
=======================================

Update database with correct Cloudflare nameservers.
"""

import sys
import logging
import json

# Add project root to path
sys.path.append('.')

from database import get_db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_nameserver_display():
    """Fix nameserver display by updating database with correct nameservers"""
    
    logger.info("🔧 FIXING NAMESERVER DISPLAY FOR LETUSDOIT.SBS")
    logger.info("=" * 50)
    
    try:
        # Get real Cloudflare nameservers
        from apis.production_cloudflare import CloudflareAPI
        cf_api = CloudflareAPI()
        
        real_nameservers = cf_api.get_nameservers('letusdoit.sbs')
        logger.info(f"Real Cloudflare nameservers: {real_nameservers}")
        
        if not real_nameservers:
            logger.error("❌ Could not retrieve real nameservers")
            return
            
        # Update database with correct nameservers
        db_manager = get_db_manager()
        session = db_manager.get_session()
        
        try:
            from sqlalchemy import text
            
            # Update the nameservers in database
            nameservers_json = json.dumps(real_nameservers)
            
            result = session.execute(text("""
                UPDATE registered_domains 
                SET nameservers = :nameservers 
                WHERE domain_name = 'letusdoit.sbs'
            """), {"nameservers": nameservers_json})
            
            session.commit()
            
            if result.rowcount > 0:
                logger.info(f"✅ Updated database with correct nameservers: {real_nameservers}")
                
                # Verify update
                verification = session.execute(text("""
                    SELECT nameservers FROM registered_domains 
                    WHERE domain_name = 'letusdoit.sbs'
                """)).fetchone()
                
                logger.info(f"Verification - Stored nameservers: {verification.nameservers}")
            else:
                logger.error("❌ No rows updated - domain may not exist")
                
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error fixing nameserver display: {e}")

if __name__ == "__main__":
    fix_nameserver_display()