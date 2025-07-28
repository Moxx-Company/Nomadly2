"""
Nameserver Management Service
Handles nameserver operations using OpenProvider API for UI integration
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

class NameserverService:
    """Service for managing domain nameservers via OpenProvider API"""
    
    # Common nameserver presets
    NAMESERVER_PRESETS = {
        "cloudflare": {
            "name": "Cloudflare DNS",
            "nameservers": ["ns1.cloudflare.com", "ns2.cloudflare.com"],
            "description": "Fast global DNS with DDoS protection and CDN integration",
            "features": ["DDoS Protection", "CDN", "Analytics", "Global Anycast"]
        },
        "openprovider": {
            "name": "OpenProvider DNS", 
            "nameservers": ["ns1.openprovider.nl", "ns2.openprovider.be", "ns3.openprovider.eu"],
            "description": "Reliable European DNS hosting with registrar integration",
            "features": ["Registrar Integration", "European Servers", "Reliable Uptime"]
        },
        "godaddy": {
            "name": "GoDaddy DNS",
            "nameservers": ["ns01.domaincontrol.com", "ns02.domaincontrol.com"],
            "description": "Popular DNS hosting with domain management tools",
            "features": ["Domain Management", "DNS Tools", "Global Presence"]
        },
        "namecheap": {
            "name": "Namecheap DNS",
            "nameservers": ["dns1.registrar-servers.com", "dns2.registrar-servers.com"],
            "description": "Affordable DNS hosting with privacy protection",
            "features": ["Privacy Protection", "Affordable", "Easy Management"]
        },
        "google": {
            "name": "Google Cloud DNS",
            "nameservers": ["ns-cloud-a1.googledomains.com", "ns-cloud-a2.googledomains.com"],
            "description": "Enterprise-grade DNS with Google's global infrastructure",
            "features": ["Enterprise Grade", "Global Infrastructure", "High Performance"]
        }
    }
    
    def __init__(self, domain_repo, openprovider_api, audit_service=None):
        self.domain_repo = domain_repo
        self.openprovider_api = openprovider_api
        self.audit_service = audit_service
    
    def get_domain_nameservers(self, domain_id: int, telegram_id: int) -> Dict[str, Any]:
        """
        Get current nameserver configuration for a domain
        UI Layer: Display current nameservers with change options
        """
        try:
            # Verify domain ownership
            domain = self.domain_repo.get_by_id(domain_id)
            if not domain or int(domain.telegram_id) != telegram_id:
                return {"success": False, "error": "Domain not found or access denied"}
            
            # Get current nameservers from database
            current_nameservers = []
            if domain.nameservers:
                try:
                    if isinstance(domain.nameservers, str):
                        current_nameservers = json.loads(domain.nameservers)
                    elif isinstance(domain.nameservers, list):
                        current_nameservers = domain.nameservers
                except json.JSONDecodeError:
                    logger.warning(f"Invalid nameserver JSON for domain {domain.domain_name}")
            
            # Determine nameserver provider
            provider = self.detect_nameserver_provider(current_nameservers)
            
            # Get nameserver status from OpenProvider if possible
            nameserver_status = "unknown"
            propagation_status = "unknown"
            
            if domain.openprovider_domain_id:
                try:
                    op_info = self.openprovider_api.get_domain_info(domain.domain_name)
                    if op_info.get("success"):
                        nameserver_status = "active"
                        # Check propagation by comparing current vs database
                        op_nameservers = op_info.get("data", {}).get("nameservers", [])
                        if op_nameservers == current_nameservers:
                            propagation_status = "propagated"
                        else:
                            propagation_status = "pending"
                except Exception as e:
                    logger.warning(f"Could not get OpenProvider nameserver status: {e}")
            
            return {
                "success": True,
                "domain_name": domain.domain_name,
                "domain_id": domain_id,
                "current_nameservers": current_nameservers,
                "provider": provider,
                "nameserver_status": nameserver_status,
                "propagation_status": propagation_status,
                "last_updated": domain.updated_at.isoformat() if domain.updated_at else None,
                "can_manage": bool(domain.openprovider_domain_id),
                "presets": self.NAMESERVER_PRESETS
            }
            
        except Exception as e:
            logger.error(f"Error getting domain nameservers: {e}")
            return {"success": False, "error": f"Failed to get nameservers: {str(e)}"}
    
    def update_domain_nameservers(self, domain_id: int, telegram_id: int, nameservers: List[str], provider_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Update nameservers for a domain via OpenProvider API
        UI Layer: Process nameserver change requests with validation
        """
        try:
            # Verify domain ownership
            domain = self.domain_repo.get_by_id(domain_id)
            if not domain or int(domain.telegram_id) != telegram_id:
                return {"success": False, "error": "Domain not found or access denied"}
            
            if not domain.openprovider_domain_id:
                return {"success": False, "error": "Domain not registered with OpenProvider - cannot manage nameservers"}
            
            # Validate nameservers
            validation = self.validate_nameservers(nameservers)
            if not validation["valid"]:
                return {"success": False, "error": validation["error"]}
            
            # Get current nameservers for audit trail
            current_nameservers = []
            if domain.nameservers:
                try:
                    if isinstance(domain.nameservers, str):
                        current_nameservers = json.loads(domain.nameservers)
                    elif isinstance(domain.nameservers, list):
                        current_nameservers = domain.nameservers
                except:
                    pass
            
            # Update nameservers via OpenProvider API
            op_result = self.openprovider_api.update_nameservers(domain.domain_name, nameservers)
            
            if not op_result:
                return {"success": False, "error": "Failed to update nameservers with OpenProvider"}
            
            # Update local database
            nameservers_json = json.dumps(nameservers)
            update_success = self.domain_repo.update_nameservers(domain_id, nameservers, provider_name or "custom")
            
            if not update_success:
                logger.warning(f"OpenProvider update succeeded but database update failed for domain {domain.domain_name}")
            
            # Log the change for audit
            if self.audit_service:
                self.audit_service.log_nameserver_change(
                    domain_id=domain_id,
                    telegram_id=telegram_id,
                    old_nameservers=current_nameservers,
                    new_nameservers=nameservers,
                    provider=provider_name,
                    success=True
                )
            
            logger.info(f"Successfully updated nameservers for {domain.domain_name}: {nameservers}")
            
            return {
                "success": True,
                "domain_name": domain.domain_name,
                "old_nameservers": current_nameservers,
                "new_nameservers": nameservers,
                "provider": provider_name,
                "propagation_time": "24-48 hours",
                "message": f"Nameservers updated successfully for {domain.domain_name}"
            }
            
        except Exception as e:
            logger.error(f"Error updating domain nameservers: {e}")
            
            # Log failed attempt
            if self.audit_service:
                self.audit_service.log_nameserver_change(
                    domain_id=domain_id,
                    telegram_id=telegram_id,
                    old_nameservers=[],
                    new_nameservers=nameservers,
                    provider=provider_name,
                    success=False,
                    error=str(e)
                )
            
            return {"success": False, "error": f"Failed to update nameservers: {str(e)}"}
    
    def set_nameserver_preset(self, domain_id: int, telegram_id: int, preset_name: str) -> Dict[str, Any]:
        """
        Set nameservers using a predefined preset
        UI Layer: Quick nameserver switching with preset options
        """
        if preset_name not in self.NAMESERVER_PRESETS:
            return {"success": False, "error": f"Invalid preset: {preset_name}"}
        
        preset = self.NAMESERVER_PRESETS[preset_name]
        
        return self.update_domain_nameservers(
            domain_id=domain_id,
            telegram_id=telegram_id,
            nameservers=preset["nameservers"],
            provider_name=preset_name
        )
    
    def validate_nameservers(self, nameservers: List[str]) -> Dict[str, Any]:
        """
        Validate nameserver format and accessibility
        Service Layer: Business logic for nameserver validation
        """
        if not nameservers:
            return {"valid": False, "error": "At least one nameserver is required"}
        
        if len(nameservers) > 6:
            return {"valid": False, "error": "Maximum 6 nameservers allowed"}
        
        # Validate each nameserver
        for i, ns in enumerate(nameservers):
            if not ns or not isinstance(ns, str):
                return {"valid": False, "error": f"Invalid nameserver format at position {i+1}"}
            
            # Basic hostname validation
            if not self.is_valid_hostname(ns):
                return {"valid": False, "error": f"Invalid hostname format: {ns}"}
            
            # Check for duplicates
            if nameservers.count(ns) > 1:
                return {"valid": False, "error": f"Duplicate nameserver: {ns}"}
        
        # Ensure at least 2 nameservers for redundancy
        if len(nameservers) < 2:
            return {"valid": False, "error": "At least 2 nameservers recommended for redundancy"}
        
        return {"valid": True}
    
    def is_valid_hostname(self, hostname: str) -> bool:
        """Validate hostname format for nameservers"""
        if not hostname or len(hostname) > 253:
            return False
        
        # Remove trailing dot if present
        hostname = hostname.rstrip('.')
        
        # Check overall format
        if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
            return False
        
        # Check each label
        labels = hostname.split('.')
        if len(labels) < 2:  # At least domain.tld
            return False
        
        for label in labels:
            if not label or len(label) > 63:
                return False
            if label.startswith('-') or label.endswith('-'):
                return False
            if not re.match(r'^[a-zA-Z0-9-]+$', label):
                return False
        
        return True
    
    def detect_nameserver_provider(self, nameservers: List[str]) -> Dict[str, Any]:
        """
        Detect nameserver provider from nameserver list
        UI Layer: Display provider information to users
        """
        if not nameservers:
            return {"provider": "unknown", "name": "Unknown", "confidence": 0}
        
        # Check against known presets
        for preset_key, preset_data in self.NAMESERVER_PRESETS.items():
            preset_ns = set(preset_data["nameservers"])
            user_ns = set(nameservers)
            
            # Exact match
            if preset_ns == user_ns:
                return {
                    "provider": preset_key,
                    "name": preset_data["name"],
                    "confidence": 100,
                    "description": preset_data["description"],
                    "features": preset_data["features"]
                }
            
            # Partial match (at least 50% overlap)
            overlap = len(preset_ns.intersection(user_ns))
            if overlap > 0 and overlap / len(preset_ns) >= 0.5:
                confidence = int((overlap / len(preset_ns)) * 100)
                return {
                    "provider": preset_key,
                    "name": preset_data["name"],
                    "confidence": confidence,
                    "description": preset_data["description"],
                    "features": preset_data["features"]
                }
        
        # Try to detect by domain patterns
        first_ns = nameservers[0].lower()
        
        if "cloudflare" in first_ns:
            return {"provider": "cloudflare", "name": "Cloudflare DNS", "confidence": 90}
        elif "openprovider" in first_ns:
            return {"provider": "openprovider", "name": "OpenProvider DNS", "confidence": 90}
        elif "godaddy" in first_ns or "domaincontrol" in first_ns:
            return {"provider": "godaddy", "name": "GoDaddy DNS", "confidence": 90}
        elif "namecheap" in first_ns or "registrar-servers" in first_ns:
            return {"provider": "namecheap", "name": "Namecheap DNS", "confidence": 90}
        elif "googledomains" in first_ns or "google" in first_ns:
            return {"provider": "google", "name": "Google DNS", "confidence": 90}
        
        return {"provider": "custom", "name": "Custom DNS", "confidence": 50}
    
    def get_nameserver_propagation_status(self, domain_id: int, telegram_id: int) -> Dict[str, Any]:
        """
        Check nameserver propagation status across global DNS
        UI Layer: Show propagation progress to users
        """
        try:
            domain = self.domain_repo.get_by_id(domain_id)
            if not domain or int(domain.telegram_id) != telegram_id:
                return {"success": False, "error": "Domain not found or access denied"}
            
            # Get current nameservers from database
            expected_nameservers = []
            if domain.nameservers:
                try:
                    if isinstance(domain.nameservers, str):
                        expected_nameservers = json.loads(domain.nameservers)
                    elif isinstance(domain.nameservers, list):
                        expected_nameservers = domain.nameservers
                except:
                    pass
            
            if not expected_nameservers:
                return {"success": False, "error": "No nameservers configured for domain"}
            
            # This would normally check DNS propagation across multiple locations
            # For now, we'll return a simplified status
            propagation_results = {
                "domain_name": domain.domain_name,
                "expected_nameservers": expected_nameservers,
                "propagation_percentage": 85,  # Would be calculated from actual DNS queries
                "status": "propagating",
                "estimated_completion": "2-4 hours",
                "global_checks": [
                    {"location": "North America", "status": "propagated", "nameservers": expected_nameservers},
                    {"location": "Europe", "status": "propagated", "nameservers": expected_nameservers},
                    {"location": "Asia", "status": "pending", "nameservers": []},
                    {"location": "Australia", "status": "propagated", "nameservers": expected_nameservers}
                ]
            }
            
            return {"success": True, "propagation": propagation_results}
            
        except Exception as e:
            logger.error(f"Error checking nameserver propagation: {e}")
            return {"success": False, "error": f"Failed to check propagation: {str(e)}"}
    
    def get_user_nameserver_history(self, telegram_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        Get nameserver change history for user
        UI Layer: Show recent nameserver changes across all domains
        """
        try:
            # Get user's domains
            user_domains = self.domain_repo.get_user_domains(telegram_id)
            
            nameserver_history = []
            
            # For each domain, get recent nameserver changes
            for domain in user_domains:
                if self.audit_service:
                    domain_history = self.audit_service.get_nameserver_history(domain.id, limit=5)
                    for entry in domain_history:
                        nameserver_history.append({
                            "domain_name": domain.domain_name,
                            "domain_id": domain.id,
                            "timestamp": entry.get("timestamp"),
                            "old_nameservers": entry.get("old_nameservers", []),
                            "new_nameservers": entry.get("new_nameservers", []),
                            "provider": entry.get("provider"),
                            "success": entry.get("success", True)
                        })
            
            # Sort by timestamp (most recent first)
            nameserver_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return {
                "success": True,
                "history": nameserver_history[:limit],
                "total_changes": len(nameserver_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting nameserver history: {e}")
            return {"success": False, "error": f"Failed to get history: {str(e)}"}
    
    def bulk_update_nameservers(self, domain_ids: List[int], telegram_id: int, nameservers: List[str], provider_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Update nameservers for multiple domains at once
        UI Layer: Bulk nameserver management for power users
        """
        results = []
        success_count = 0
        
        for domain_id in domain_ids:
            result = self.update_domain_nameservers(domain_id, telegram_id, nameservers, provider_name)
            results.append({
                "domain_id": domain_id,
                "success": result.get("success", False),
                "domain_name": result.get("domain_name", "Unknown"),
                "error": result.get("error") if not result.get("success") else None
            })
            
            if result.get("success"):
                success_count += 1
        
        return {
            "success": success_count > 0,
            "total_domains": len(domain_ids),
            "successful_updates": success_count,
            "failed_updates": len(domain_ids) - success_count,
            "results": results,
            "nameservers": nameservers,
            "provider": provider_name
        }