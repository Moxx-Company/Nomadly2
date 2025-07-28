#!/usr/bin/env python3
"""
Async API Clients for Nomadly2
Full async implementation using aiohttp for all external API calls
"""

import asyncio
import aiohttp
import logging

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_performance(func_name: str = None):
    """Simple performance monitoring decorator"""
    def decorator(func):
        return func  # No-op for now
    return decorator
import json
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

logger = logger

class AsyncOpenProviderAPI:
    """Async OpenProvider API client with proper timeout and retry handling"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.auth_token = None
        self.base_url = "https://api.openprovider.eu"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30, connect=8)
        self.session = aiohttp.ClientSession(timeout=timeout)
        await self.authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self) -> bool:
        """Async authentication with OpenProvider"""
        try:
            logger.info("openprovider_auth_started")
            
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(
                f"{self.base_url}/v1beta/auth/login",
                json=auth_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get('data', {}).get('token')
                    
                    logger.info(
                        "openprovider_auth_success",
                        token_length=len(self.auth_token) if self.auth_token else 0
                    )
                    return True
                else:
                    error_text = await response.text()
                    logger.error(
                        "openprovider_auth_failed",
                        status=response.status,
                        error=error_text
                    )
                    return False
                    
        except Exception as e:
            logger.error(
                "openprovider_auth_error",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """Create OpenProvider contact asynchronously"""
        try:
            logger.info("openprovider_create_contact_started")
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{self.base_url}/v1beta/customers",
                json=contact_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    contact_handle = result.get('data', {}).get('handle')
                    
                    logger.info(
                        "openprovider_contact_created",
                        contact_handle=contact_handle
                    )
                    return contact_handle
                else:
                    error_text = await response.text()
                    logger.error(
                        "openprovider_contact_failed",
                        status=response.status,
                        error=error_text
                    )
                    return None
                    
        except Exception as e:
            logger.error(
                "openprovider_contact_error",
                error=str(e)
            )
            return None
    
    async def register_domain(
        self, 
        domain_name: str, 
        contact_handle: str, 
        nameservers: List[str]
    ) -> Optional[str]:
        """Register domain asynchronously"""
        try:
            logger.info(
                "openprovider_register_domain_started",
                domain=domain_name,
                contact_handle=contact_handle
            )
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            domain_data = {
                "domain": {
                    "name": domain_name.split('.')[0],
                    "extension": domain_name.split('.', 1)[1]
                },
                "period": 1,
                "owner_handle": contact_handle,
                "admin_handle": contact_handle,
                "tech_handle": contact_handle,
                "billing_handle": contact_handle,
                "name_servers": [{"name": ns} for ns in nameservers]
            }
            
            async with self.session.post(
                f"{self.base_url}/v1beta/domains",
                json=domain_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    domain_id = result.get('data', {}).get('id')
                    
                    logger.info(
                        "openprovider_domain_registered",
                        domain=domain_name,
                        domain_id=domain_id
                    )
                    return str(domain_id)
                else:
                    error_text = await response.text()
                    logger.error(
                        "openprovider_domain_registration_failed",
                        domain=domain_name,
                        status=response.status,
                        error=error_text
                    )
                    return None
                    
        except Exception as e:
            logger.error(
                "openprovider_domain_error",
                domain=domain_name,
                error=str(e)
            )
            return None

class AsyncCloudflareAPI:
    """Async Cloudflare API client with comprehensive DNS management"""
    
    def __init__(self, email: str, api_key: str, api_token: str):
        self.email = email
        self.api_key = api_key
        self.api_token = api_token
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30, connect=8)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def create_zone(self, domain_name: str) -> Tuple[bool, Optional[str], List[str]]:
        """Create Cloudflare zone asynchronously"""
        try:
            logger.info(
                "cloudflare_create_zone_started",
                domain=domain_name
            )
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            zone_data = {
                "name": domain_name,
                "type": "full"
            }
            
            async with self.session.post(
                f"{self.base_url}/zones",
                json=zone_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    zone_data = result.get('result', {})
                    cloudflare_zone_id = zone_data.get('id')
                    nameservers = zone_data.get('name_servers', [])
                    
                    logger.info(
                        "cloudflare_zone_created",
                        domain=domain_name,
                        cloudflare_zone_id=cloudflare_zone_id,
                        nameservers=nameservers
                    )
                    return True, cloudflare_zone_id, nameservers
                else:
                    error_text = await response.text()
                    logger.error(
                        "cloudflare_zone_creation_failed",
                        domain=domain_name,
                        status=response.status,
                        error=error_text
                    )
                    return False, None, []
                    
        except Exception as e:
            logger.error(
                "cloudflare_zone_error",
                domain=domain_name,
                error=str(e)
            )
            return False, None, []
    
    async def create_dns_record(
        self, 
        cloudflare_zone_id: str, 
        record_data: Dict[str, Any]
    ) -> Optional[str]:
        """Create DNS record asynchronously with proper MX priority support"""
        try:
            logger.info(
                "cloudflare_create_dns_record_started",
                cloudflare_zone_id=cloudflare_zone_id,
                record_type=record_data.get('type'),
                name=record_data.get('name')
            )
            
            # Ensure MX records have priority parameter
            if record_data.get('type', '').upper() == 'MX' and 'priority' not in record_data:
                record_data['priority'] = 10  # Default MX priority
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records",
                json=record_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    record_id = result.get('result', {}).get('id')
                    
                    logger.info(
                        "cloudflare_dns_record_created",
                        cloudflare_zone_id=cloudflare_zone_id,
                        record_id=record_id,
                        type=record_data.get('type'),
                        name=record_data.get('name')
                    )
                    return record_id
                else:
                    error_text = await response.text()
                    logger.error(
                        "cloudflare_dns_record_failed",
                        cloudflare_zone_id=cloudflare_zone_id,
                        status=response.status,
                        error=error_text
                    )
                    return None
                    
        except Exception as e:
            logger.error(
                "cloudflare_dns_record_error",
                cloudflare_zone_id=cloudflare_zone_id,
                error=str(e)
            )
            return None
    
    async def list_dns_records(self, cloudflare_zone_id: str) -> List[Dict[str, Any]]:
        """List all DNS records for a zone asynchronously"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    records = result.get('result', [])
                    
                    logger.info(
                        "cloudflare_dns_records_listed",
                        cloudflare_zone_id=cloudflare_zone_id,
                        count=len(records)
                    )
                    return records
                else:
                    logger.error(
                        "cloudflare_list_dns_records_failed",
                        cloudflare_zone_id=cloudflare_zone_id,
                        status=response.status
                    )
                    return []
                    
        except Exception as e:
            logger.error(
                "cloudflare_list_dns_records_error",
                cloudflare_zone_id=cloudflare_zone_id,
                error=str(e)
            )
            return []

