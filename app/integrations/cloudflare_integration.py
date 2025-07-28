"""
Cloudflare API Integration for Nomadly3
Complete implementation for DNS zone management and record operations
"""

import logging
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..core.config import config
from ..core.external_services import CloudflareServiceInterface
from ..repositories.external_integration_repo import (
    CloudflareIntegrationRepository, DNSOperationRepository, APIUsageLogRepository
)

logger = logging.getLogger(__name__)

class CloudflareAPI(CloudflareServiceInterface):
    """Complete Cloudflare API integration for DNS management"""
    
    def __init__(self):
        self.api_token = config.CLOUDFLARE_API_TOKEN
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Repository dependencies
        self.cloudflare_repo = CloudflareIntegrationRepository()
        self.dns_operation_repo = DNSOperationRepository()
        self.api_usage_repo = APIUsageLogRepository()
    
    async def create_zone(self, domain_name: str, account_id: str = None) -> Dict[str, Any]:
        """Create a new DNS zone in Cloudflare"""
        start_time = datetime.now()
        
        payload = {
            "name": domain_name,
            "type": "full"
        }
        
        if account_id:
            payload["account"] = {"id": account_id}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/zones",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint="/zones",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("success"):
                        zone_data = response_data["result"]
                        logger.info(f"Successfully created Cloudflare zone for {domain_name}")
                        
                        return {
                            "success": True,
                            "zone_id": zone_data["id"],
                            "zone_name": zone_data["name"],
                            "nameservers": zone_data.get("name_servers", []),
                            "status": zone_data.get("status"),
                            "cloudflare_data": zone_data
                        }
                    else:
                        error_msg = response_data.get("errors", [{"message": "Unknown error"}])[0]["message"]
                        logger.error(f"Failed to create Cloudflare zone for {domain_name}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "cloudflare_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception creating Cloudflare zone for {domain_name}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def get_zone_nameservers(self, zone_id: str) -> List[str]:
        """Get nameservers for a Cloudflare zone"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/zones/{zone_id}",
                    headers=self.headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get("success"):
                        zone_data = response_data["result"]
                        nameservers = zone_data.get("name_servers", [])
                        logger.info(f"Retrieved nameservers for zone {zone_id}: {nameservers}")
                        return nameservers
                    else:
                        logger.error(f"Failed to get nameservers for zone {zone_id}: {response_data}")
                        return []
                        
        except Exception as e:
            logger.error(f"Exception getting nameservers for zone {zone_id}: {str(e)}")
            return []
    
    async def create_country_access_rule(self, zone_id: str, countries: List[str], 
                                       action: str = "block", description: str = None) -> Dict[str, Any]:
        """Create country-based access control using WAF Custom Rules"""
        start_time = datetime.now()
        
        # Build country expression for WAF Custom Rules
        country_list = " ".join([f'"{country.upper()}"' for country in countries])
        
        if action == "allow_only":
            # Allow only specified countries (block all others)
            expression = f"(not ip.src.country in {{{country_list}}})"
            action = "block"
            description = description or f"Allow only countries: {', '.join(countries)}"
        else:
            # Block specified countries
            expression = f"ip.src.country in {{{country_list}}}"
            description = description or f"Block countries: {', '.join(countries)}"
        
        payload = {
            "kind": "zone",
            "name": "Country access control",
            "phase": "http_request_firewall_custom",
            "rules": [{
                "expression": expression,
                "action": action,
                "description": description
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/zones/{zone_id}/rulesets",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/zones/{zone_id}/rulesets",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("success"):
                        ruleset_data = response_data["result"]
                        
                        # Store integration record
                        integration = self.cloudflare_repo.create_operation_record(
                            zone_id=zone_id,
                            operation_type="country_access_rule",
                            operation_data={
                                "countries": countries,
                                "action": action,
                                "expression": expression,
                                "ruleset_id": ruleset_data["id"]
                            },
                            operation_status="completed"
                        )
                        
                        logger.info(f"Successfully created country access rule for {zone_id}: {description}")
                        
                        return {
                            "success": True,
                            "ruleset_id": ruleset_data["id"],
                            "rule_id": ruleset_data["rules"][0]["id"],
                            "countries": countries,
                            "action": action,
                            "expression": expression,
                            "description": description,
                            "integration_id": integration.id,
                            "cloudflare_data": ruleset_data
                        }
                    else:
                        error_msg = response_data.get("errors", [{"message": "Unknown error"}])[0]["message"]
                        logger.error(f"Failed to create country access rule for {zone_id}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "cloudflare_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception creating country access rule for {zone_id}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def update_country_access_rule(self, zone_id: str, ruleset_id: str, 
                                       countries: List[str], action: str = "block",
                                       description: str = None) -> Dict[str, Any]:
        """Update existing country access rule"""
        start_time = datetime.now()
        
        # Build updated country expression
        country_list = " ".join([f'"{country.upper()}"' for country in countries])
        
        if action == "allow_only":
            expression = f"(not ip.src.country in {{{country_list}}})"
            action = "block"
            description = description or f"Allow only countries: {', '.join(countries)}"
        else:
            expression = f"ip.src.country in {{{country_list}}}"
            description = description or f"Block countries: {', '.join(countries)}"
        
        payload = {
            "expression": expression,
            "action": action,
            "description": description
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.base_url}/zones/{zone_id}/rulesets/{ruleset_id}/rules/1",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/zones/{zone_id}/rulesets/{ruleset_id}/rules/1",
                        method="PUT",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("success"):
                        rule_data = response_data["result"]
                        
                        # Update integration record
                        self.cloudflare_repo.update_operation_record(
                            zone_id,
                            operation_type="country_access_rule",
                            operation_data={
                                "countries": countries,
                                "action": action,
                                "expression": expression,
                                "ruleset_id": ruleset_id,
                                "updated": True
                            }
                        )
                        
                        logger.info(f"Successfully updated country access rule for {zone_id}: {description}")
                        
                        return {
                            "success": True,
                            "rule_id": rule_data["id"],
                            "countries": countries,
                            "action": action,
                            "expression": expression,
                            "description": description,
                            "cloudflare_data": rule_data
                        }
                    else:
                        error_msg = response_data.get("errors", [{"message": "Unknown error"}])[0]["message"]
                        logger.error(f"Failed to update country access rule for {zone_id}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "cloudflare_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception updating country access rule for {zone_id}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def get_country_access_rules(self, zone_id: str) -> Dict[str, Any]:
        """Get all country access rules for a zone"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/zones/{zone_id}/rulesets",
                    headers=self.headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get("success"):
                        rulesets = response_data["result"]
                        country_rules = []
                        
                        for ruleset in rulesets:
                            if ruleset.get("phase") == "http_request_firewall_custom":
                                for rule in ruleset.get("rules", []):
                                    expression = rule.get("expression", "")
                                    if "ip.src.country" in expression:
                                        country_rules.append({
                                            "ruleset_id": ruleset["id"],
                                            "rule_id": rule["id"],
                                            "expression": expression,
                                            "action": rule.get("action"),
                                            "description": rule.get("description"),
                                            "enabled": rule.get("enabled", True)
                                        })
                        
                        logger.info(f"Retrieved {len(country_rules)} country access rules for zone {zone_id}")
                        
                        return {
                            "success": True,
                            "rules": country_rules,
                            "total_rules": len(country_rules)
                        }
                    else:
                        logger.error(f"Failed to get country access rules for {zone_id}: {response_data}")
                        return {
                            "success": False,
                            "error": response_data.get("errors", [{"message": "Unknown error"}])[0]["message"],
                            "cloudflare_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception getting country access rules for {zone_id}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def delete_country_access_rule(self, zone_id: str, ruleset_id: str) -> bool:
        """Delete a country access rule"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/zones/{zone_id}/rulesets/{ruleset_id}",
                    headers=self.headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get("success"):
                        # Update integration record
                        self.cloudflare_repo.update_operation_record(
                            zone_id,
                            operation_type="country_access_rule",
                            operation_data={"deleted": True, "ruleset_id": ruleset_id}
                        )
                        
                        logger.info(f"Successfully deleted country access rule {ruleset_id} for zone {zone_id}")
                        return True
                    else:
                        logger.error(f"Failed to delete country access rule {ruleset_id}: {response_data}")
                        return False
                        
        except Exception as e:
            logger.error(f"Exception deleting country access rule {ruleset_id}: {str(e)}")
            return False
    
    async def create_continent_access_rule(self, zone_id: str, continents: List[str], 
                                         action: str = "block", description: str = None) -> Dict[str, Any]:
        """Create continent-based access control (AF, AS, EU, NA, OC, SA, AN)"""
        start_time = datetime.now()
        
        # Build continent expression
        continent_list = " ".join([f'"{continent.upper()}"' for continent in continents])
        
        if action == "allow_only":
            expression = f"(not ip.geoip.continent in {{{continent_list}}})"
            action = "block"
            description = description or f"Allow only continents: {', '.join(continents)}"
        else:
            expression = f"ip.geoip.continent in {{{continent_list}}}"
            description = description or f"Block continents: {', '.join(continents)}"
        
        payload = {
            "kind": "zone",
            "name": "Continent access control",
            "phase": "http_request_firewall_custom",
            "rules": [{
                "expression": expression,
                "action": action,
                "description": description
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/zones/{zone_id}/rulesets",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/zones/{zone_id}/rulesets",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("success"):
                        ruleset_data = response_data["result"]
                        
                        # Store integration record
                        integration = self.cloudflare_repo.create_operation_record(
                            zone_id=zone_id,
                            operation_type="continent_access_rule",
                            operation_data={
                                "continents": continents,
                                "action": action,
                                "expression": expression,
                                "ruleset_id": ruleset_data["id"]
                            },
                            operation_status="completed"
                        )
                        
                        logger.info(f"Successfully created continent access rule for {zone_id}: {description}")
                        
                        return {
                            "success": True,
                            "ruleset_id": ruleset_data["id"],
                            "rule_id": ruleset_data["rules"][0]["id"],
                            "continents": continents,
                            "action": action,
                            "expression": expression,
                            "description": description,
                            "integration_id": integration.id,
                            "cloudflare_data": ruleset_data
                        }
                    else:
                        error_msg = response_data.get("errors", [{"message": "Unknown error"}])[0]["message"]
                        logger.error(f"Failed to create continent access rule for {zone_id}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "cloudflare_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception creating continent access rule for {zone_id}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def create_advanced_geo_rule(self, zone_id: str, rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced geo-blocking rule with multiple conditions"""
        start_time = datetime.now()
        
        expressions = []
        
        # Build country conditions
        if "block_countries" in rule_config:
            country_list = " ".join([f'"{c.upper()}"' for c in rule_config["block_countries"]])
            expressions.append(f"ip.src.country in {{{country_list}}}")
        
        if "allow_countries" in rule_config:
            country_list = " ".join([f'"{c.upper()}"' for c in rule_config["allow_countries"]])
            expressions.append(f"(not ip.src.country in {{{country_list}}})")
        
        # Build continent conditions
        if "block_continents" in rule_config:
            continent_list = " ".join([f'"{c.upper()}"' for c in rule_config["block_continents"]])
            expressions.append(f"ip.geoip.continent in {{{continent_list}}}")
        
        # Build ASN conditions (for blocking specific ISPs/hosting providers)
        if "block_asn" in rule_config:
            asn_list = " ".join([str(asn) for asn in rule_config["block_asn"]])
            expressions.append(f"ip.geoip.asnum in {{{asn_list}}}")
        
        # Combine expressions
        if not expressions:
            return {
                "success": False,
                "error": "No geo-blocking conditions specified"
            }
        
        expression = " or ".join(expressions) if len(expressions) > 1 else expressions[0]
        
        payload = {
            "kind": "zone",
            "name": "Advanced geo-blocking",
            "phase": "http_request_firewall_custom",
            "rules": [{
                "expression": expression,
                "action": rule_config.get("action", "block"),
                "description": rule_config.get("description", "Advanced geo-blocking rule")
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/zones/{zone_id}/rulesets",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/zones/{zone_id}/rulesets",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("success"):
                        ruleset_data = response_data["result"]
                        
                        # Store integration record
                        integration = self.cloudflare_repo.create_operation_record(
                            zone_id=zone_id,
                            operation_type="advanced_geo_rule",
                            operation_data={
                                "rule_config": rule_config,
                                "expression": expression,
                                "ruleset_id": ruleset_data["id"]
                            },
                            operation_status="completed"
                        )
                        
                        logger.info(f"Successfully created advanced geo rule for {zone_id}")
                        
                        return {
                            "success": True,
                            "ruleset_id": ruleset_data["id"],
                            "rule_id": ruleset_data["rules"][0]["id"],
                            "expression": expression,
                            "rule_config": rule_config,
                            "integration_id": integration.id,
                            "cloudflare_data": ruleset_data
                        }
                    else:
                        error_msg = response_data.get("errors", [{"message": "Unknown error"}])[0]["message"]
                        logger.error(f"Failed to create advanced geo rule for {zone_id}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "cloudflare_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception creating advanced geo rule for {zone_id}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def get_geo_blocking_templates(self) -> Dict[str, Any]:
        """Get common geo-blocking rule templates"""
        templates = {
            "block_high_risk_countries": {
                "name": "Block High-Risk Countries",
                "description": "Block countries commonly associated with cyber attacks",
                "countries": ["CN", "RU", "KP", "IR"],
                "action": "block"
            },
            "allow_nato_countries": {
                "name": "Allow NATO Countries Only",
                "description": "Allow access only from NATO member countries",
                "countries": ["US", "CA", "GB", "FR", "DE", "IT", "ES", "TR", "GR", "PL", "RO", "NL", "BE", "CZ", "PT", "HU", "BG", "HR", "SK", "SI", "LT", "LV", "EE", "LU", "DK", "NO", "IS", "AL", "ME", "MK", "MT"],
                "action": "allow_only"
            },
            "block_vpn_hosting": {
                "name": "Block VPN/Hosting Providers",
                "description": "Block major VPN and hosting provider ASNs",
                "asn": [13335, 16509, 15169, 14061, 20473],  # Cloudflare, Amazon, Google, DigitalOcean, AS20473
                "action": "challenge"
            },
            "allow_eu_only": {
                "name": "EU Countries Only",
                "description": "Allow access only from European Union countries",
                "countries": ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"],
                "action": "allow_only"
            },
            "block_asia_pacific": {
                "name": "Block Asia-Pacific",
                "description": "Block entire Asia-Pacific region",
                "continents": ["AS", "OC"],
                "action": "block"
            }
        }
        
        return {
            "success": True,
            "templates": templates,
            "total_templates": len(templates)
        }
    
    async def create_dns_record(self, zone_id: str, record_type: str, name: str, 
                               content: str, ttl: int = 1, priority: int = None) -> Dict[str, Any]:
        """Create a DNS record in Cloudflare zone"""
        start_time = datetime.now()
        
        # Get integration record for tracking
        integration = self.cloudflare_repo.get_by_zone_id(zone_id)
        
        # Create operation record
        operation = self.dns_operation_repo.create_operation(
            cloudflare_integration_id=integration.id if integration else None,
            operation_type="create",
            record_type=record_type,
            record_name=name,
            record_content=content,
            ttl=ttl,
            priority=priority
        )
        
        payload = {
            "type": record_type,
            "name": name,
            "content": content,
            "ttl": ttl
        }
        
        if priority is not None and record_type in ["MX", "SRV"]:
            payload["priority"] = priority
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/zones/{zone_id}/dns_records",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/zones/{zone_id}/dns_records",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("success"):
                        record_data = response_data["result"]
                        
                        # Update operation status
                        self.dns_operation_repo.update_operation_status(
                            operation.id,
                            status="success",
                            cloudflare_record_id=record_data["id"],
                            api_response=response_data
                        )
                        
                        logger.info(f"Successfully created DNS record {record_type} {name} in zone {zone_id}")
                        
                        return {
                            "success": True,
                            "record_id": record_data["id"],
                            "record_type": record_data["type"],
                            "name": record_data["name"],
                            "content": record_data["content"],
                            "ttl": record_data["ttl"],
                            "cloudflare_data": record_data
                        }
                    else:
                        error_msg = response_data.get("errors", [{"message": "Unknown error"}])[0]["message"]
                        
                        # Update operation status
                        self.dns_operation_repo.update_operation_status(
                            operation.id,
                            status="failed",
                            api_response=response_data,
                            error_message=error_msg
                        )
                        
                        logger.error(f"Failed to create DNS record {record_type} {name}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "cloudflare_response": response_data
                        }
                        
        except Exception as e:
            # Update operation status
            self.dns_operation_repo.update_operation_status(
                operation.id,
                status="failed",
                error_message=str(e)
            )
            
            logger.error(f"Exception creating DNS record {record_type} {name}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def update_dns_record(self, zone_id: str, record_id: str, 
                               updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a DNS record in Cloudflare zone"""
        start_time = datetime.now()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    f"{self.base_url}/zones/{zone_id}/dns_records/{record_id}",
                    headers=self.headers,
                    json=updates
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/zones/{zone_id}/dns_records/{record_id}",
                        method="PATCH",
                        status=response.status,
                        request_data=updates,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("success"):
                        record_data = response_data["result"]
                        logger.info(f"Successfully updated DNS record {record_id} in zone {zone_id}")
                        
                        return {
                            "success": True,
                            "record_id": record_data["id"],
                            "cloudflare_data": record_data
                        }
                    else:
                        error_msg = response_data.get("errors", [{"message": "Unknown error"}])[0]["message"]
                        logger.error(f"Failed to update DNS record {record_id}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "cloudflare_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception updating DNS record {record_id}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """Delete a DNS record from Cloudflare zone"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/zones/{zone_id}/dns_records/{record_id}",
                    headers=self.headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get("success"):
                        logger.info(f"Successfully deleted DNS record {record_id} from zone {zone_id}")
                        return True
                    else:
                        error_msg = response_data.get("errors", [{"message": "Unknown error"}])[0]["message"]
                        logger.error(f"Failed to delete DNS record {record_id}: {error_msg}")
                        return False
                        
        except Exception as e:
            logger.error(f"Exception deleting DNS record {record_id}: {str(e)}")
            return False
    
    async def list_dns_records(self, zone_id: str, record_type: str = None) -> List[Dict[str, Any]]:
        """List DNS records in a Cloudflare zone"""
        try:
            url = f"{self.base_url}/zones/{zone_id}/dns_records"
            params = {}
            
            if record_type:
                params["type"] = record_type
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get("success"):
                        records = response_data["result"]
                        logger.info(f"Retrieved {len(records)} DNS records from zone {zone_id}")
                        return records
                    else:
                        logger.error(f"Failed to list DNS records for zone {zone_id}: {response_data}")
                        return []
                        
        except Exception as e:
            logger.error(f"Exception listing DNS records for zone {zone_id}: {str(e)}")
            return []
    
    async def _log_api_usage(self, endpoint: str, method: str, status: int,
                            request_data: Dict[str, Any] = None,
                            response_data: Dict[str, Any] = None,
                            response_time_ms: int = None):
        """Log API usage for monitoring"""
        try:
            self.api_usage_repo.log_api_call(
                service_name="cloudflare",
                api_endpoint=endpoint,
                http_method=method,
                response_status=status,
                request_data=request_data,
                response_data=response_data,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.error(f"Failed to log API usage: {str(e)}")
    
    async def get_zone_info(self, zone_id: str) -> Dict[str, Any]:
        """Get complete zone information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/zones/{zone_id}",
                    headers=self.headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get("success"):
                        return response_data["result"]
                    else:
                        logger.error(f"Failed to get zone info for {zone_id}: {response_data}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Exception getting zone info for {zone_id}: {str(e)}")
            return {}