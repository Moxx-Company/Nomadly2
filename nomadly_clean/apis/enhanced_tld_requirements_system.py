#!/usr/bin/env python3
"""
Enhanced TLD Requirements System - 2025 Edition
Based on actual OpenProvider API documentation and NIS2 Directive compliance
Integrates with custom nameserver workflow and provides accurate country TLD validation
"""

import os
import json
import requests
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class TLDRiskLevel(Enum):
    NONE = "NONE"
    LOW = "LOW"  
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class TLDAction(Enum):
    ALLOW = "ALLOW"
    REQUIRE_TRUSTEE = "REQUIRE_TRUSTEE"
    REQUIRE_ADDITIONAL_DATA = "REQUIRE_ADDITIONAL_DATA"
    BLOCK_WITH_MESSAGE = "BLOCK_WITH_MESSAGE"


@dataclass
class TLDRequirement:
    """OpenProvider TLD additional data requirement"""
    name: str
    description: str
    required: bool
    field_type: str  # text, select, checkbox, etc.
    validation_pattern: Optional[str] = None
    possible_values: Optional[List[str]] = None


@dataclass
class TLDInfo:
    """Complete TLD information with 2025 requirements"""
    tld: str
    country: Optional[str]
    risk_level: TLDRiskLevel
    recommended_action: TLDAction
    requirements: List[str]
    additional_data_domain: List[TLDRequirement]
    additional_data_customer: List[TLDRequirement]
    nis2_affected: bool
    email_verification_required: bool
    trustee_service_available: bool
    special_notes: List[str]


