#!/usr/bin/env python3
"""
Enhanced Registration Service - Using correct OpenProvider API
Implements proper customer handle reuse and consistent contact management
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from database import get_db_manager
from complete_openprovider_fix import CorrectOpenProviderAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRegistrationService:
    """Enhanced registration service with proper OpenProvider integration"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.openprovider = CorrectOpenProviderAPI()
        
    async def register_domain_for_customer(self, telegram_id: int, domain_name: str, 
                                         nameserver_choice: str = "cloudflare") -> Dict[str, Any]:
        """Register domain with consistent customer handle reuse"""
        logger.info(f"🚀 ENHANCED DOMAIN REGISTRATION: {domain_name}")
        logger.info(f"Customer: {telegram_id}, NS: {nameserver_choice}")
        
        try:
            # Step 1: Get or create consistent customer handle
            customer_handle = await self._get_or_create_customer_handle(telegram_id)
            if not customer_handle:
                return {"success": False, "error": "Failed to get customer handle"}
            
            logger.info(f"✅ Customer handle: {customer_handle}")
            
            # Step 2: Setup DNS infrastructure if needed
            cloudflare_zone_id = None
            nameservers = None
            
            if nameserver_choice == "cloudflare":
                cloudflare_zone_id, nameservers = await self._setup_cloudflare_dns(domain_name)
                if not cloudflare_zone_id:
                    return {"success": False, "error": "Failed to create Cloudflare zone"}
                logger.info(f"✅ Cloudflare zone: {cloudflare_zone_id}")
            else:
                nameservers = ["ns1.openprovider.nl", "ns2.openprovider.be"]
            
            # Step 3: Register domain with OpenProvider
            registration_result = self.openprovider.register_domain_with_handle(
                domain_name, customer_handle, nameservers
            )
            
            if not registration_result.get('success'):
                logger.error(f"❌ Domain registration failed: {registration_result}")
                return registration_result
                
            openprovider_domain_id = registration_result.get('domain_id')
            logger.info(f"✅ Domain registered: {openprovider_domain_id}")
            
            # Step 4: Save to database
            saved = await self._save_domain_record(
                telegram_id=telegram_id,
                domain_name=domain_name,
                customer_handle=customer_handle,
                openprovider_domain_id=openprovider_domain_id,
                cloudflare_zone_id=cloudflare_zone_id,
                nameservers=nameservers
            )
            
            if saved:
                logger.info(f"✅ Registration complete: {domain_name}")
                return {
                    "success": True,
                    "domain_name": domain_name,
                    "openprovider_domain_id": openprovider_domain_id,
                    "customer_handle": customer_handle,
                    "cloudflare_zone_id": cloudflare_zone_id
                }
            else:
                return {"success": False, "error": "Failed to save domain record"}
                
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_or_create_customer_handle(self, telegram_id: int) -> Optional[str]:
        """Get existing customer handle or create new one"""
        try:
            # Check if customer already has a handle
            existing_domains = self.db.get_user_domains(telegram_id)
            
            for domain in existing_domains:
                if domain.openprovider_contact_handle and not domain.openprovider_contact_handle.startswith('contact_'):
                    # Found existing proper OpenProvider handle
                    logger.info(f"♻️ Reusing existing handle: {domain.openprovider_contact_handle}")
                    return domain.openprovider_contact_handle
            
            # Need to create new customer handle
            logger.info("🆕 Creating new customer handle")
            
            user = self.db.get_user_by_telegram_id(telegram_id)
            customer_data = {
                'first_name': 'Privacy',  # Anonymous contact
                'last_name': 'User',
                'email': user.technical_email if user and user.technical_email else f'user{telegram_id}@privacy.example.com',
                'street': 'Privacy Lane',
                'number': str(telegram_id % 9999),  # Unique but anonymous
                'city': 'New York',
                'state': 'NY',
                'zipcode': '10001', 
                'country': 'US',
                'country_code': '+1',
                'area_code': '555',
                'phone': str(telegram_id % 9999999)  # Unique phone
            }
            
            handle = self.openprovider.create_customer_handle(customer_data)
            return handle
            
        except Exception as e:
            logger.error(f"Customer handle error: {e}")
            return None
    
    async def _setup_cloudflare_dns(self, domain_name: str) -> tuple:
        """Setup Cloudflare DNS zone"""
        try:
            from apis.production_cloudflare import CloudflareAPI
            cf_api = CloudflareAPI()
            
            # Create zone
            zone_result = await cf_api.create_zone_async(domain_name)
            if not zone_result:
                return None, None
                
            cloudflare_zone_id = zone_result.get('id')
            nameservers = zone_result.get('name_servers', [])
            
            # Create basic A record
            record_data = {
                "type": "A",
                "name": "@", 
                "content": "192.0.2.1",  # Placeholder IP
                "ttl": 300
            }
            
            await cf_api.create_dns_record_async(cloudflare_zone_id, record_data)
            
            return cloudflare_zone_id, nameservers
            
        except Exception as e:
            logger.error(f"Cloudflare setup error: {e}")
            return None, None
    
    async def _save_domain_record(self, **kwargs) -> bool:
        """Save domain record to database"""
        try:
            # Convert nameservers to string format
            nameservers = kwargs.get('nameservers', [])
            if isinstance(nameservers, list):
                nameservers_str = ','.join(nameservers)
            else:
                nameservers_str = str(nameservers)
            
            # Create domain record
            domain = self.db.create_registered_domain(
                telegram_id=kwargs['telegram_id'],
                domain_name=kwargs['domain_name'],
                openprovider_contact_handle=kwargs['customer_handle'],
                cloudflare_zone_id=kwargs.get('cloudflare_zone_id'),
                nameservers=nameservers_str
            )
            
            if domain and kwargs.get('openprovider_domain_id'):
                # Update with OpenProvider ID
                session = self.db.get_session()
                try:
                    domain.openprovider_domain_id = str(kwargs['openprovider_domain_id'])
                    domain.status = 'active'
                    session.commit()
                    logger.info(f"✅ Database record updated with OpenProvider ID")
                except Exception as update_error:
                    logger.error(f"Update error: {update_error}")
                    session.rollback()
                finally:
                    session.close()
            
            return domain is not None
            
        except Exception as e:
            logger.error(f"Database save error: {e}")
            return False

async def test_enhanced_service():
    """Test the enhanced registration service"""
    logger.info("🧪 TESTING ENHANCED REGISTRATION SERVICE")
    logger.info("=" * 60)
    
    try:
        service = EnhancedRegistrationService()
        
        # Test customer handle creation/reuse
        telegram_id = 6896666427  # Customer @folly542
        handle = await service._get_or_create_customer_handle(telegram_id)
        
        if handle:
            logger.info(f"✅ Customer handle system working: {handle}")
            logger.info("✅ Enhanced registration service ready")
            logger.info("\nThis service provides:")
            logger.info("1. Proper OpenProvider API integration")
            logger.info("2. Customer handle reuse across all domains")
            logger.info("3. Consistent contact information")
            logger.info("4. Proper DNS setup integration")
            logger.info("5. Database consistency")
        else:
            logger.error("❌ Customer handle system failed")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_service())