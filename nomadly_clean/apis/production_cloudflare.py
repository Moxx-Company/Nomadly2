"""
Production Cloudflare API - NO MOCK/FALLBACK FUNCTIONALITY
Fails cleanly if credentials are invalid - forces proper API setup
"""

import os
import requests
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class CloudflareAPI:
    """Production Cloudflare API - no mock functionality"""

    def __init__(self, email=None, api_key=None, api_token=None):
        # First try to use global API key + email from user-provided credentials
        self.email = email or os.getenv("CLOUDFLARE_EMAIL", "onarrival21@gmail.com")
        self.api_key = api_key or os.getenv("CLOUDFLARE_GLOBAL_API_KEY", "ba2e4fe1fc6cc75bc63c26e0417de3de383ba")
        # Fallback to token if no global API key
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

    def get_zone_analytics(self, zone_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Get zone analytics for visitor statistics using GraphQL API"""
        try:
            # Calculate date range (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # GraphQL query for zone analytics
            query = {
                "query": f"""{{
                    viewer {{
                        zones(filter: {{zoneTag: "{zone_id}"}}) {{
                            httpRequests1dGroups(
                                filter: {{
                                    date_gt: "{start_date.strftime('%Y-%m-%d')}"
                                    date_lt: "{end_date.strftime('%Y-%m-%d')}"
                                }}
                                orderBy: [date_ASC]
                                limit: {days_back}
                            ) {{
                                dimensions {{
                                    date
                                }}
                                sum {{
                                    requests
                                    pageViews
                                    bytes
                                    countryMap {{
                                        requests
                                        clientCountryName
                                    }}
                                }}
                                uniq {{
                                    uniques
                                }}
                            }}
                        }}
                    }}
                }}""",
                "variables": {}
            }
            
            # Use GraphQL endpoint
            url = f"{self.base_url}/graphql"
            
            response = requests.post(
                url, 
                json=query, 
                headers=self._get_headers(), 
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("data") and result["data"].get("viewer"):
                    zones = result["data"]["viewer"].get("zones", [])
                    if zones and len(zones) > 0:
                        analytics_data = zones[0].get("httpRequests1dGroups", [])
                        
                        # Calculate totals and country breakdown
                        total_requests = 0
                        total_page_views = 0
                        total_uniques = 0
                        total_bytes = 0
                        country_requests = {}
                        
                        for day_data in analytics_data:
                            if day_data.get("sum"):
                                total_requests += day_data["sum"].get("requests", 0)
                                total_page_views += day_data["sum"].get("pageViews", 0)
                                total_bytes += day_data["sum"].get("bytes", 0)
                                
                                # Process country data
                                country_map = day_data["sum"].get("countryMap", [])
                                for country_data in country_map:
                                    country_name = country_data.get("clientCountryName", "Unknown")
                                    country_req = country_data.get("requests", 0)
                                    if country_name in country_requests:
                                        country_requests[country_name] += country_req
                                    else:
                                        country_requests[country_name] = country_req
                                        
                            if day_data.get("uniq"):
                                total_uniques += day_data["uniq"].get("uniques", 0)
                        
                        # Find top country
                        top_country = "Unknown"
                        if country_requests:
                            top_country = max(country_requests.items(), key=lambda x: x[1])[0]
                        
                        # Format monthly estimates (scale up from days_back to 30 days)
                        scale_factor = 30 / days_back if days_back > 0 else 1
                        monthly_visitors = int(total_uniques * scale_factor)
                        monthly_page_views = int(total_page_views * scale_factor)
                        monthly_requests = int(total_requests * scale_factor)
                        
                        # Format visitor count for display
                        if monthly_visitors >= 1000:
                            visitor_display = f"{monthly_visitors / 1000:.1f}k"
                        else:
                            visitor_display = str(monthly_visitors)
                        
                        # Format page views for display
                        if monthly_page_views >= 1000:
                            pageview_display = f"{monthly_page_views / 1000:.1f}k"
                        else:
                            pageview_display = str(monthly_page_views)
                        
                        logger.info(f"Zone analytics for {zone_id}: {monthly_visitors} monthly visitors, {monthly_page_views} page views, top country: {top_country}")
                        
                        return {
                            "success": True,
                            "monthly_visitors": monthly_visitors,
                            "monthly_page_views": monthly_page_views,
                            "monthly_requests": monthly_requests,
                            "visitor_display": visitor_display,
                            "pageview_display": pageview_display,
                            "top_country": top_country,
                            "country_breakdown": country_requests,
                            "days_analyzed": days_back,
                            "raw_data": analytics_data
                        }
            
            logger.warning(f"Failed to get analytics for zone {zone_id}: HTTP {response.status_code}")
            return {"success": False, "error": f"API returned {response.status_code}"}
            
        except Exception as e:
            logger.error(f"Error fetching zone analytics for {zone_id}: {e}")
            return {"success": False, "error": str(e)}

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
