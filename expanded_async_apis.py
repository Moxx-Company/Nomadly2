#!/usr/bin/env python3
"""
Expanded Async API Methods
Complete async implementations for all API operations
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
import json
import time
from functools import wraps

logger = logging.getLogger(__name__)

def async_retry(max_attempts: int = 3, delay: float = 1.0, exponential_backoff: bool = True):
    """Decorator for async operations with retry logic"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"❌ {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    wait_time = delay * (2 ** attempt if exponential_backoff else 1)
                    logger.warning(f"⚠️ {func.__name__} attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
            
            raise last_exception
        return wrapper
    return decorator

class ExpandedAsyncOpenProviderAPI:
    """Complete async OpenProvider API implementation"""
    
    def __init__(self):
        self.base_url = "https://api.openprovider.eu"
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
        )
        await self.authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @async_retry(max_attempts=3, delay=1.0)
    async def authenticate(self) -> bool:
        """Async authentication with OpenProvider"""
        try:
            auth_data = {
                "username": "nomadly2",
                "password": "nm2@abyss",
                "ip": "0.0.0.0"
            }
            
            async with self.session.post(
                f"{self.base_url}/v1beta/auth/login",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("data", {}).get("token")
                    logger.info("✅ OpenProvider async authentication successful")
                    return True
                else:
                    logger.error(f"❌ OpenProvider auth failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ OpenProvider auth error: {e}")
            raise
    
    @async_retry(max_attempts=3, delay=2.0)
    async def search_domain_async(self, domain_name: str) -> Dict[str, Any]:
        """Async domain availability search"""
        try:
            search_data = {
                "domains": [{"name": domain_name}],
                "with_price": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{self.base_url}/v1beta/domains/check",
                json=search_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    domains = data.get("data", {}).get("results", [])
                    
                    if domains:
                        domain_info = domains[0]
                        return {
                            "success": True,
                            "available": domain_info.get("status") == "free",
                            "domain": domain_name,
                            "price": domain_info.get("price", {}).get("product", {}).get("price"),
                            "currency": domain_info.get("price", {}).get("product", {}).get("currency", "USD")
                        }
                    
                return {"success": False, "error": "No domain data received"}
                
        except Exception as e:
            logger.error(f"❌ Async domain search error: {e}")
            return {"success": False, "error": str(e)}
    
    @async_retry(max_attempts=3, delay=3.0)
    async def register_domain_async(self, domain_name: str, contact_handle: str, nameservers: List[str]) -> Dict[str, Any]:
        """Async domain registration"""
        try:
            registration_data = {
                "domain": {
                    "name": domain_name,
                    "period": 1
                },
                "owner_handle": contact_handle,
                "admin_handle": contact_handle,
                "tech_handle": contact_handle,
                "billing_handle": contact_handle,
                "name_servers": [{"name": ns} for ns in nameservers],
                "dnssec_keys": [],
                "use_domicile": False,
                "promo_code": ""
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{self.base_url}/v1beta/domains",
                json=registration_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    domain_data = data.get("data", {})
                    
                    return {
                        "success": True,
                        "domain_id": domain_data.get("id"),
                        "status": domain_data.get("status"),
                        "domain_name": domain_name
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Domain registration failed: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            logger.error(f"❌ Async domain registration error: {e}")
            return {"success": False, "error": str(e)}

class ExpandedAsyncCloudflareAPI:
    """Complete async Cloudflare API implementation"""
    
    def __init__(self):
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.session = None
        self.api_token = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        import os
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @async_retry(max_attempts=3, delay=2.0)
    async def create_zone_async(self, domain_name: str) -> Dict[str, Any]:
        """Async Cloudflare zone creation"""
        try:
            zone_data = {
                "name": domain_name,
                "account": {"id": "your_account_id"},
                "jump_start": True
            }
            
            async with self.session.post(
                f"{self.base_url}/zones",
                json=zone_data
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    zone_info = data.get("result", {})
                    
                    return {
                        "success": True,
                        "zone_id": zone_info.get("id"),
                        "nameservers": zone_info.get("name_servers", []),
                        "status": zone_info.get("status")
                    }
                else:
                    error_data = await response.json()
                    return {"success": False, "error": error_data.get("errors", [])}
                    
        except Exception as e:
            logger.error(f"❌ Async zone creation error: {e}")
            return {"success": False, "error": str(e)}
    
    @async_retry(max_attempts=3, delay=1.0)
    async def create_dns_record_async(self, cloudflare_zone_id: str, record_type: str, name: str, content: str, ttl: int = 300) -> Dict[str, Any]:
        """Async DNS record creation"""
        try:
            record_data = {
                "type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl
            }
            
            async with self.session.post(
                f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records",
                json=record_data
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    record_info = data.get("result", {})
                    
                    return {
                        "success": True,
                        "record_id": record_info.get("id"),
                        "name": record_info.get("name"),
                        "content": record_info.get("content")
                    }
                else:
                    error_data = await response.json()
                    return {"success": False, "error": error_data.get("errors", [])}
                    
        except Exception as e:
            logger.error(f"❌ Async DNS record creation error: {e}")
            return {"success": False, "error": str(e)}
    
    @async_retry(max_attempts=3, delay=1.0)
    async def list_dns_records_async(self, cloudflare_zone_id: str) -> Dict[str, Any]:
        """Async DNS records listing"""
        try:
            async with self.session.get(
                f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records"
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "records": data.get("result", [])
                    }
                else:
                    error_data = await response.json()
                    return {"success": False, "error": error_data.get("errors", [])}
                    
        except Exception as e:
            logger.error(f"❌ Async DNS records listing error: {e}")
            return {"success": False, "error": str(e)}

class ExpandedAsyncBlockBeeAPI:
    """Complete async BlockBee API implementation"""
    
    def __init__(self):
        self.base_url = "https://api.blockbee.io"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @async_retry(max_attempts=3, delay=1.0)
    async def create_payment_address_async(self, crypto_currency: str, callback_url: str, amount: float) -> Dict[str, Any]:
        """Async payment address creation"""
        try:
            params = {
                "callback": callback_url,
                "apikey": "your_api_key"
            }
            
            async with self.session.get(
                f"{self.base_url}/{crypto_currency}/create/",
                params=params
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        return {
                            "success": True,
                            "payment_address": data.get("address_in"),
                            "qr_code": data.get("qr_code_url"),
                            "amount": amount
                        }
                    else:
                        return {"success": False, "error": data.get("error", "Unknown error")}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Async payment address creation error: {e}")
            return {"success": False, "error": str(e)}
    
    @async_retry(max_attempts=3, delay=1.0)
    async def get_payment_info_async(self, crypto_currency: str, payment_address: str) -> Dict[str, Any]:
        """Async payment information retrieval"""
        try:
            params = {
                "apikey": "your_api_key"
            }
            
            async with self.session.get(
                f"{self.base_url}/{crypto_currency}/info/{payment_address}/",
                params=params
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "payment_info": data
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Async payment info error: {e}")
            return {"success": False, "error": str(e)}

# Async API manager for all services
class ExpandedAsyncAPIManager:
    """Unified async API manager"""
    
    def __init__(self):
        self.openprovider = None
        self.cloudflare = None
        self.blockbee = None
    
    async def __aenter__(self):
        """Initialize all async API clients"""
        self.openprovider = ExpandedAsyncOpenProviderAPI()
        self.cloudflare = ExpandedAsyncCloudflareAPI()
        self.blockbee = ExpandedAsyncBlockBeeAPI()
        
        await self.openprovider.__aenter__()
        await self.cloudflare.__aenter__()
        await self.blockbee.__aenter__()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup all async API clients"""
        if self.openprovider:
            await self.openprovider.__aexit__(exc_type, exc_val, exc_tb)
        if self.cloudflare:
            await self.cloudflare.__aexit__(exc_type, exc_val, exc_tb)
        if self.blockbee:
            await self.blockbee.__aexit__(exc_type, exc_val, exc_tb)

logger.info("✅ Expanded async API implementations loaded")