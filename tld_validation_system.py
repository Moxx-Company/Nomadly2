#!/usr/bin/env python3
"""
TLD-specific validation system to prevent registration failures
"""

class TLDValidator:
    """Validates TLD-specific requirements before domain registration"""
    
    def __init__(self):
        self.tld_requirements = {
            # High-risk TLDs that need special handling
            ".it": {
                "requires_documents": True,
                "risk_level": "HIGH",
                "requirements": [
                    "EEA residency/citizenship required",
                    "Passport/ID number required", 
                    "Fiscal code (SSN) required",
                    "Email confirmation within 14 days"
                ],
                "trustee_available": False,
                "recommended_action": "BLOCK_WITH_MESSAGE"
            },
            ".ca": {
                "requires_documents": True,
                "risk_level": "HIGH", 
                "requirements": [
                    "Canadian Presence Requirements (CPR)",
                    "Canadian citizen/resident required",
                    "Business registration required"
                ],
                "trustee_available": True,
                "recommended_action": "REQUIRE_TRUSTEE"
            },
            ".au": {
                "requires_documents": True,
                "risk_level": "HIGH",
                "requirements": [
                    "Australian presence required",
                    "ABN (Australian Business Number) required",
                    "Business registration verification"
                ],
                "trustee_available": True,
                "recommended_action": "REQUIRE_TRUSTEE"
            },
            ".br": {
                "requires_documents": True,
                "risk_level": "HIGH",
                "requirements": [
                    "Brazilian presence required",
                    "CPF (individual) or CNPJ (company) required",
                    "Government ID verification"
                ],
                "trustee_available": True,
                "recommended_action": "REQUIRE_TRUSTEE"
            },
            ".fr": {
                "requires_documents": True,
                "risk_level": "MEDIUM",
                "requirements": [
                    "EU residency or company required",
                    "Email verification (NIS2 compliance)"
                ],
                "trustee_available": True,
                "recommended_action": "ALLOW_WITH_TRUSTEE"
            },
            ".eu": {
                "requires_documents": True,
                "risk_level": "MEDIUM",
                "requirements": [
                    "EU/EEA residency OR EU citizenship",
                    "Citizenship verification if outside EU"
                ],
                "trustee_available": True,
                "recommended_action": "ALLOW_WITH_TRUSTEE"
            },
            ".es": {
                "requires_documents": False,
                "risk_level": "MEDIUM",
                "requirements": [
                    "EU residency preferred but not mandatory",
                    "Email verification required"
                ],
                "trustee_available": True,
                "recommended_action": "ALLOW_WITH_WARNING"
            },
            ".de": {
                "requires_documents": False,
                "risk_level": "LOW",
                "requirements": [
                    "DNS pre-configuration required",
                    "Trustee service for non-German registrants"
                ],
                "trustee_available": True,
                "recommended_action": "ALLOW_WITH_SPECIAL_DNS",
                "implemented": True
            },
            # Standard TLDs (no restrictions)
            ".uk": {"risk_level": "NONE", "recommended_action": "ALLOW"},
            ".nl": {"risk_level": "NONE", "recommended_action": "ALLOW"},
            ".ch": {"risk_level": "NONE", "recommended_action": "ALLOW"},
            ".com": {"risk_level": "NONE", "recommended_action": "ALLOW"},
            ".net": {"risk_level": "NONE", "recommended_action": "ALLOW"},
            ".org": {"risk_level": "NONE", "recommended_action": "ALLOW"},
            ".io": {"risk_level": "NONE", "recommended_action": "ALLOW"},
            ".sbs": {"risk_level": "NONE", "recommended_action": "ALLOW"}
        }
    
    def validate_tld(self, domain_name: str) -> dict:
        """Validate if a TLD can be registered without issues"""
        
        # Extract TLD from domain name
        tld = "." + domain_name.split(".")[-1]
        
        if tld not in self.tld_requirements:
            # Unknown TLD - allow but warn
            return {
                "allowed": True,
                "risk_level": "UNKNOWN",
                "action": "ALLOW_WITH_WARNING", 
                "message": f"⚠️ {tld} domain registration may have special requirements. Proceeding with standard registration.",
                "requirements": []
            }
        
        tld_info = self.tld_requirements[tld]
        action = tld_info["recommended_action"]
        
        if action == "BLOCK_WITH_MESSAGE":
            return {
                "allowed": False,
                "risk_level": tld_info["risk_level"],
                "action": action,
                "message": f"🚫 {tld} domains require specific documentation that we cannot provide automatically. Requirements: {', '.join(tld_info['requirements'])}",
                "requirements": tld_info["requirements"]
            }
        
        elif action == "REQUIRE_TRUSTEE":
            return {
                "allowed": True,
                "risk_level": tld_info["risk_level"],
                "action": action,
                "message": f"⚠️ {tld} domains require local presence. We'll use trustee services to complete registration. Additional fees may apply.",
                "requirements": tld_info["requirements"],
                "special_handling": "trustee_service"
            }
            
        elif action == "ALLOW_WITH_TRUSTEE":
            return {
                "allowed": True, 
                "risk_level": tld_info["risk_level"],
                "action": action,
                "message": f"✅ {tld} domain registration available with trustee service for compliance.",
                "requirements": tld_info["requirements"],
                "special_handling": "trustee_service"
            }
            
        elif action == "ALLOW_WITH_WARNING":
            return {
                "allowed": True,
                "risk_level": tld_info["risk_level"], 
                "action": action,
                "message": f"⚠️ {tld} domain has some requirements but registration should succeed. {', '.join(tld_info['requirements'])}",
                "requirements": tld_info["requirements"]
            }
            
        elif action == "ALLOW_WITH_SPECIAL_DNS":
            return {
                "allowed": True,
                "risk_level": tld_info["risk_level"],
                "action": action,
                "message": f"✅ {tld} domain registration with enhanced DNS pre-configuration.",
                "requirements": tld_info["requirements"],
                "special_handling": "dns_preconfiguration"
            }
            
        else:  # ALLOW
            return {
                "allowed": True,
                "risk_level": "NONE",
                "action": "ALLOW",
                "message": f"✅ {tld} domain registration available.",
                "requirements": []
            }
    
    def get_blocked_tlds(self) -> list:
        """Get list of TLDs that are blocked"""
        blocked = []
        for tld, info in self.tld_requirements.items():
            if info["recommended_action"] == "BLOCK_WITH_MESSAGE":
                blocked.append(tld)
        return blocked
    
    def get_trustee_tlds(self) -> list:
        """Get list of TLDs that require trustee services"""
        trustee = []
        for tld, info in self.tld_requirements.items():
            if "TRUSTEE" in info["recommended_action"]:
                trustee.append(tld)
        return trustee

def test_tld_validation():
    """Test the TLD validation system"""
    validator = TLDValidator()
    
    test_domains = [
        "test.com", "test.de", "test.it", "test.ca", 
        "test.au", "test.fr", "test.eu", "test.es",
        "test.unknown"
    ]
    
    print("🧪 TESTING TLD VALIDATION SYSTEM")
    print("=" * 50)
    
    for domain in test_domains:
        result = validator.validate_tld(domain)
        print(f"\n🌍 {domain}")
        print(f"   Allowed: {result['allowed']}")
        print(f"   Risk: {result['risk_level']}")
        print(f"   Action: {result['action']}")
        print(f"   Message: {result['message']}")
        
    print(f"\n📊 SUMMARY:")
    print(f"   Blocked TLDs: {validator.get_blocked_tlds()}")
    print(f"   Trustee TLDs: {validator.get_trustee_tlds()}")

if __name__ == "__main__":
    test_tld_validation()