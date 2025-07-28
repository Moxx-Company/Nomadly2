"""
Production Cloudflare API - NO MOCK/FALLBACK FUNCTIONALITY
Fails cleanly if credentials are invalid - forces proper API setup
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class CloudflareAPI:
    """Production Cloudflare API - no mock functionality"""

    def __init__(self, email=None, api_key=None, api_token=None):
        self.email = email or os.getenv("CLOUDFLARE_EMAIL")
        self.api_key = api_key or os.getenv("CLOUDFLARE_GLOBAL_API_KEY")
        self.api_token = api_token or os.getenv("CLOUDFLARE_API_TOKEN")
        self.base_url = "https://api.cloudflare.com/client/v4"

        # Validate credentials on initialization
        if not self._has_valid_credentials():
            raise Exception(
                "CLOUDFLARE CREDENTIALS REQUIRED: Set CLOUDFLARE_EMAIL + CLOUDFLARE_GLOBAL_API_KEY or CLOUDFLARE_API_TOKEN"
            )

    def _has_valid_credentials(self) -> bool:
        """Check if we have valid credentials"""
        return (self.email and self.api_key) or self.api_token

    def _get_headers(self):
        """Get proper authentication headers"""
        if self.email and self.api_key:
            return {
                "X-Auth-Email": self.email,
                "X-Auth-Key": self.api_key,
                "Content-Type": "application/json",
            }
        elif self.api_token:
            # Validate and clean token format
            token_str = str(self.api_token).strip()
            if not token_str or len(token_str) < 10:
                logger.error(f"Invalid Cloudflare token format: token length={len(token_str)}")
                raise Exception("Invalid Cloudflare API token format")
            
            # Additional validation - token should not contain Bearer prefix
            if token_str.lower().startswith("bearer "):
                token_str = token_str[7:].strip()
                logger.info("Removed duplicate Bearer prefix from token")
            
            return {
                "Authorization": f"Bearer {token_str}",
                "Content-Type": "application/json",
            }
        else:
            raise Exception("No valid Cloudflare credentials configured")

    def create_zone(self, domain_name: str) -> Tuple[bool, Optional[str], List[str]]:
        """Create a new DNS zone and return success, cloudflare_zone_id, and nameservers - WORKING VERSION"""
        try:
            url = f"{self.base_url}/zones"
            data = {"name": domain_name}

            response = requests.post(url, json=data, headers=self._get_headers(), timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    zone_data = result.get("result", {})
                    cloudflare_zone_id = zone_data.get("id")
                    nameservers = zone_data.get("name_servers", [])

                    logger.info(
                        f"Cloudflare zone created: {domain_name} (ID: {cloudflare_zone_id})"
                    )
                    return True, cloudflare_zone_id, nameservers
                else:
                    errors = result.get("errors", [])
                    # Check if zone already exists
                    if any(error.get("code") == 1061 for error in errors):
                        logger.info(
                            f"Zone already exists for {domain_name}, retrieving existing zone"
                        )
                        existing_zone = self.get_zone_by_domain(domain_name)
                        if existing_zone.get("success"):
                            cloudflare_zone_id = existing_zone["zone"]["id"]
                            nameservers = existing_zone["zone"].get("name_servers", [])
                            logger.info(f"Retrieved existing zone: {cloudflare_zone_id}")
                            return True, cloudflare_zone_id, nameservers

                    logger.error(f"Zone creation failed: {errors}")
                    return False, None, []
            else:
                logger.error(f"Zone creation failed: {response.status_code}")
                return False, None, []

        except Exception as e:
            logger.error(f"Zone creation error: {e}")
            return False, None, []

    def get_zone_nameservers(self, cloudflare_zone_id: str) -> List[str]:
        """Get nameservers for a zone by zone ID"""
        try:
            url = f"{self.base_url}/zones/{cloudflare_zone_id}"
            headers = self._get_headers()

            response = requests.get(url, headers=headers, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    zone_data = result.get("result", {})
                    nameservers = zone_data.get("name_servers", [])
                    logger.info(
                        f"Retrieved nameservers for zone {cloudflare_zone_id}: {nameservers}"
                    )
                    return nameservers
                else:
                    errors = result.get("errors", [])
                    logger.error(f"Failed to get zone nameservers: {errors}")
                    return []
            else:
                logger.error(f"HTTP {response.status_code}: {response.text[:500]}")
                return []

        except Exception as e:
            logger.error(f"Zone nameserver lookup exception: {e}")
            return []

    def get_zone_by_domain(self, domain_name: str) -> Dict:
        """Get zone information by domain name"""
        try:
            url = f"{self.base_url}/zones"
            params = {"name": domain_name}
            headers = self._get_headers()

            response = requests.get(url, params=params, headers=headers, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("result"):
                    zones = result.get("result", [])
                    if zones:
                        zone = zones[0]  # First matching zone
                        logger.info(f"Found zone for {domain_name}: {zone.get('id')}")
                        return {"success": True, "zone": zone}
                    else:
                        logger.info(f"No zone found for {domain_name}")
                        return {"success": False, "error": "Zone not found"}
                else:
                    errors = result.get("errors", [])
                    logger.error(f"Zone lookup failed: {errors}")
                    return {"success": False, "error": str(errors)}
            else:
                logger.error(f"HTTP {response.status_code}: {response.text[:500]}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Zone lookup exception: {e}")
            return {"success": False, "error": str(e)}

    async def list_zones(self) -> List[Dict]:
        """List all zones - Missing method fix"""
        try:
            url = f"{self.base_url}/zones"
            headers = self._get_headers()

            response = requests.get(url, headers=headers, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    zones = result.get("result", [])
                    logger.info(f"Retrieved {len(zones)} zones")
                    return zones
                else:
                    errors = result.get("errors", [])
                    logger.error(f"Zone listing failed: {errors}")
                    return []
            else:
                logger.error(f"HTTP {response.status_code}: {response.text[:500]}")
                return []

        except Exception as e:
            logger.error(f"Zone listing exception: {e}")
            return []

    def create_dns_record(self, cloudflare_zone_id: str, record_data: dict) -> Optional[dict]:
        """Create DNS record - Synchronous method fix"""
        try:
            url = f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records"
            headers = self._get_headers()

            response = requests.post(url, json=record_data, headers=headers, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"DNS record created: {record_data}")
                    return result.get("result", {})
                else:
                    errors = result.get("errors", [])
                    logger.error(f"DNS record creation failed: {errors}")
                    return None
            else:
                logger.error(f"HTTP {response.status_code}: {response.text[:500]}")
                return None

        except Exception as e:
            logger.error(f"DNS record creation error: {e}")
            return None

    async def create_dns_record_async(self, cloudflare_zone_id: str, record_data: dict) -> Optional[dict]:
        """Create DNS record - ASYNC VERSION"""
        try:
            url = f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records"

            headers = self._get_headers()

            # Use aiohttp for async requests
            import aiohttp
            import asyncio

            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url, json=record_data, headers=headers
                ) as response:
                    result = await response.json()

                    if response.status == 200 and result.get("success"):
                        logger.info(f"DNS record created: {record_data}")
                        return result.get("result", {})
                    else:
                        errors = result.get("errors", [])
                        logger.error(f"DNS record creation failed: {errors}")
                        return None

        except Exception as e:
            logger.error(f"DNS record exception: {e}")
            return None

    def get_dns_records(self, domain_name: str) -> Dict[str, Any]:
        """Alias for list_dns_records for consistency"""
        return self.list_dns_records(domain_name)

    def list_dns_records(self, domain_name: str) -> Dict[str, Any]:
        """List DNS records for a domain - PRODUCTION ONLY"""
        try:
            # First get zone ID for domain
            cloudflare_zone_id = self._get_zone_id(domain_name)
            if not cloudflare_zone_id:
                return {"success": False, "error": f"Zone not found for {domain_name}"}

            url = f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records"
            headers = self._get_headers()

            response = requests.get(url, headers=headers, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    records = result.get("result", [])
                    logger.info(
                        f"Retrieved {len(records)} DNS records for {domain_name}"
                    )
                    return {"success": True, "records": records}
                else:
                    errors = result.get("errors", [])
                    logger.error(f"Failed to list DNS records: {errors}")
                    return {"success": False, "error": str(errors)}
            else:
                logger.error(f"HTTP {response.status_code}: {response.text[:500]}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"List DNS records exception: {e}")
            return {"success": False, "error": str(e)}

    async def get_zone_id(self, domain_name: str) -> Optional[str]:
        """Get zone ID for a domain - Public async method"""
        return self._get_zone_id(domain_name)

    async def get_nameservers(self, cloudflare_zone_id: str) -> Optional[List[str]]:
        """Get nameservers for a zone"""
        try:
            url = f"{self.base_url}/zones/{cloudflare_zone_id}"
            headers = self._get_headers()

            response = requests.get(url, headers=headers, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("result"):
                    zone = result.get("result", {})
                    nameservers = zone.get("name_servers", [])
                    logger.info(f"Found nameservers for zone {cloudflare_zone_id}: {nameservers}")
                    return nameservers

            logger.warning(f"Could not get nameservers for zone {cloudflare_zone_id}")
            return None

        except Exception as e:
            logger.error(f"Get nameservers exception: {e}")
            return None

    def _get_zone_id(self, domain_name: str) -> Optional[str]:
        """Get zone ID for a domain"""
        try:
            url = f"{self.base_url}/zones"
            headers = self._get_headers()
            params = {"name": domain_name}

            response = requests.get(url, headers=headers, params=params, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("result"):
                    zones = result.get("result", [])
                    if zones:
                        cloudflare_zone_id = zones[0].get("id")
                        logger.info(f"Found zone ID {cloudflare_zone_id} for {domain_name}")
                        return cloudflare_zone_id

            logger.warning(f"Zone not found for domain {domain_name}")
            return None

        except Exception as e:
            logger.error(f"Zone lookup exception: {e}")
            return None

    def add_dns_record(
        self,
        domain_name: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 300,
    ) -> Dict[str, Any]:
        """Add DNS record - PRODUCTION ONLY"""
        try:
            # Get zone ID for domain
            cloudflare_zone_id = self._get_zone_id(domain_name)
            if not cloudflare_zone_id:
                return {"success": False, "error": f"Zone not found for {domain_name}"}

            url = f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records"
            headers = self._get_headers()

            record_data = {
                "type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
            }

            response = requests.post(url, json=record_data, headers=headers, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    record = result.get("result", {})
                    logger.info(f"DNS record added: {record_type} {name} -> {content}")
                    return {"success": True, "record": record}
                else:
                    # Return the full response text for enhanced error parsing
                    logger.error(f"Failed to add DNS record: {response.text}")
                    return {"success": False, "error": response.text}
            else:
                logger.error(f"HTTP {response.status_code}: {response.text[:500]}")
                return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Add DNS record exception: {e}")
            return {"success": False, "error": str(e)}

    def update_dns_record(self, domain_name: str, record_id: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a DNS record - PRODUCTION ONLY"""
        try:
            # First get zone ID for domain
            cloudflare_zone_id = self._get_zone_id(domain_name)
            if not cloudflare_zone_id:
                return {"success": False, "error": f"Zone not found for {domain_name}"}

            url = f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records/{record_id}"
            headers = self._get_headers()

            response = requests.put(url, json=record_data, headers=headers, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"Updated DNS record {record_id} for {domain_name}")
                    return {"success": True, "result": result.get("result", {})}
                else:
                    errors = result.get("errors", [])
                    logger.error(f"Failed to update DNS record: {errors}")
                    return {"success": False, "error": str(errors)}
            else:
                error_text = response.text[:500]
                logger.error(f"HTTP {response.status_code}: {error_text}")
                return {"success": False, "error": error_text}

        except Exception as e:
            logger.error(f"Update DNS record exception: {e}")
            return {"success": False, "error": str(e)}

    def delete_dns_record(self, domain_name: str, record_id: str) -> Dict[str, Any]:
        """Delete DNS record - PRODUCTION ONLY"""
        try:
            # Get zone ID for domain
            cloudflare_zone_id = self._get_zone_id(domain_name)
            if not cloudflare_zone_id:
                return {"success": False, "error": f"Zone not found for {domain_name}"}

            url = f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records/{record_id}"
            headers = self._get_headers()

            response = requests.delete(url, headers=headers, timeout=8)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"DNS record deleted: {record_id} from {domain_name}")
                    return {"success": True}
                else:
                    errors = result.get("errors", [])
                    logger.error(f"Failed to delete DNS record: {errors}")
                    return {"success": False, "error": str(errors)}
            else:
                logger.error(f"HTTP {response.status_code}: {response.text[:500]}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Delete DNS record exception: {e}")
            return {"success": False, "error": str(e)}

    async def list_dns_records_async(self, domain_name: str) -> Dict[str, Any]:
        """Async version of list_dns_records"""
        return self.list_dns_records(domain_name)

    async def add_dns_record_async(
        self,
        domain_name: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 300,
        priority: int = None,
    ) -> Dict[str, Any]:
        """Async version of add_dns_record with priority support"""
        try:
            # Get zone ID for domain
            cloudflare_zone_id = self._get_zone_id(domain_name)
            if not cloudflare_zone_id:
                return {"success": False, "error": f"Zone not found for {domain_name}"}

            record_data = {
                "type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
            }

            # Add priority for MX records
            if record_type == "MX" and priority is not None:
                record_data["priority"] = priority

            url = f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records"
            headers = self._get_headers()

            response = requests.post(url, json=record_data, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"Created {record_type} record for {domain_name}")
                    return {"success": True, "result": result.get("result", {})}
                else:
                    errors = result.get("errors", [])
                    error_msg = str(errors)
                    logger.error(f"Failed to create DNS record: {errors}")
                    return {"success": False, "error": error_msg}
            else:
                error_text = response.text[:500]
                logger.error(f"HTTP {response.status_code}: {error_text}")
                return {"success": False, "error": error_text}

        except Exception as e:
            logger.error(f"Create DNS record exception: {e}")
            return {"success": False, "error": str(e)}

    async def delete_dns_record_async(
        self, domain_name: str, record_id: str
    ) -> Dict[str, Any]:
        """Async version of delete_dns_record"""
        return self.delete_dns_record(domain_name, record_id)
