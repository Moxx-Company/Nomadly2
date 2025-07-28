#!/usr/bin/env python3
"""
Test Enhanced TLD Requirements System Integration
Validates TLD requirements with OpenProvider API and custom nameserver workflow
"""

import asyncio
import logging
from enhanced_tld_requirements_system import get_enhanced_tld_system
from fixed_registration_service import FixedRegistrationService
from apis.production_openprovider import OpenProviderAPI
from nameserver_manager import NameserverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTLDIntegrationTest:
    """Comprehensive test suite for TLD requirements integration"""
    
    def __init__(self):
        self.tld_system = get_enhanced_tld_system()
        self.registration_service = FixedRegistrationService()
        self.nameserver_manager = NameserverManager()
        
    def test_tld_validation_for_custom_nameservers(self):
        """Test TLD validation with custom nameserver scenarios"""
        logger.info("🧪 Testing TLD validation for custom nameserver workflows")
        
        test_scenarios = [
            # Safe TLDs for custom nameservers
            (".com", True, ["ns1.privatehoster.cc", "ns2.privatehoster.cc"]),
            (".net", True, ["ns1.customdns.com", "ns2.customdns.com"]),
            (".org", True, ["dns1.example.org", "dns2.example.org"]),
            
            # European TLDs with NIS2 requirements
            (".de", True, ["ns1.privatehoster.cc", "ns2.privatehoster.cc"]),
            (".fr", True, ["ns1.custom.fr", "ns2.custom.fr"]),
            (".nl", True, ["ns1.hostingprovider.com", "ns2.hostingprovider.com"]),
            
            # High-risk TLDs
            (".it", False, ["ns1.italian-host.com", "ns2.italian-host.com"]),
            (".ca", True, ["ns1.custom.ca", "ns2.custom.ca"]),
            (".au", True, ["ns1.aussiehost.com", "ns2.aussiehost.com"]),
            
            # New 2025 requirements
            (".dk", True, ["ns1.privatehoster.cc", "ns2.privatehoster.cc"]),
        ]
        
        results = []
        for tld, should_allow, custom_ns in test_scenarios:
            recommendation = self.tld_system.get_registration_recommendation(
                tld, use_custom_nameservers=True
            )
            
            # Validate custom nameservers
            ns_valid = self.nameserver_manager._validate_nameservers(custom_ns)
            
            test_result = {
                "tld": tld,
                "expected_allowed": should_allow,
                "actual_allowed": recommendation["can_register"],
                "nameservers_valid": ns_valid,
                "risk_level": recommendation["risk_level"],
                "warnings": recommendation["warnings"],
                "additional_data_needed": recommendation["additional_data_needed"],
                "trustee_available": recommendation["trustee_service_available"]
            }
            
            results.append(test_result)
            
            status = "✅" if recommendation["can_register"] == should_allow else "❌"
            logger.info(f"{status} {tld}: Can register={recommendation['can_register']}, "
                       f"Risk={recommendation['risk_level']}, "
                       f"NS Valid={ns_valid}, Additional Data={recommendation['additional_data_needed']}")
            
            if recommendation["warnings"]:
                logger.info(f"    ⚠️ Warnings: {'; '.join(recommendation['warnings'])}")
        
        # Summary
        passed = sum(1 for r in results if r["actual_allowed"] == r["expected_allowed"])
        total = len(results)
        logger.info(f"🎯 TLD Validation Results: {passed}/{total} tests passed")
        
        return results
    
    def test_nis2_directive_compliance(self):
        """Test NIS2 Directive compliance for EU TLDs"""
        logger.info("🇪🇺 Testing NIS2 Directive compliance")
        
        nis2_tlds = [".at", ".dk", ".fi", ".fr", ".de", ".it", ".nl", ".pl"]
        
        results = []
        for tld in nis2_tlds:
            tld_info = self.tld_system.analyze_tld_for_registration(tld)
            
            result = {
                "tld": tld,
                "nis2_affected": tld_info.nis2_affected,
                "email_verification_required": tld_info.email_verification_required,
                "risk_level": tld_info.risk_level.value,
                "additional_requirements": len(tld_info.additional_data_domain) + len(tld_info.additional_data_customer)
            }
            
            results.append(result)
            
            status = "✅" if tld_info.nis2_affected else "⚠️"
            logger.info(f"{status} {tld}: NIS2={tld_info.nis2_affected}, "
                       f"Email Verification={tld_info.email_verification_required}, "
                       f"Additional Requirements={result['additional_requirements']}")
        
        nis2_compliant = sum(1 for r in results if r["nis2_affected"])
        logger.info(f"🎯 NIS2 Compliance: {nis2_compliant}/{len(nis2_tlds)} TLDs properly flagged")
        
        return results
    
    def test_2025_dk_requirements(self):
        """Test new 2025 .dk domain requirements"""
        logger.info("🇩🇰 Testing 2025 .dk domain requirements")
        
        tld_info = self.tld_system.analyze_tld_for_registration(".dk")
        
        # Check if .dk has the mandatory acceptance parameter
        additional_data = self.tld_system.prepare_additional_data_for_registration(
            ".dk", {"email": "test@example.com"}
        )
        
        has_dk_acceptance = "dk_acceptance" in additional_data
        
        result = {
            "tld": ".dk",
            "has_2025_requirement": has_dk_acceptance,
            "dk_acceptance_value": additional_data.get("dk_acceptance"),
            "risk_level": tld_info.risk_level.value,
            "special_notes": tld_info.special_notes
        }
        
        status = "✅" if has_dk_acceptance and additional_data.get("dk_acceptance") == 1 else "❌"
        logger.info(f"{status} .dk 2025 Requirements: "
                   f"Has dk_acceptance={has_dk_acceptance}, "
                   f"Value={additional_data.get('dk_acceptance')}")
        
        if tld_info.special_notes:
            logger.info(f"    📝 Notes: {'; '.join(tld_info.special_notes)}")
        
        return result
    
    def test_trustee_service_integration(self):
        """Test trustee service availability for high-risk TLDs"""
        logger.info("🛡️ Testing trustee service integration")
        
        trustee_tlds = [(".ca", True), (".au", True), (".br", True), (".de", True), (".it", False)]
        
        results = []
        for tld, should_have_trustee in trustee_tlds:
            recommendation = self.tld_system.get_registration_recommendation(tld)
            
            result = {
                "tld": tld,
                "expected_trustee": should_have_trustee,
                "actual_trustee": recommendation["trustee_service_available"],
                "can_register": recommendation["can_register"],
                "risk_level": recommendation["risk_level"]
            }
            
            results.append(result)
            
            status = "✅" if recommendation["trustee_service_available"] == should_have_trustee else "❌"
            logger.info(f"{status} {tld}: Trustee Available={recommendation['trustee_service_available']}, "
                       f"Can Register={recommendation['can_register']}, "
                       f"Risk={recommendation['risk_level']}")
        
        correct_trustee = sum(1 for r in results if r["actual_trustee"] == r["expected_trustee"])
        logger.info(f"🎯 Trustee Service: {correct_trustee}/{len(results)} correctly configured")
        
        return results
    
    def test_openprovider_additional_data_preparation(self):
        """Test OpenProvider additional_data preparation"""
        logger.info("📊 Testing OpenProvider additional_data preparation")
        
        test_cases = [
            (".de", {"email": "test@example.com"}, ["de_accept_trustee_tac", "de_abuse_contact"]),
            (".dk", {"email": "test@example.com"}, ["dk_acceptance"]),
            (".ca", {"email": "test@example.com"}, []),  # Handled by trustee service
            (".com", {"email": "test@example.com"}, []),  # No additional data needed
        ]
        
        results = []
        for tld, user_data, expected_fields in test_cases:
            additional_data = self.tld_system.prepare_additional_data_for_registration(tld, user_data)
            
            result = {
                "tld": tld,
                "additional_data": additional_data,
                "expected_fields": expected_fields,
                "has_expected_fields": all(field in additional_data for field in expected_fields),
                "extra_fields": [field for field in additional_data if field not in expected_fields]
            }
            
            results.append(result)
            
            status = "✅" if result["has_expected_fields"] else "❌"
            logger.info(f"{status} {tld}: Additional Data Fields={list(additional_data.keys())}")
            
            if additional_data:
                for field, value in additional_data.items():
                    logger.info(f"    {field}: {value}")
        
        return results

