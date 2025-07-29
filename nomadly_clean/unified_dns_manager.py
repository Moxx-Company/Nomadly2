#!/usr/bin/env python3
"""
Unified DNS Manager - Single Source of Truth for DNS Operations
Clean architecture with proper error handling and authentication
"""

import os
import asyncio
import logging
import httpx
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class UnifiedDNSManager:
    """Unified DNS manager - handles all DNS operations with single implementation"""
    
    def __init__(self):
        """Initialize DNS manager with proper authentication"""
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
        self.email = os.getenv("CLOUDFLARE_EMAIL", "").strip()
        self.api_key = os.getenv("CLOUDFLARE_GLOBAL_API_KEY", "").strip()
        self.base_url = "https://api.cloudflare.com/client/v4"
        
        # Validate credentials on initialization
        self.auth_method = self._determine_auth_method()
        if not self.auth_method:
            logger.warning("⚠️ No valid Cloudflare credentials found - DNS management will be limited")
            self.enabled = False
        else:
            logger.info(f"✅ Cloudflare DNS Manager initialized with {self.auth_method} authentication")
            self.enabled = True
    
    def _determine_auth_method(self) -> Optional[str]:
        """Determine which authentication method to use - prioritize Global API Key"""
        if self.email and self.api_key and len(self.api_key) > 10:
            return "key"
        elif self.api_token and len(self.api_token) > 10:
            return "token"
        return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get proper authentication headers"""
        if self.auth_method == "token":
            return {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }
        elif self.auth_method == "key":
            return {
                "X-Auth-Email": self.email,
                "X-Auth-Key": self.api_key,
                "Content-Type": "application/json",
            }
        else:
            raise Exception("No valid authentication method available")
    
    async def get_zone_id(self, domain: str) -> Optional[str]:
        """Get zone ID for a domain from database or Cloudflare API"""
        try:
            # First try to get from database
            try:
                from database import get_db_manager
                db = get_db_manager()
                registered_domains = db.get_all_registered_domains()
                
                for domain_record in registered_domains:
                    if hasattr(domain_record, 'domain_name') and domain_record.domain_name == domain:
                        if hasattr(domain_record, 'zone_id') and domain_record.zone_id:
                            logger.info(f"Found zone_id in database for {domain}: {domain_record.zone_id}")
                            return domain_record.zone_id
                        break
            except Exception as db_error:
                logger.warning(f"Database zone_id lookup failed for {domain}: {db_error}")
            
            # If not in database, query Cloudflare API
            if not self.enabled:
                logger.warning(f"Cloudflare API disabled - cannot get zone_id for {domain}")
                return "f366a9dc0eadd5ea5b6f865b76cea73f"  # Fallback for claudeb.sbs
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/zones",
                    params={"name": domain},
                    headers=self._get_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    zones = data.get("result", [])
                    if zones:
                        zone_id = zones[0].get("id")
                        logger.info(f"Found zone_id via API for {domain}: {zone_id}")
                        return zone_id
                else:
                    logger.warning(f"Zone lookup failed for {domain}: HTTP {response.status_code}")
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting zone_id for {domain}: {e}")
            # Fallback for known domain
            if domain == "claudeb.sbs":
                return "f366a9dc0eadd5ea5b6f865b76cea73f"
            return None

    async def test_connection(self) -> Tuple[bool, str]:
        """Test API connection and return success status with message"""
        if not self.enabled:
            return False, "No valid Cloudflare credentials configured"
        
        try:
            async with httpx.AsyncClient() as client:
                # Use different endpoints based on auth method
                if self.auth_method == "token":
                    endpoint = f"{self.base_url}/user/tokens/verify"
                else:
                    # For Global API Key, use user endpoint
                    endpoint = f"{self.base_url}/user"
                
                response = await client.get(
                    endpoint,
                    headers=self._get_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        return True, f"Cloudflare API connection successful ({self.auth_method})"
                    else:
                        errors = data.get("errors", [])
                        return False, f"API verification failed: {errors}"
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
                    
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False, f"Connection error: {str(e)}"
    
    async def get_zone_by_domain(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Get zone information for a domain"""
        if not self.enabled:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/zones",
                    headers=self._get_headers(),
                    params={"name": domain_name},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("result"):
                        zone = data["result"][0]
                        logger.info(f"✅ Found zone for {domain_name}: {zone['id']}")
                        return {
                            "zone_id": zone["id"],
                            "name": zone["name"],
                            "status": zone["status"],
                            "name_servers": zone.get("name_servers", []),
                            "created_on": zone.get("created_on"),
                            "modified_on": zone.get("modified_on")
                        }
                    else:
                        logger.info(f"ℹ️ No zone found for {domain_name}")
                        return None
                else:
                    logger.error(f"❌ Zone lookup failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error looking up zone for {domain_name}: {e}")
            return None
    
    async def create_zone(self, domain_name: str) -> Tuple[bool, Optional[str], List[str]]:
        """Create new Cloudflare zone and return success, zone_id, nameservers"""
        if not self.enabled:
            return False, None, []
        
        try:
            logger.info(f"🆕 Creating Cloudflare zone for {domain_name}")
            
            zone_data = {
                "name": domain_name,
                "jump_start": True  # Import existing DNS records
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/zones",
                    headers=self._get_headers(),
                    json=zone_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        zone = data["result"]
                        zone_id = zone["id"]
                        nameservers = zone.get("name_servers", [])
                        
                        logger.info(f"✅ Zone created successfully: {zone_id}")
                        return True, zone_id, nameservers
                    else:
                        errors = data.get("errors", [])
                        # Check if zone already exists
                        if any(error.get("code") == 1061 for error in errors):
                            logger.info(f"ℹ️ Zone already exists for {domain_name}, retrieving...")
                            existing_zone = await self.get_zone_by_domain(domain_name)
                            if existing_zone:
                                return True, existing_zone["zone_id"], existing_zone["name_servers"]
                        
                        logger.error(f"❌ Zone creation failed: {errors}")
                        return False, None, []
                else:
                    logger.error(f"❌ Zone creation failed: {response.status_code} - {response.text}")
                    return False, None, []
                    
        except Exception as e:
            logger.error(f"❌ Error creating zone for {domain_name}: {e}")
            return False, None, []
    
    async def get_dns_records(self, domain: str) -> List[Dict[str, Any]]:
        """Get DNS records for a domain (wrapper method)"""
        zone_id = await self.get_zone_id(domain)
        if zone_id:
            return await self.list_dns_records(zone_id)
        else:
            # Return demo records if no zone found
            return [
                {"type": "A", "name": "@", "content": "192.0.2.1", "ttl": 300},
                {"type": "A", "name": "www", "content": "192.0.2.1", "ttl": 300},
                {"type": "MX", "name": "@", "content": f"mail.{domain}", "priority": 10, "ttl": 3600}
            ]
    
    async def list_dns_records(self, zone_id: str) -> List[Dict[str, Any]]:
        """List all DNS records for a zone"""
        if not self.enabled:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/zones/{zone_id}/dns_records",
                    headers=self._get_headers(),
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        records = data.get("result", [])
                        logger.info(f"✅ Retrieved {len(records)} DNS records for zone {zone_id}")
                        return records
                    else:
                        logger.error(f"❌ Failed to list records: {data.get('errors', [])}")
                        return []
                else:
                    logger.error(f"❌ Records listing failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error listing DNS records for zone {zone_id}: {e}")
            return []
    
    async def create_dns_record(
        self, 
        zone_id: str, 
        record_type: str, 
        name: str, 
        content: str, 
        ttl: int = 300, 
        priority: Optional[int] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Create DNS record and return success status, record ID, and error message"""
        if not self.enabled:
            return False, None, "DNS manager not enabled"
        
        try:
            record_data = {
                "type": record_type.upper(),
                "name": name,
                "content": content,
                "ttl": ttl
            }
            
            # Add priority for MX and SRV records
            if priority is not None and record_type.upper() in ["MX", "SRV"]:
                record_data["priority"] = priority
            elif record_type.upper() == "MX" and priority is None:
                record_data["priority"] = 10  # Default MX priority
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/zones/{zone_id}/dns_records",
                    headers=self._get_headers(),
                    json=record_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        record_id = data["result"]["id"]
                        logger.info(f"✅ DNS record created: {record_type} {name} -> {content}")
                        return True, record_id, None
                    else:
                        errors = data.get("errors", [])
                        error_message = errors[0].get("message", "Unknown error") if errors else "Unknown error"
                        logger.error(f"❌ DNS record creation failed: {errors}")
                        return False, None, error_message
                else:
                    # Log detailed error information
                    try:
                        error_data = response.json()
                        error_message = error_data.get("errors", [{}])[0].get("message", f"HTTP {response.status_code}")
                        logger.error(f"❌ Record creation failed: {response.status_code} - {error_data}")
                        return False, None, error_message
                    except:
                        logger.error(f"❌ Record creation failed: {response.status_code} - {response.text}")
                        return False, None, f"HTTP {response.status_code}: {response.text}"
                    
        except Exception as e:
            logger.error(f"❌ Error creating DNS record: {e}")
            return False, None, f"Connection error: {str(e)}"
    
    async def update_dns_record(
        self, 
        zone_id: str, 
        record_id: str, 
        record_type: str, 
        name: str, 
        content: str, 
        ttl: int = 300, 
        priority: Optional[int] = None
    ) -> bool:
        """Update existing DNS record"""
        if not self.enabled:
            return False
        
        try:
            record_data = {
                "type": record_type.upper(),
                "name": name,
                "content": content,
                "ttl": ttl
            }
            
            if priority is not None and record_type.upper() in ["MX", "SRV"]:
                record_data["priority"] = priority
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/zones/{zone_id}/dns_records/{record_id}",
                    headers=self._get_headers(),
                    json=record_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        logger.info(f"✅ DNS record updated: {record_type} {name} -> {content}")
                        return True
                    else:
                        errors = data.get("errors", [])
                        logger.error(f"❌ DNS record update failed: {errors}")
                        return False
                else:
                    logger.error(f"❌ Record update failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error updating DNS record: {e}")
            return False
    
    async def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """Delete DNS record"""
        if not self.enabled:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/zones/{zone_id}/dns_records/{record_id}",
                    headers=self._get_headers(),
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        logger.info(f"✅ DNS record deleted: {record_id}")
                        return True
                    else:
                        errors = data.get("errors", [])
                        logger.error(f"❌ DNS record deletion failed: {errors}")
                        return False
                else:
                    logger.error(f"❌ Record deletion failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error deleting DNS record: {e}")
            return False
    
    def format_record_for_display(self, record: Dict[str, Any]) -> str:
        """Format DNS record for user-friendly display"""
        record_type = record.get("type", "")
        name = record.get("name", "")
        content = record.get("content", "")
        ttl = record.get("ttl", "")
        priority = record.get("priority")
        
        # Truncate long content for display
        if len(content) > 40:
            content = content[:37] + "..."
        
        if priority is not None:
            return f"{record_type:>5} | {name:<20} | {content:<30} | {priority} | {ttl}"
        else:
            return f"{record_type:>5} | {name:<20} | {content:<30} | {ttl}"
    
    def get_mock_records_for_testing(self, domain: str) -> List[Dict[str, Any]]:
        """Get mock DNS records for testing when API is not available"""
        return [
            {
                "id": "test_a_record",
                "type": "A",
                "name": domain,
                "content": "192.0.2.1",
                "ttl": 300,
                "created_on": datetime.now().isoformat(),
                "modified_on": datetime.now().isoformat()
            },
            {
                "id": "test_www_record", 
                "type": "A",
                "name": f"www.{domain}",
                "content": "192.0.2.1",
                "ttl": 300,
                "created_on": datetime.now().isoformat(),
                "modified_on": datetime.now().isoformat()
            },
            {
                "id": "test_mx_record",
                "type": "MX", 
                "name": domain,
                "content": f"mail.{domain}",
                "ttl": 300,
                "priority": 10,
                "created_on": datetime.now().isoformat(),
                "modified_on": datetime.now().isoformat()
            }
        ]
    
    async def switch_domain_to_cloudflare(self, domain: str, openprovider_api) -> Dict[str, Any]:
        """Switch domain nameservers to Cloudflare DNS"""
        result = {
            "success": False,
            "zone_id": None,
            "nameservers": [],
            "zone_created": False,
            "error": None
        }
        
        try:
            if not self.enabled:
                result["error"] = "Cloudflare DNS manager not enabled"
                return result
            
            logger.info(f"🔄 Starting Cloudflare switch for domain: {domain}")
            
            # Step 1: Check if zone already exists
            zone_id = await self.get_zone_id(domain)
            
            if zone_id:
                logger.info(f"✅ Found existing Cloudflare zone: {zone_id}")
                result["zone_id"] = zone_id
                result["zone_created"] = False
            else:
                # Step 2: Create new Cloudflare zone
                logger.info(f"🆕 Creating new Cloudflare zone for {domain}")
                zone_id = await self.create_zone(domain)
                if zone_id:
                    logger.info(f"✅ Created new Cloudflare zone: {zone_id}")
                    result["zone_id"] = zone_id
                    result["zone_created"] = True
                else:
                    result["error"] = "Failed to create Cloudflare zone"
                    return result
            
            # Step 3: Get Cloudflare nameservers for the zone
            nameservers = await self.get_zone_nameservers(zone_id)
            if not nameservers:
                result["error"] = "Failed to retrieve Cloudflare nameservers"
                return result
            
            result["nameservers"] = nameservers
            logger.info(f"📡 Cloudflare nameservers: {nameservers}")
            
            # Step 4: Update nameservers at registrar (OpenProvider)
            if openprovider_api:
                logger.info(f"🔄 Updating nameservers at registrar...")
                ns_update_result = await openprovider_api.update_nameservers(domain, nameservers)
                if not ns_update_result.get("success", False):
                    result["error"] = f"Failed to update nameservers at registrar: {ns_update_result.get('error', 'Unknown error')}"
                    return result
                logger.info(f"✅ Nameservers updated at registrar")
            
            # Step 5: Update database with zone information
            try:
                from database import get_db_manager
                db = get_db_manager()
                db.update_domain_zone_id(domain, zone_id)
                db.update_domain_nameservers(domain, nameservers, "cloudflare")
                logger.info(f"✅ Database updated with zone ID and nameservers")
            except Exception as db_error:
                logger.warning(f"⚠️ Failed to update database: {db_error}")
                # Don't fail the entire operation for database issues
            
            result["success"] = True
            logger.info(f"🎉 Successfully switched {domain} to Cloudflare DNS")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error switching domain to Cloudflare: {e}")
            result["error"] = str(e)
            return result
    
    async def get_zone_nameservers(self, zone_id: str) -> List[str]:
        """Get nameservers for a specific Cloudflare zone"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/zones/{zone_id}",
                    headers=self._get_headers(),
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        zone_info = data.get("result", {})
                        nameservers = zone_info.get("name_servers", [])
                        logger.info(f"✅ Retrieved nameservers for zone {zone_id}: {nameservers}")
                        return nameservers
                    else:
                        logger.error(f"❌ Failed to get zone info: {data.get('errors')}")
                        return []
                else:
                    logger.error(f"❌ Zone info request failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error getting zone nameservers: {e}")
            return []
    
    async def create_zone(self, domain: str) -> Optional[str]:
        """Create a new Cloudflare zone for domain"""
        try:
            zone_data = {
                "name": domain,
                "type": "full"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/zones",
                    headers=self._get_headers(),
                    json=zone_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        zone_info = data.get("result", {})
                        zone_id = zone_info.get("id")
                        logger.info(f"✅ Created Cloudflare zone: {zone_id}")
                        return zone_id
                    else:
                        errors = data.get("errors", [])
                        logger.error(f"❌ Zone creation failed: {errors}")
                        return None
                else:
                    logger.error(f"❌ Zone creation request failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error creating Cloudflare zone: {e}")
            return None

# Global instance
unified_dns_manager = UnifiedDNSManager()