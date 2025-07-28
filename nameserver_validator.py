
#!/usr/bin/env python3
"""
Nameserver Validation and Correction System
==========================================

Automatically validates and corrects nameserver data.
"""

import logging
import json
import asyncio
from database import get_db_manager

logger = logging.getLogger(__name__)

class NameserverValidator:
    """Validates and corrects nameserver data"""
    
    def __init__(self):
        self.corrections_made = 0
        
    async def validate_and_correct_all_domains(self):
        """Validate nameservers for all domains and correct if needed"""
        
        db_manager = get_db_manager()
        session = db_manager.get_session()
        
        try:
            from sqlalchemy import text
            from apis.production_cloudflare import CloudflareAPI
            
            # Get all domains with Cloudflare zones
            domains = session.execute(text("""
                SELECT domain_name, nameservers, cloudflare_zone_id 
                FROM registered_domains 
                WHERE cloudflare_zone_id IS NOT NULL
            """)).fetchall()
            
            cf_api = CloudflareAPI()
            
            for domain in domains:
                await self._validate_domain_nameservers(
                    session, cf_api, domain.domain_name, 
                    domain.nameservers, domain.cloudflare_zone_id
                )
                
            session.commit()
            logger.info(f"✅ Validation complete. Made {self.corrections_made} corrections.")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Validation error: {e}")
        finally:
            session.close()
            
    async def _validate_domain_nameservers(self, session, cf_api, domain_name, 
                                         stored_ns, cloudflare_zone_id):
        """Validate nameservers for a single domain"""
        
        try:
            # Get real nameservers from Cloudflare
            real_ns = await self._get_real_nameservers(cf_api, cloudflare_zone_id)
            
            if not real_ns:
                logger.warning(f"Could not get real nameservers for {domain_name}")
                return
                
            # Parse stored nameservers
            if isinstance(stored_ns, str):
                stored_list = json.loads(stored_ns)
            else:
                stored_list = stored_ns or []
                
            # Compare and correct if needed
            if set(stored_list) != set(real_ns):
                logger.info(f"🔧 Correcting nameservers for {domain_name}")
                logger.info(f"  Old: {stored_list}")
                logger.info(f"  New: {real_ns}")
                
                # Update database
                from sqlalchemy import text
                session.execute(text("""
                    UPDATE registered_domains 
                    SET nameservers = :nameservers 
                    WHERE domain_name = :domain_name
                """), {
                    "nameservers": json.dumps(real_ns),
                    "domain_name": domain_name
                })
                
                self.corrections_made += 1
            else:
                logger.info(f"✅ {domain_name} nameservers are correct")
                
        except Exception as e:
            logger.error(f"Error validating {domain_name}: {e}")
            
    async def _get_real_nameservers(self, cf_api, cloudflare_zone_id):
        """Get real nameservers from Cloudflare API"""
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {cf_api.api_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                zone_data = response.json()
                if zone_data.get('success'):
                    return zone_data['result'].get('name_servers', [])
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting nameservers for zone {cloudflare_zone_id}: {e}")
            return None

async def main():
    validator = NameserverValidator()
    await validator.validate_and_correct_all_domains()

if __name__ == "__main__":
    asyncio.run(main())