class EnhancedTLDRequirementsSystem:
    """Enhanced TLD requirements system with real OpenProvider API integration"""
    
    def __init__(self):
        self.api_base = "https://api.openprovider.eu"
        self.token = None
        
        # 2025 NIS2 Directive affected TLDs
        self.nis2_affected_tlds = {
            ".at", ".co.at", ".or.at", ".dk", ".fi", ".fr", ".pm", ".re", 
            ".tf", ".wf", ".yt", ".de", ".it", ".nl", ".amsterdam", ".pl"
        }
        
        # Initialize known high-risk TLDs based on OpenProvider documentation
        self.high_risk_tlds = {
            ".it": {
                "country": "Italy",
                "risk_level": TLDRiskLevel.VERY_HIGH,
                "action": TLDAction.BLOCK_WITH_MESSAGE,
                "requirements": [
                    "EEA residency/citizenship required",
                    "Valid fiscal code (SSN) required",
                    "Passport/ID number required",
                    "Email confirmation within 14 days"
                ],
                "trustee_available": False,
                "notes": ["Requires physical presence in EEA", "Documentation verification mandatory"]
            },
            ".ca": {
                "country": "Canada", 
                "risk_level": TLDRiskLevel.HIGH,
                "action": TLDAction.REQUIRE_TRUSTEE,
                "requirements": [
                    "Canadian Presence Requirements (CPR)",
                    "Canadian citizenship/residency or business registration"
                ],
                "trustee_available": True,
                "notes": ["OpenProvider trustee service available"]
            },
            ".au": {
                "country": "Australia",
                "risk_level": TLDRiskLevel.HIGH,
                "action": TLDAction.REQUIRE_TRUSTEE,
                "requirements": [
                    "Australian presence required",
                    "ABN (Australian Business Number) for businesses",
                    "Australian citizenship/residency proof"
                ],
                "trustee_available": True,
                "notes": ["OpenProvider trustee service available"]
            },
            ".br": {
                "country": "Brazil",
                "risk_level": TLDRiskLevel.HIGH,
                "action": TLDAction.REQUIRE_TRUSTEE,
                "requirements": [
                    "Brazilian CPF (individuals) or CNPJ (companies)",
                    "Brazilian address required"
                ],
                "trustee_available": True,
                "notes": ["OpenProvider trustee service available"]
            },
            ".dk": {
                "country": "Denmark",
                "risk_level": TLDRiskLevel.MEDIUM,
                "action": TLDAction.REQUIRE_ADDITIONAL_DATA,
                "requirements": [
                    "dk_acceptance parameter required (2025 update)",
                    "Terms and conditions acceptance mandatory"
                ],
                "trustee_available": False,
                "notes": ["New 2025 requirement: dk_acceptance=1 parameter mandatory"]
            },
            ".de": {
                "country": "Germany",
                "risk_level": TLDRiskLevel.MEDIUM,
                "action": TLDAction.REQUIRE_ADDITIONAL_DATA,
                "requirements": [
                    "DENIC abuse contact required",
                    "DNS pre-configuration before registration",
                    "Trustee service for non-German registrants"
                ],
                "trustee_available": True,
                "notes": ["Requires DNS setup before registration", "15-second propagation wait needed"]
            }
        }
        
        # Safe TLDs that work well with custom nameservers
        self.safe_tlds = {
            ".com", ".net", ".org", ".info", ".biz", ".name", ".mobi",
            ".uk", ".co.uk", ".nl", ".ch", ".li", ".be", ".eu",
            ".io", ".ly", ".me", ".tv", ".cc", ".ws", ".sx"
        }
    
    def _authenticate_openprovider(self) -> bool:
        """Authenticate with OpenProvider API"""
        try:
            username = os.getenv("OPENPROVIDER_USERNAME")
            password = os.getenv("OPENPROVIDER_PASSWORD")
            
            if not username or not password:
                logger.warning("OpenProvider credentials not available - using cached requirements")
                return False
            
            url = f"{self.api_base}/v1beta/auth/login"
            data = {"username": username, "password": password}
            
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("data", {}).get("token")
                return True
            
            logger.warning(f"OpenProvider auth failed: {response.status_code}")
            return False
            
        except Exception as e:
            logger.warning(f"OpenProvider auth error: {e}")
            return False
    
    def get_tld_additional_data_requirements(self, tld: str) -> Tuple[List[TLDRequirement], List[TLDRequirement]]:
        """Get additional data requirements from OpenProvider API"""
        try:
            if not self.token and not self._authenticate_openprovider():
                return self._get_cached_requirements(tld)
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Get domain additional data requirements
            domain_url = f"{self.api_base}/v1beta/domains/additional-data"
            domain_params = {"domain.extension": tld.lstrip(".")}
            
            domain_requirements = []
            try:
                domain_response = requests.get(domain_url, headers=headers, params=domain_params, timeout=15)
                if domain_response.status_code == 200:
                    domain_data = domain_response.json().get("data", [])
                    for req in domain_data:
                        domain_requirements.append(TLDRequirement(
                            name=req.get("name", ""),
                            description=req.get("description", ""),
                            required=req.get("required", False),
                            field_type=req.get("type", "text"),
                            possible_values=req.get("values", []) if req.get("values") else None
                        ))
            except Exception as e:
                logger.warning(f"Failed to get domain requirements for {tld}: {e}")
            
            # Get customer additional data requirements
            customer_url = f"{self.api_base}/v1beta/domains/additional-data/customers/"
            customer_params = {"domain.extension": tld.lstrip(".")}
            
            customer_requirements = []
            try:
                customer_response = requests.get(customer_url, headers=headers, params=customer_params, timeout=15)
                if customer_response.status_code == 200:
                    customer_data = customer_response.json().get("data", [])
                    for req in customer_data:
                        customer_requirements.append(TLDRequirement(
                            name=req.get("name", ""),
                            description=req.get("description", ""),
                            required=req.get("required", False),
                            field_type=req.get("type", "text"),
                            possible_values=req.get("values", []) if req.get("values") else None
                        ))
            except Exception as e:
                logger.warning(f"Failed to get customer requirements for {tld}: {e}")
            
            return domain_requirements, customer_requirements
            
        except Exception as e:
            logger.warning(f"Error getting TLD requirements: {e}")
            return self._get_cached_requirements(tld)
    
    def _get_cached_requirements(self, tld: str) -> Tuple[List[TLDRequirement], List[TLDRequirement]]:
        """Get cached requirements when API is not available"""
        domain_reqs = []
        customer_reqs = []
        
        # Special cases based on known requirements
        if tld == ".dk":
            domain_reqs.append(TLDRequirement(
                name="dk_acceptance",
                description="Acceptance of .dk terms and conditions (mandatory since 2025)",
                required=True,
                field_type="checkbox"
            ))
        
        elif tld == ".de":
            domain_reqs.extend([
                TLDRequirement(
                    name="de_accept_trustee_tac",
                    description="Accept trustee terms and conditions for non-German registrants",
                    required=True,
                    field_type="checkbox"
                ),
                TLDRequirement(
                    name="de_abuse_contact",
                    description="German registry abuse contact email",
                    required=True,
                    field_type="text"
                )
            ])
        
        elif tld in [".fr", ".eu"]:
            customer_reqs.append(TLDRequirement(
                name="eu_citizenship",
                description="EU citizenship or residency proof",
                required=True,
                field_type="select",
                possible_values=["individual", "organization"]
            ))
        
        return domain_reqs, customer_reqs
    
    def analyze_tld_for_registration(self, tld: str) -> TLDInfo:
        """Comprehensive TLD analysis for registration decision"""
        try:
            tld_clean = tld.lower()
            if not tld_clean.startswith("."):
                tld_clean = f".{tld_clean}"
            
            # Get additional data requirements from API
            domain_reqs, customer_reqs = self.get_tld_additional_data_requirements(tld_clean)
            
            # Check if it's a known high-risk TLD
            if tld_clean in self.high_risk_tlds:
                info = self.high_risk_tlds[tld_clean]
                return TLDInfo(
                    tld=tld_clean,
                    country=info["country"],
                    risk_level=info["risk_level"],
                    recommended_action=info["action"],
                    requirements=info["requirements"],
                    additional_data_domain=domain_reqs,
                    additional_data_customer=customer_reqs,
                    nis2_affected=tld_clean in self.nis2_affected_tlds,
                    email_verification_required=tld_clean in self.nis2_affected_tlds,
                    trustee_service_available=info["trustee_available"],
                    special_notes=info["notes"]
                )
            
            # Check if it's NIS2 affected (requires enhanced validation)
            elif tld_clean in self.nis2_affected_tlds:
                return TLDInfo(
                    tld=tld_clean,
                    country=self._get_country_from_tld(tld_clean),
                    risk_level=TLDRiskLevel.MEDIUM,
                    recommended_action=TLDAction.REQUIRE_ADDITIONAL_DATA,
                    requirements=[
                        "Enhanced email verification required (NIS2 Directive)",
                        "Accurate contact data validation",
                        "No WHOIS privacy protection for new registrations"
                    ],
                    additional_data_domain=domain_reqs,
                    additional_data_customer=customer_reqs,
                    nis2_affected=True,
                    email_verification_required=True,
                    trustee_service_available=False,
                    special_notes=["Subject to NIS2 Directive requirements"]
                )
            
            # Check if it's a safe TLD
            elif tld_clean in self.safe_tlds:
                return TLDInfo(
                    tld=tld_clean,
                    country=self._get_country_from_tld(tld_clean),
                    risk_level=TLDRiskLevel.NONE,
                    recommended_action=TLDAction.ALLOW,
                    requirements=["Standard registration process"],
                    additional_data_domain=domain_reqs,
                    additional_data_customer=customer_reqs,
                    nis2_affected=False,
                    email_verification_required=False,
                    trustee_service_available=False,
                    special_notes=["Safe for custom nameserver registration"]
                )
            
            # Unknown TLD - check for additional requirements
            else:
                risk_level = TLDRiskLevel.LOW
                action = TLDAction.ALLOW
                requirements = ["Standard registration process"]
                
                # If has additional requirements, increase risk level
                if domain_reqs or customer_reqs:
                    risk_level = TLDRiskLevel.MEDIUM
                    action = TLDAction.REQUIRE_ADDITIONAL_DATA
                    requirements = [f"Additional data required: {len(domain_reqs + customer_reqs)} fields"]
                
                return TLDInfo(
                    tld=tld_clean,
                    country=self._get_country_from_tld(tld_clean),
                    risk_level=risk_level,
                    recommended_action=action,
                    requirements=requirements,
                    additional_data_domain=domain_reqs,
                    additional_data_customer=customer_reqs,
                    nis2_affected=False,
                    email_verification_required=False,
                    trustee_service_available=False,
                    special_notes=["Analysis based on API requirements"]
                )
                
        except Exception as e:
            logger.error(f"Error analyzing TLD {tld}: {e}")
            # Return safe fallback
            return TLDInfo(
                tld=tld,
                country=None,
                risk_level=TLDRiskLevel.LOW,
                recommended_action=TLDAction.ALLOW,
                requirements=["Standard registration - analysis unavailable"],
                additional_data_domain=[],
                additional_data_customer=[],
                nis2_affected=False,
                email_verification_required=False,
                trustee_service_available=False,
                special_notes=["Fallback analysis - API unavailable"]
            )
    
    def _get_country_from_tld(self, tld: str) -> Optional[str]:
        """Get country name from TLD"""
        country_map = {
            ".de": "Germany", ".fr": "France", ".it": "Italy", ".es": "Spain",
            ".nl": "Netherlands", ".be": "Belgium", ".at": "Austria", ".ch": "Switzerland",
            ".uk": "United Kingdom", ".ie": "Ireland", ".pt": "Portugal", ".dk": "Denmark",
            ".se": "Sweden", ".no": "Norway", ".fi": "Finland", ".pl": "Poland",
            ".ca": "Canada", ".au": "Australia", ".br": "Brazil", ".mx": "Mexico",
            ".jp": "Japan", ".kr": "South Korea", ".cn": "China", ".ru": "Russia",
            ".in": "India", ".sg": "Singapore", ".hk": "Hong Kong", ".tw": "Taiwan"
        }
        return country_map.get(tld)
    
    def get_registration_recommendation(self, tld: str, use_custom_nameservers: bool = False) -> Dict[str, Any]:
        """Get registration recommendation based on TLD analysis and nameserver choice"""
        try:
            tld_info = self.analyze_tld_for_registration(tld)
            
            recommendation = {
                "tld": tld_info.tld,
                "country": tld_info.country,
                "can_register": True,
                "risk_level": tld_info.risk_level.value,
                "recommended_action": tld_info.recommended_action.value,
                "requirements": tld_info.requirements,
                "warnings": [],
                "additional_data_needed": len(tld_info.additional_data_domain) + len(tld_info.additional_data_customer) > 0,
                "trustee_service_available": tld_info.trustee_service_available,
                "custom_nameserver_compatible": True,
                "special_notes": tld_info.special_notes
            }
            
            # Add warnings based on risk level and requirements
            if tld_info.risk_level == TLDRiskLevel.VERY_HIGH:
                recommendation["can_register"] = False
                recommendation["warnings"].append(f"Registration not recommended: {', '.join(tld_info.requirements)}")
            
            elif tld_info.risk_level == TLDRiskLevel.HIGH:
                if tld_info.trustee_service_available:
                    recommendation["warnings"].append("Trustee service will be used for compliance")
                else:
                    recommendation["can_register"] = False
                    recommendation["warnings"].append("Registration requires documents we cannot provide")
            
            elif tld_info.nis2_affected:
                recommendation["warnings"].append("Subject to enhanced EU validation requirements (NIS2)")
            
            # Add custom nameserver specific notes
            if use_custom_nameservers:
                if tld_info.tld == ".de":
                    recommendation["warnings"].append("Custom nameservers: DNS pre-configuration required before registration")
                elif tld_info.risk_level in [TLDRiskLevel.HIGH, TLDRiskLevel.VERY_HIGH]:
                    recommendation["warnings"].append("Custom nameservers: May require additional validation time")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error getting registration recommendation: {e}")
            return {
                "tld": tld,
                "can_register": True,
                "risk_level": "UNKNOWN",
                "warnings": ["Analysis unavailable - proceeding with caution"],
                "additional_data_needed": False,
                "trustee_service_available": False,
                "custom_nameserver_compatible": True,
                "special_notes": ["Fallback recommendation"]
            }
    
    def prepare_additional_data_for_registration(self, tld: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare additional_data object for OpenProvider domain registration"""
        try:
            tld_info = self.analyze_tld_for_registration(tld)
            additional_data = {}
            
            # Handle domain-specific additional data
            for req in tld_info.additional_data_domain:
                if req.name == "dk_acceptance" and tld == ".dk":
                    additional_data["dk_acceptance"] = 1
                elif req.name == "de_accept_trustee_tac" and tld == ".de":
                    additional_data["de_accept_trustee_tac"] = 1
                elif req.name == "de_abuse_contact" and tld == ".de":
                    additional_data["de_abuse_contact"] = user_data.get("email", "abuse@nameword.net")
                # Add more specific mappings as needed
            
            # Handle special TLD requirements based on known registry needs
            if tld == ".de":
                additional_data.update({
                    "de_accept_trustee_tac": 1,
                    "de_abuse_contact": user_data.get("email", "abuse@nameword.net")
                })
            
            # Handle customer-specific additional data
            for req in tld_info.additional_data_customer:
                # Map common customer fields
                if "vat" in req.name.lower():
                    additional_data[req.name] = user_data.get("vat_number", "")
                elif "company" in req.name.lower():
                    additional_data[req.name] = user_data.get("company_name", "")
                # Add more mappings as needed
            
            logger.info(f"Prepared additional data for {tld}: {additional_data}")
            return additional_data
            
        except Exception as e:
            logger.error(f"Error preparing additional data: {e}")
            return {}


# Global instance
_enhanced_tld_system = None

def get_enhanced_tld_system() -> EnhancedTLDRequirementsSystem:
    """Get global enhanced TLD system instance"""
    global _enhanced_tld_system
    if _enhanced_tld_system is None:
        _enhanced_tld_system = EnhancedTLDRequirementsSystem()
    return _enhanced_tld_system


if __name__ == "__main__":
    # Test the system
    system = EnhancedTLDRequirementsSystem()
    
    test_tlds = [".com", ".de", ".it", ".ca", ".dk", ".au", ".fr", ".unknown"]
    
    print("🌍 Enhanced TLD Requirements System - 2025 Edition")
    print("=" * 60)
    
    for tld in test_tlds:
        print(f"\n🔍 Analyzing {tld}:")
        recommendation = system.get_registration_recommendation(tld, use_custom_nameservers=True)
        
        print(f"  ✅ Can Register: {recommendation['can_register']}")
        print(f"  🚨 Risk Level: {recommendation['risk_level']}")
        print(f"  📋 Additional Data: {'Yes' if recommendation['additional_data_needed'] else 'No'}")
        print(f"  🛡️ Trustee Available: {'Yes' if recommendation['trustee_service_available'] else 'No'}")
        
        if recommendation['warnings']:
            print(f"  ⚠️  Warnings: {'; '.join(recommendation['warnings'])}")
        
        if recommendation['special_notes']:
            print(f"  📝 Notes: {'; '.join(recommendation['special_notes'])}")
    
    print("\n" + "=" * 60)
    print("✅ Enhanced TLD Requirements System operational")