class AsyncBlockBeeAPI:
    """Async BlockBee API client for cryptocurrency payments"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.blockbee.io"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=15, connect=5)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def create_payment_address(
        self, 
        cryptocurrency: str, 
        callback_url: str, 
        order_id: str
    ) -> Optional[Dict[str, Any]]:
        """Create payment address asynchronously"""
        try:
            logger.info(
                "blockbee_create_address_started",
                cryptocurrency=cryptocurrency,
                order_id=order_id
            )
            
            params = {
                "callback": callback_url,
                "apikey": self.api_key,
                "order_id": order_id
            }
            
            async with self.session.get(
                f"{self.base_url}/{cryptocurrency}/create/",
                params=params
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get('status') == 'success':
                        logger.info(
                            "blockbee_address_created",
                            cryptocurrency=cryptocurrency,
                            order_id=order_id,
                            address=result.get('address_in')
                        )
                        return result
                    else:
                        logger.error(
                            "blockbee_address_creation_failed",
                            cryptocurrency=cryptocurrency,
                            error=result.get('error')
                        )
                        return None
                else:
                    error_text = await response.text()
                    logger.error(
                        "blockbee_address_api_error",
                        cryptocurrency=cryptocurrency,
                        status=response.status,
                        error=error_text
                    )
                    return None
                    
        except Exception as e:
            logger.error(
                "blockbee_address_error",
                cryptocurrency=cryptocurrency,
                error=str(e)
            )
            return None
    
    async def get_exchange_rates(self) -> Dict[str, float]:
        """Get current cryptocurrency exchange rates"""
        try:
            async with self.session.get(
                f"{self.base_url}/info/prices/"
            ) as response:
                
                if response.status == 200:
                    rates = await response.json()
                    logger.info(
                        "blockbee_rates_fetched",
                        currencies=list(rates.keys()) if rates else []
                    )
                    return rates
                else:
                    logger.error(
                        "blockbee_rates_failed",
                        status=response.status
                    )
                    return {}
                    
        except Exception as e:
            logger.error(
                "blockbee_rates_error",
                error=str(e)
            )
            return {}

# Utility functions for async API usage
async def create_domain_with_dns(
    domain_name: str,
    contact_data: Dict[str, Any],
    nameserver_choice: str,
    openprovider_credentials: Dict[str, str],
    cloudflare_credentials: Dict[str, str]
) -> Dict[str, Any]:
    """
    Complete domain registration with DNS setup using async APIs
    """
    result = {
        "success": False,
        "domain_id": None,
        "zone_id": None,
        "nameservers": [],
        "errors": []
    }
    
    try:
        # Step 1: Create Cloudflare zone (if needed)
        cloudflare_zone_id = None
        nameservers = []
        
        if nameserver_choice == "cloudflare":
            async with AsyncCloudflareAPI(**cloudflare_credentials) as cf_api:
                success, cloudflare_zone_id, nameservers = await cf_api.create_zone(domain_name)
                
                if success and cloudflare_zone_id:
                    # Add A record pointing to server
                    server_ip = "89.117.27.176"  # From environment
                    
                    a_record_data = {
                        "type": "A",
                        "name": domain_name,
                        "content": server_ip,
                        "ttl": 300
                    }
                    
                    await cf_api.create_dns_record(cloudflare_zone_id, a_record_data)
                    
                    result["zone_id"] = cloudflare_zone_id
                    result["nameservers"] = nameservers
                else:
                    result["errors"].append("Cloudflare zone creation failed")
                    return result
        else:
            # Use default nameservers
            nameservers = ["ns1.openprovider.com", "ns2.openprovider.com"]
            result["nameservers"] = nameservers
        
        # Step 2: Register domain with OpenProvider
        async with AsyncOpenProviderAPI(**openprovider_credentials) as op_api:
            # Create contact
            contact_handle = await op_api.create_contact(contact_data)
            
            if not contact_handle:
                result["errors"].append("Contact creation failed")
                return result
            
            # Register domain
            domain_id = await op_api.register_domain(
                domain_name, 
                contact_handle, 
                nameservers
            )
            
            if domain_id:
                result["success"] = True
                result["domain_id"] = domain_id
            else:
                result["errors"].append("Domain registration failed")
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Async domain creation error: {str(e)}")
        logger.error(
            "async_domain_creation_error",
            domain=domain_name,
            error=str(e)
        )
        return result

# Example usage
async def main():
    """Example usage of async API clients"""
    logger.info("async_api_clients_test_started")
    
    # Test async API clients here if needed
    
    logger.info("async_api_clients_test_completed")

if __name__ == "__main__":
    asyncio.run(main())