#!/usr/bin/env python3
"""
Trustee Service Manager for Country-Specific Domain Registration
Handles OpenProvider trustee services with 2x domain cost pricing
"""

import logging
from typing import Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class TrusteeRequirement(Enum):
    NONE = "none"
    RECOMMENDED = "recommended"
    REQUIRED = "required"
    BLOCKED = "blocked"

class TrusteeServiceManager:
    """Manages trustee services for country-specific TLD registrations"""
    
    def __init__(self):

        self.base_trustee_costs = {
                ".ca": 20,   # Canada
                ".au": 25,   # Australia
                ".fr": 15,   # France
                ".eu": 15,   # European Union
                ".de": 10,   # Germany (optional)
                ".dk": 12,   # Denmark
                ".br": 18,   # Brazil (premium option)
                ".com.br": 0,
                ".hu": 0,
                ".jp": 0,
                ".kr": 0,
                ".sg": 0,
                ".com.sg": 0,
            }
        # Country TLD requirements with trustee information
        self.tld_trustee_config = {
            # European TLDs
            ".de": {
                "country": "Germany", 
                "trustee_requirement": TrusteeRequirement.NONE,
                "reasons": ["Optional trustee for legal document service only", "No local presence required since May 2018"],
                "special_requirements": ["A record setup before registration", "15-second propagation wait", "DNS validation by DENIC before registration"],
                "registration_complexity": "simple",
                "notes": "Trustee service only needed if non-German registrant wants legal document service coverage"
            },
            ".fr": {
                "country": "France",
                "trustee_requirement": TrusteeRequirement.REQUIRED,
                "reasons": ["EU presence required", "AFNIC compliance"],
                "special_requirements": ["Email verification mandatory"],
                "registration_complexity": "high"
            },
            ".it": {
                "country": "Italy", 
                "trustee_requirement": TrusteeRequirement.BLOCKED,
                "reasons": ["Requires personal documents", "EEA residency/citizenship"],
                "special_requirements": ["Passport/ID required", "Fiscal code required"],
                "registration_complexity": "blocked"
            },
            ".eu": {
                "country": "European Union",
                "trustee_requirement": TrusteeRequirement.REQUIRED,
                "reasons": ["EU residency required", "Business registration"],
                "special_requirements": ["EU presence verification"],
                "registration_complexity": "high"
            },
            
            # Americas TLDs
            ".ca": {
                "country": "Canada",
                "trustee_requirement": TrusteeRequirement.REQUIRED,
                "reasons": ["Canadian Presence Requirements (CPR)", "Business registration"],
                "special_requirements": ["Canadian citizen/resident required"],
                "registration_complexity": "high"
            },
            ".br": {
                "country": "Brazil",
                "trustee_requirement": TrusteeRequirement.REQUIRED,
                "reasons": ["Brazilian CPF/CNPJ required", "Local address"],
                "special_requirements": ["Brazilian tax number required"],
                "registration_complexity": "high"
            },
            
            # Asia-Pacific TLDs
            ".au": {
                "country": "Australia",
                "trustee_requirement": TrusteeRequirement.REQUIRED,
                "reasons": ["Australian presence required", "ABN for businesses"],
                "special_requirements": ["Australian Business Number", "Residency proof"],
                "registration_complexity": "high"
            },
            
            # Nordic TLDs
            ".dk": {
                "country": "Denmark",
                "trustee_requirement": TrusteeRequirement.RECOMMENDED,
                "reasons": ["2025 compliance updates", "Terms acceptance"],
                "special_requirements": ["dk_acceptance=1 parameter required"],
                "registration_complexity": "medium"
            }
        }
        
        # Safe TLDs that don't require trustees
        self.safe_tlds = {
            ".com", ".net", ".org", ".info", ".biz", ".name", 
            ".uk", ".co.uk", ".nl", ".ch", ".li", ".be", ".de",
            ".io", ".ly", ".me", ".tv", ".cc", ".ws", ".sx"
        }

    def get_tld_from_domain(self, domain_name: str) -> str:
        """Extract TLD from domain name"""
        parts = domain_name.lower().split('.')
        if len(parts) >= 2:
            # Handle .co.uk style domains
            if len(parts) >= 3 and parts[-2] == 'co' and parts[-1] == 'uk':
                return '.co.uk'
            else:
                return '.' + parts[-1]
        return ''

    def check_trustee_requirement(self, domain_name: str) -> Dict:
        """Check if domain requires trustee service"""
        tld = self.get_tld_from_domain(domain_name)
        
        # Check if TLD has specific configuration first (even if in safe_tlds)
        if tld in self.tld_trustee_config:
            config = self.tld_trustee_config[tld]
            requires_trustee = config["trustee_requirement"] in [
                TrusteeRequirement.REQUIRED, 
                TrusteeRequirement.RECOMMENDED
            ]
            can_register = config["trustee_requirement"] != TrusteeRequirement.BLOCKED
            
            return {
                "requires_trustee": requires_trustee,
                "trustee_requirement": config["trustee_requirement"],
                "country": config["country"],
                "reasons": config["reasons"],
                "special_requirements": config["special_requirements"],
                "registration_complexity": config["registration_complexity"],
                "can_register": can_register,
                "tld": tld
            }
        
        if tld in self.safe_tlds:
            return {
                "requires_trustee": False,
                "trustee_requirement": TrusteeRequirement.NONE,
                "country": "International",
                "reasons": [],
                "special_requirements": [],
                "registration_complexity": "simple",
                "can_register": True
            }
        
        # Unknown TLD - treat as potentially risky
        return {
            "requires_trustee": False,
            "trustee_requirement": TrusteeRequirement.NONE,
            "country": "Unknown",
            "reasons": ["TLD requirements not verified"],
            "special_requirements": ["Manual verification may be required"],
            "registration_complexity": "unknown",
            "can_register": True,
            "warning": "TLD requirements not fully verified"
        }

    def calculate_trustee_pricing(self, base_domain_price: float, domain_name: str) -> Tuple[float, Dict]:
        """Calculate total cost including trustee service (2x domain cost)"""
        trustee_info = self.check_trustee_requirement(domain_name)
        
        if not trustee_info["requires_trustee"]:
            return base_domain_price, {
                "total_cost": base_domain_price,
                "domain_cost": base_domain_price,
                "trustee_cost": 0.0,
                "requires_trustee": False,
                "trustee_required": False,
                "tld": self.get_tld_from_domain(domain_name).replace('.', ''),
                "risk_level": "LOW",
                "breakdown": f"Domain only: ${base_domain_price:.2f}"
            }
        
        tld = self.get_tld_from_domain(domain_name)
        base_trustee_cost = self.base_trustee_costs.get(tld, 20)
        trustee_cost = base_domain_price * 2.0
        total_cost = base_domain_price + trustee_cost
        
        # Determine risk level based on complexity
        risk_level = {
            "simple": "LOW",
            "medium": "MEDIUM", 
            "high": "HIGH",
            "blocked": "HIGH"
        }.get(trustee_info.get("registration_complexity", "medium"), "MEDIUM")
        
        return total_cost, {
            "total_cost": total_cost,
            "domain_cost": base_domain_price,
            "trustee_cost": trustee_cost,
            "trustee_fee": trustee_cost,
            "requires_trustee": True,
            "trustee_required": True,
            "trustee_multiplier": 2.0,
            "tld": self.get_tld_from_domain(domain_name).replace('.', ''),
            "risk_level": risk_level,
            "trustee_name": f"{trustee_info['country']} Trustee Service",
            "registration_success_rate": {"LOW": 98, "MEDIUM": 95, "HIGH": 90}.get(risk_level, 95),
            "documents_required": "Handled by trustee service",
            "breakdown": f"Domain: ${base_domain_price:.2f} + Trustee: ${trustee_cost:.2f} = ${total_cost:.2f}",
            "country": trustee_info["country"],
            "reasons": trustee_info["reasons"]
        }

    def get_registration_guidance(self, domain_name: str) -> Dict:
        """Get comprehensive registration guidance for domain"""
        trustee_info = self.check_trustee_requirement(domain_name)
        tld = self.get_tld_from_domain(domain_name)
        
        if not trustee_info["can_register"]:
            return {
                "can_register": False,
                "guidance_type": "blocked",
                "title": f"⚠️ {tld.upper()} Registration Blocked",
                "message": f"Unfortunately, {trustee_info['country']} domains require personal documents and residency proof that cannot be fulfilled through trustee services.",
                "reasons": trustee_info["reasons"],
                "alternative_suggestion": "Consider similar domains with .com, .net, or other international extensions."
            }
        
        if trustee_info["requires_trustee"]:
            return {
                "can_register": True,
                "guidance_type": "trustee_required",
                "title": f"🛡️ {tld.upper()} Trustee Service Required",
                "message": f"This {trustee_info['country']} domain requires our trustee service for offshore registration. We'll handle all local compliance requirements.",
                "reasons": trustee_info["reasons"],
                "special_requirements": trustee_info["special_requirements"],
                "trustee_benefits": [
                    "Complete privacy protection",
                    "Local compliance handling", 
                    "No personal documents required",
                    "Full domain control maintained"
                ]
            }
        
        return {
            "can_register": True,
            "guidance_type": "standard",
            "title": f"✅ {tld.upper()} Standard Registration",
            "message": f"This domain can be registered with standard offshore privacy protection.",
            "reasons": ["No special country requirements"],
            "benefits": [
                "Standard privacy protection",
                "Immediate registration",
                "Full control and ownership"
            ]
        }

    def format_trustee_explanation(self, domain_name: str, base_price: float) -> str:
        """Format user-friendly trustee service explanation"""
        trustee_info = self.check_trustee_requirement(domain_name)
        tld = self.get_tld_from_domain(domain_name)
        
        if not trustee_info["can_register"]:
            return (
                f"❌ **{tld.upper()} Registration Not Available**\n\n"
                f"🏴‍☠️ **{trustee_info['country']} Domain Restrictions**\n\n"
                f"Unfortunately, {trustee_info['country']} domains require:\n"
                + "\n".join([f"• {req}" for req in trustee_info["reasons"]]) + "\n\n"
                f"These requirements cannot be fulfilled through our offshore trustee services.\n\n"
                f"**Alternative:** Consider {domain_name.replace(tld, '.com')} or other international extensions."
            )
        
        if trustee_info["requires_trustee"]:
            total_cost, pricing = self.calculate_trustee_pricing(base_price, domain_name)
            
            return (
                f"🛡️ **{tld.upper()} Trustee Service Required**\n\n"
                f"🏴‍☠️ **{trustee_info['country']} Domain Registration**\n\n"
                f"**Why Trustee Service is Needed:**\n"
                + "\n".join([f"• {reason}" for reason in trustee_info["reasons"]]) + "\n\n"
                f"**What Our Trustee Service Provides:**\n"
                f"• Complete privacy protection\n"
                f"• Local compliance handling\n"
                f"• No personal documents required\n"
                f"• Full domain control maintained\n\n"
                f"**Pricing Breakdown:**\n"
                f"• Domain Registration: ${pricing['domain_cost']:.2f}\n"
                f"• Trustee Service (2x): ${pricing['trustee_cost']:.2f}\n"
                f"• **Total Cost: ${pricing['total_cost']:.2f}**\n\n"
                f"The trustee service ensures your {trustee_info['country']} domain is properly registered while maintaining complete anonymity."
            )
        
        return (
            f"✅ **{tld.upper()} Standard Registration**\n\n"
            f"🏴‍☠️ **International Domain**\n\n"
            f"This domain can be registered with our standard offshore privacy protection.\n\n"
            f"**Features Included:**\n"
            f"• Complete WHOIS privacy\n"
            f"• Anonymous registration\n"
            f"• Immediate activation\n"
            f"• Full domain control\n\n"
            f"**Total Cost: ${base_price:.2f}**"
        )