async def run_comprehensive_test():
    """Run all enhanced TLD system integration tests"""
    logger.info("🚀 Starting Enhanced TLD Requirements System Integration Test")
    logger.info("=" * 70)
    
    test_suite = EnhancedTLDIntegrationTest()
    
    # Run all test categories
    logger.info("\n1️⃣ TLD VALIDATION FOR CUSTOM NAMESERVERS")
    logger.info("-" * 50)
    tld_validation_results = test_suite.test_tld_validation_for_custom_nameservers()
    
    logger.info("\n2️⃣ NIS2 DIRECTIVE COMPLIANCE")
    logger.info("-" * 50)
    nis2_results = test_suite.test_nis2_directive_compliance()
    
    logger.info("\n3️⃣ 2025 .DK REQUIREMENTS")
    logger.info("-" * 50)
    dk_results = test_suite.test_2025_dk_requirements()
    
    logger.info("\n4️⃣ TRUSTEE SERVICE INTEGRATION")
    logger.info("-" * 50)
    trustee_results = test_suite.test_trustee_service_integration()
    
    logger.info("\n5️⃣ OPENPROVIDER ADDITIONAL DATA PREPARATION")
    logger.info("-" * 50)
    additional_data_results = test_suite.test_openprovider_additional_data_preparation()
    
    # Final summary
    logger.info("\n" + "=" * 70)
    logger.info("🎉 ENHANCED TLD REQUIREMENTS SYSTEM TEST COMPLETE")
    
    # Calculate overall success rate
    total_tests = (
        len(tld_validation_results) + 
        len(nis2_results) + 
        1 +  # dk test
        len(trustee_results) + 
        len(additional_data_results)
    )
    
    successful_tests = (
        sum(1 for r in tld_validation_results if r["actual_allowed"] == r["expected_allowed"]) +
        sum(1 for r in nis2_results if r["nis2_affected"]) +
        (1 if dk_results["has_2025_requirement"] else 0) +
        sum(1 for r in trustee_results if r["actual_trustee"] == r["expected_trustee"]) +
        sum(1 for r in additional_data_results if r["has_expected_fields"])
    )
    
    success_rate = (successful_tests / total_tests) * 100
    logger.info(f"📊 Overall Success Rate: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        logger.info("✅ Enhanced TLD Requirements System is production-ready!")
    elif success_rate >= 75:
        logger.info("⚠️ Enhanced TLD Requirements System needs minor adjustments")
    else:
        logger.info("❌ Enhanced TLD Requirements System needs significant work")
    
    return {
        "success_rate": success_rate,
        "tld_validation": tld_validation_results,
        "nis2_compliance": nis2_results,
        "dk_2025": dk_results,
        "trustee_services": trustee_results,
        "additional_data": additional_data_results
    }


if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())