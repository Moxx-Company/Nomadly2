"""
OpenProvider API Integration for Nomadly3
Complete implementation for domain registration, user creation, and nameserver management
"""

import logging
import aiohttp
import json
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from ..core.config import config
from ..core.external_services import OpenProviderServiceInterface
from ..repositories.external_integration_repo import (
    OpenProviderIntegrationRepository, NameserverOperationRepository, APIUsageLogRepository
)

logger = logging.getLogger(__name__)

class OpenProviderAPI(OpenProviderServiceInterface):
    """Complete OpenProvider API integration for domain registration"""
    
    def __init__(self):
        self.username = config.OPENPROVIDER_USERNAME
        self.password = config.OPENPROVIDER_PASSWORD
        self.base_url = "https://api.openprovider.eu/v1beta"
        
        # Create basic auth header
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        
        # Repository dependencies
        self.openprovider_repo = OpenProviderIntegrationRepository()
        self.nameserver_operation_repo = NameserverOperationRepository()
        self.api_usage_repo = APIUsageLogRepository()
    
    async def check_domain_availability(self, domain_name: str) -> Dict[str, Any]:
        """Check if domain is available for registration"""
        start_time = datetime.now()
        
        # Split domain into name and extension
        parts = domain_name.split('.')
        if len(parts) < 2:
            return {"success": False, "error": "Invalid domain format"}
        
        domain_name_part = '.'.join(parts[:-1])
        extension = parts[-1]
        
        payload = {
            "domains": [{
                "name": domain_name_part,
                "extension": extension
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/domains/check",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint="/domains/check",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200:
                        domain_data = response_data.get("data", {}).get("results", [])
                        if domain_data:
                            domain_info = domain_data[0]
                            is_available = domain_info.get("status") == "free"
                            
                            logger.info(f"Domain availability check for {domain_name}: {'available' if is_available else 'not available'}")
                            
                            return {
                                "success": True,
                                "domain_name": domain_name,
                                "available": is_available,
                                "status": domain_info.get("status"),
                                "price": domain_info.get("price"),
                                "premium": domain_info.get("is_premium", False),
                                "openprovider_data": domain_info
                            }
                    
                    error_msg = response_data.get("desc", "Unknown error")
                    logger.error(f"Failed to check domain availability for {domain_name}: {error_msg}")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "openprovider_response": response_data
                    }
                    
        except Exception as e:
            logger.error(f"Exception checking domain availability for {domain_name}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> str:
        """Create contact handle for domain registration"""
        start_time = datetime.now()
        
        # Generate anonymous contact data if not provided
        if not contact_data:
            contact_data = await self._generate_anonymous_contact()
        
        payload = {
            "first_name": contact_data.get("first_name", "Anonymous"),
            "last_name": contact_data.get("last_name", "User"),
            "full_name": f"{contact_data.get('first_name', 'Anonymous')} {contact_data.get('last_name', 'User')}",
            "initials": contact_data.get("initials", "AU"),
            "gender": contact_data.get("gender", "M"),
            "birth_date": contact_data.get("birth_date", "1990-01-01"),
            "birth_place": contact_data.get("birth_place", "Unknown"),
            "birth_country": contact_data.get("birth_country", "NL"),
            "email": contact_data.get("email", "noreply@cloakhost.ru"),
            "phone": {
                "country_code": contact_data.get("phone_country", "+31"),
                "area_code": contact_data.get("phone_area", "20"),
                "subscriber_number": contact_data.get("phone_number", "1234567")
            },
            "address": {
                "street": contact_data.get("street", "Privacy Street"),
                "number": contact_data.get("number", "1"),
                "suffix": contact_data.get("suffix", ""),
                "zipcode": contact_data.get("zipcode", "1000AA"),
                "city": contact_data.get("city", "Amsterdam"),
                "state": contact_data.get("state", "NH"),
                "country": contact_data.get("country", "NL")
            },
            "is_private": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/customers",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint="/customers",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200:
                        contact_handle = response_data.get("data", {}).get("handle")
                        if contact_handle:
                            logger.info(f"Successfully created OpenProvider contact: {contact_handle}")
                            return contact_handle
                    
                    error_msg = response_data.get("desc", "Unknown error")
                    logger.error(f"Failed to create OpenProvider contact: {error_msg}")
                    raise Exception(f"Contact creation failed: {error_msg}")
                    
        except Exception as e:
            logger.error(f"Exception creating OpenProvider contact: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
    
    async def register_domain(self, domain_name: str, contact_handle: str, 
                             period: int = 1, nameservers: List[str] = None) -> Dict[str, Any]:
        """Register a domain with OpenProvider"""
        start_time = datetime.now()
        
        # Split domain into name and extension
        parts = domain_name.split('.')
        domain_name_part = '.'.join(parts[:-1])
        extension = parts[-1]
        
        payload = {
            "domain": {
                "name": domain_name_part,
                "extension": extension
            },
            "period": period,
            "owner_handle": contact_handle,
            "admin_handle": contact_handle,
            "tech_handle": contact_handle,
            "billing_handle": contact_handle,
            "auto_renew": "on",
            "is_private_whois": True
        }
        
        if nameservers:
            payload["name_servers"] = [{"name": ns} for ns in nameservers]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/domains",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint="/domains",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200:
                        domain_data = response_data.get("data", {})
                        domain_id = str(domain_data.get("id"))
                        
                        logger.info(f"Successfully registered domain {domain_name} with ID: {domain_id}")
                        
                        return {
                            "success": True,
                            "domain_id": domain_id,
                            "domain_name": domain_name,
                            "registration_date": datetime.utcnow(),
                            "expiry_date": datetime.utcnow() + timedelta(days=365 * period),
                            "nameservers": nameservers or [],
                            "openprovider_data": domain_data
                        }
                    
                    error_msg = response_data.get("desc", "Unknown error")
                    logger.error(f"Failed to register domain {domain_name}: {error_msg}")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "openprovider_response": response_data
                    }
                    
        except Exception as e:
            logger.error(f"Exception registering domain {domain_name}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def update_nameservers(self, domain_id: str, nameservers: List[str]) -> Dict[str, Any]:
        """Update nameservers for a domain"""
        start_time = datetime.now()
        
        # Get integration record for tracking
        integration = self.openprovider_repo.get_by_openprovider_id(domain_id)
        
        # Create nameserver operation record
        operation = self.nameserver_operation_repo.create_operation(
            openprovider_integration_id=integration.id if integration else None,
            operation_type="update_nameservers",
            old_nameservers=[],  # Could fetch current ones first
            new_nameservers=nameservers
        )
        
        payload = {
            "name_servers": [{"name": ns} for ns in nameservers]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.base_url}/domains/{domain_id}",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/domains/{domain_id}",
                        method="PUT",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200:
                        # Update operation status
                        self.nameserver_operation_repo.update_operation_status(
                            operation.id,
                            status="success",
                            api_response=response_data
                        )
                        
                        logger.info(f"Successfully updated nameservers for domain {domain_id}")
                        
                        return {
                            "success": True,
                            "domain_id": domain_id,
                            "nameservers": nameservers,
                            "openprovider_data": response_data.get("data", {})
                        }
                    
                    error_msg = response_data.get("desc", "Unknown error")
                    
                    # Update operation status
                    self.nameserver_operation_repo.update_operation_status(
                        operation.id,
                        status="failed",
                        api_response=response_data,
                        error_message=error_msg
                    )
                    
                    logger.error(f"Failed to update nameservers for domain {domain_id}: {error_msg}")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "openprovider_response": response_data
                    }
                    
        except Exception as e:
            # Update operation status
            self.nameserver_operation_repo.update_operation_status(
                operation.id,
                status="failed",
                error_message=str(e)
            )
            
            logger.error(f"Exception updating nameservers for domain {domain_id}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def get_domain_info(self, domain_id: str) -> Dict[str, Any]:
        """Get domain information from OpenProvider"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/domains/{domain_id}",
                    headers=self.headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        domain_data = response_data.get("data", {})
                        logger.info(f"Retrieved domain info for {domain_id}")
                        return domain_data
                    else:
                        logger.error(f"Failed to get domain info for {domain_id}: {response_data}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Exception getting domain info for {domain_id}: {str(e)}")
            return {}
    
    async def renew_domain(self, domain_id: str, period: int = 1) -> Dict[str, Any]:
        """Renew a domain registration"""
        payload = {
            "period": period
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/domains/{domain_id}/renew",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        logger.info(f"Successfully renewed domain {domain_id} for {period} years")
                        return {
                            "success": True,
                            "domain_id": domain_id,
                            "period": period,
                            "openprovider_data": response_data.get("data", {})
                        }
                    
                    error_msg = response_data.get("desc", "Unknown error")
                    logger.error(f"Failed to renew domain {domain_id}: {error_msg}")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "openprovider_response": response_data
                    }
                    
        except Exception as e:
            logger.error(f"Exception renewing domain {domain_id}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def _generate_anonymous_contact(self) -> Dict[str, Any]:
        """Generate anonymous contact data for privacy-focused registrations"""
        import random
        import string
        
        # Generate random data for privacy
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        return {
            "first_name": "Privacy",
            "last_name": f"User{random_suffix[:3].upper()}",
            "initials": "PU",
            "gender": "M",
            "birth_date": "1990-01-01",
            "birth_place": "Unknown",
            "birth_country": "NL",
            "email": "noreply@cloakhost.ru",
            "phone_country": "+31",
            "phone_area": "20",
            "phone_number": f"123{random.randint(1000, 9999)}",
            "street": "Privacy Street",
            "number": str(random.randint(1, 999)),
            "zipcode": "1000AA",
            "city": "Amsterdam",
            "state": "NH",
            "country": "NL"
        }
    
    async def _log_api_usage(self, endpoint: str, method: str, status: int,
                            request_data: Dict[str, Any] = None,
                            response_data: Dict[str, Any] = None,
                            response_time_ms: int = None):
        """Log API usage for monitoring"""
        try:
            self.api_usage_repo.log_api_call(
                service_name="openprovider",
                api_endpoint=endpoint,
                http_method=method,
                response_status=status,
                request_data=request_data,
                response_data=response_data,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.error(f"Failed to log API usage: {str(e)}")
    
    async def get_domain_list(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get list of domains in account"""
        try:
            params = {
                "limit": limit,
                "offset": offset
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/domains",
                    headers=self.headers,
                    params=params
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        domains = response_data.get("data", {}).get("results", [])
                        logger.info(f"Retrieved {len(domains)} domains from OpenProvider")
                        return domains
                    else:
                        logger.error(f"Failed to get domain list: {response_data}")
                        return []
                        
        except Exception as e:
            logger.error(f"Exception getting domain list: {str(e)}")
            return []