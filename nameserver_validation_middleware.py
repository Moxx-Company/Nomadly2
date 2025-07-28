#!/usr/bin/env python3
"""
Nameserver Validation Middleware
===============================

Validates nameserver data during domain registration to prevent corruption.
"""

import logging
import json
import asyncio

logger = logging.getLogger(__name__)

class NameserverValidationMiddleware:
    """Validates nameserver data during registration"""
    
    @staticmethod
    async def validate_nameservers_before_storage(domain_name: str, nameservers: List[str], cloudflare_zone_id: str = None):
        """Validate nameservers before storing in database"""
        
        logger.info(f"🔍 Validating nameservers for {domain_name}: {nameservers}")
        
        # Check if using generic Cloudflare nameservers
        generic_ns = [await get_real_cloudflare_nameservers(domain_name)]
        if set(nameservers) == set(generic_ns):
            logger.warning(f"⚠️ Generic nameservers detected for {domain_name}")
            
            # Try to get real nameservers if cloudflare_zone_id available
            if cloudflare_zone_id:
                real_ns = await NameserverValidationMiddleware._get_real_nameservers(cloudflare_zone_id)
                if real_ns and set(real_ns) != set(generic_ns):
                    logger.info(f"✅ Found real nameservers for {domain_name}: {real_ns}")
                    return real_ns
                    
            logger.warning(f"⚠️ Could not get real nameservers, using generic ones")
            
        return nameservers
        
    @staticmethod
    async def _get_real_nameservers(cloudflare_zone_id: str):
        """Get real nameservers from Cloudflare"""
        
        try:
            from apis.production_cloudflare import CloudflareAPI
            cf_api = CloudflareAPI()
            
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
            logger.error(f"Error getting real nameservers: {e}")
            return None
            
    @staticmethod
    async def post_registration_validation(domain_name: str):
        """Validate nameservers after registration is complete"""
        
        from database import get_db_manager
        from sqlalchemy import text
        
        db_manager = get_db_manager()
        session = db_manager.get_session()
        
        try:
            # Get stored nameservers
            result = session.execute(text("""
                SELECT nameservers, cloudflare_zone_id 
                FROM registered_domains 
                WHERE domain_name = :domain_name
            """), {"domain_name": domain_name}).fetchone()
            
            if result:
                stored_ns = json.loads(result.nameservers) if result.nameservers else []
                cloudflare_zone_id = result.cloudflare_zone_id
                
                # Validate stored nameservers
                validated_ns = await NameserverValidationMiddleware.validate_nameservers_before_storage(
                    domain_name, stored_ns, cloudflare_zone_id
                )
                
                # Update if different
                if set(validated_ns) != set(stored_ns):
                    session.execute(text("""
                        UPDATE registered_domains 
                        SET nameservers = :nameservers 
                        WHERE domain_name = :domain_name
                    """), {
                        "nameservers": json.dumps(validated_ns),
                        "domain_name": domain_name
                    })
                    session.commit()
                    logger.info(f"✅ Updated nameservers for {domain_name}: {validated_ns}")
                    
        except Exception as e:
            session.rollback()
            logger.error(f"Post-registration validation error: {e}")
        finally:
            session.close()
