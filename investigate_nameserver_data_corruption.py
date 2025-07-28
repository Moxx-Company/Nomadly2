#!/usr/bin/env python3
"""
Investigate Nameserver Data Corruption
=====================================

Analyze why letusdoit.sbs had wrong nameserver data and prevent future issues.
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

def investigate_nameserver_data_corruption():
    """Investigate why nameserver data became corrupted"""
    
    logger.info("🔍 INVESTIGATING NAMESERVER DATA CORRUPTION")
    logger.info("=" * 60)
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        from sqlalchemy import text
        
        # Check current nameserver data for both domains
        domains_data = session.execute(text("""
            SELECT 
                domain_name,
                nameservers,
                cloudflare_zone_id,
                created_at,
                nameserver_mode
            FROM registered_domains 
            ORDER BY created_at DESC
        """)).fetchall()
        
        logger.info("📊 CURRENT DOMAIN NAMESERVER DATA:")
        logger.info("-" * 40)
        
        for domain in domains_data:
            logger.info(f"Domain: {domain.domain_name}")
            logger.info(f"  Stored NS: {domain.nameservers}")
            logger.info(f"  Zone ID: {domain.cloudflare_zone_id}")
            logger.info(f"  Mode: {domain.nameserver_mode}")
            logger.info(f"  Created: {domain.created_at}")
            logger.info("")
            
        # Check what the real Cloudflare nameservers should be
        logger.info("🌐 CHECKING REAL CLOUDFLARE NAMESERVERS:")
        logger.info("-" * 40)
        
        from apis.production_cloudflare import CloudflareAPI
        cf_api = CloudflareAPI()
        
        for domain in domains_data:
            if domain.cloudflare_zone_id:
                try:
                    # Get zone details from Cloudflare API
                    import requests
                    headers = {
                        'Authorization': f'Bearer {cf_api.api_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    url = f"https://api.cloudflare.com/client/v4/zones/{domain.cloudflare_zone_id}"
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        zone_data = response.json()
                        if zone_data.get('success'):
                            real_ns = zone_data['result'].get('name_servers', [])
                            logger.info(f"{domain.domain_name} real NS: {real_ns}")
                        else:
                            logger.error(f"Cloudflare API error for {domain.domain_name}: {zone_data}")
                    else:
                        logger.error(f"HTTP {response.status_code} for {domain.domain_name}")
                        
                except Exception as e:
                    logger.error(f"Error getting real NS for {domain.domain_name}: {e}")
        
        # Analyze the registration process
        logger.info("")
        logger.info("🔧 ANALYZING REGISTRATION PROCESS:")
        logger.info("-" * 40)
        
        # Check how nameservers are stored during registration
        logger.info("Looking at registration service implementation...")
        
        # Check fixed_registration_service.py
        try:
            with open('fixed_registration_service.py', 'r') as f:
                content = f.read()
                
            if 'ns1.cloudflare.com' in content:
                logger.warning("⚠️ Found hardcoded 'ns1.cloudflare.com' in registration service")
            if 'ns2.cloudflare.com' in content:
                logger.warning("⚠️ Found hardcoded 'ns2.cloudflare.com' in registration service")
            if 'get_nameservers' in content:
                logger.info("✅ Found get_nameservers call in registration service")
            else:
                logger.error("❌ No get_nameservers call found in registration service")
                
        except FileNotFoundError:
            logger.warning("registration service file not found")
            
        # Check payment_service.py for registration logic
        try:
            with open('payment_service.py', 'r') as f:
                content = f.read()
                
            if 'ns1.cloudflare.com' in content:
                logger.warning("⚠️ Found hardcoded 'ns1.cloudflare.com' in payment service")
            if 'ns2.cloudflare.com' in content:
                logger.warning("⚠️ Found hardcoded 'ns2.cloudflare.com' in payment service")
                
        except FileNotFoundError:
            logger.warning("payment service file not found")
            
        # Check nameserver_manager.py
        try:
            with open('nameserver_manager.py', 'r') as f:
                content = f.read()
                
            if 'CLOUDFLARE_NS' in content:
                logger.info("Found CLOUDFLARE_NS constant")
                # Extract the constant value
                for line in content.split('\n'):
                    if 'CLOUDFLARE_NS' in line and '=' in line:
                        logger.info(f"Nameserver constant: {line.strip()}")
                        
        except FileNotFoundError:
            logger.warning("nameserver_manager.py not found")
            
    except Exception as e:
        logger.error(f"Investigation error: {e}")
        
    finally:
        session.close()
        
    # Root cause analysis
    logger.info("")
    logger.info("🎯 ROOT CAUSE ANALYSIS:")
    logger.info("-" * 30)
    
    logger.info("HYPOTHESIS 1: Hardcoded nameserver values during registration")
    logger.info("- Registration service may use hardcoded ns1/ns2.cloudflare.com")
    logger.info("- Instead of fetching real nameservers from Cloudflare API")
    
    logger.info("")
    logger.info("HYPOTHESIS 2: API timing issue during registration")
    logger.info("- Zone created but nameservers not immediately available")
    logger.info("- Registration proceeds with default values")
    
    logger.info("")
    logger.info("HYPOTHESIS 3: Missing nameserver update after zone creation")
    logger.info("- Zone created successfully")
    logger.info("- Real nameservers never fetched and stored")

def create_nameserver_validation_system():
    """Create system to validate and maintain correct nameserver data"""
    
    logger.info("")
    logger.info("🛡️ CREATING NAMESERVER VALIDATION SYSTEM:")
    logger.info("-" * 50)
    
    validation_code = '''
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
'''
    
    # Write the validation system
    try:
        with open('nameserver_validator.py', 'w') as f:
            f.write(validation_code)
        logger.info("✅ Created nameserver_validator.py")
    except Exception as e:
        logger.error(f"Error creating validator: {e}")

if __name__ == "__main__":
    investigate_nameserver_data_corruption()
    create_nameserver_validation_system()
    
    logger.info("")
    logger.info("🎯 NEXT STEPS TO PREVENT FUTURE ISSUES:")
    logger.info("=" * 50)
    logger.info("1. Fix registration service to use real Cloudflare nameservers")
    logger.info("2. Add nameserver validation after zone creation")
    logger.info("3. Implement periodic nameserver data validation")
    logger.info("4. Add alerts for nameserver data mismatches")
    logger.info("5. Test registration process thoroughly")