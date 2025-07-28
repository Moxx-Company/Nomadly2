#!/usr/bin/env python3
"""
Test integration of trustee costs into domain pricing system
Verify that bot now charges correct prices including 2x trustee markup
"""

import sys
from domain_service import get_domain_service

def test_trustee_cost_integration():
    """Test that trustee costs are properly integrated into pricing"""
    
    print("🧮 TESTING TRUSTEE COST INTEGRATION INTO DOMAIN PRICING")
    print("=" * 70)
    
    domain_service = get_domain_service()
    
    # Test cases: domains with different trustee cost scenarios
    test_cases = [
        # Standard domains (no trustee needed)
        {"domain": "test.com", "base_expected": 42.87, "trustee_cost": 0},
        {"domain": "sample.net", "base_expected": 49.47, "trustee_cost": 0},
        {"domain": "example.org", "base_expected": 46.17, "trustee_cost": 0},
        
        # Free trustee service domains
        {"domain": "brasil.com.br", "base_expected": 42.87, "trustee_cost": 0},  # Free trustee
        {"domain": "japan.jp", "base_expected": 42.87, "trustee_cost": 0},      # Free trustee
        {"domain": "korea.kr", "base_expected": 42.87, "trustee_cost": 0},      # Free trustee
        
        # Paid trustee service domains (2x multiplier applied)
        {"domain": "france.fr", "base_expected": 42.87, "trustee_cost": 30},    # $15 * 2 = $30
        {"domain": "europe.eu", "base_expected": 42.87, "trustee_cost": 30},    # $15 * 2 = $30
        {"domain": "canada.ca", "base_expected": 42.87, "trustee_cost": 40},    # $20 * 2 = $40
        {"domain": "australia.au", "base_expected": 42.87, "trustee_cost": 50}, # $25 * 2 = $50
        {"domain": "germany.de", "base_expected": 42.87, "trustee_cost": 20},   # $10 * 2 = $20
        {"domain": "denmark.dk", "base_expected": 42.87, "trustee_cost": 24},   # $12 * 2 = $24
        {"domain": "brazilian.br", "base_expected": 42.87, "trustee_cost": 36}, # $18 * 2 = $36
    ]
    
    all_passed = True
    
    print("📊 TRUSTEE COST INTEGRATION TEST RESULTS:")
    print("-" * 70)
    print(f"{'Domain':<20} {'Base Price':<12} {'Trustee':<10} {'Total':<12} {'Status':<8}")
    print("-" * 70)
    
    for case in test_cases:
        domain = case["domain"]
        base_expected = case["base_expected"]
        trustee_expected = case["trustee_cost"]
        total_expected = base_expected + trustee_expected
        
        # Get actual pricing from domain service (now includes trustee costs)
        actual_total = domain_service.get_domain_price(domain)
        
        # Check if pricing matches expected total
        price_match = abs(actual_total - total_expected) <= 0.01
        status = "✅ PASS" if price_match else "❌ FAIL"
        
        if not price_match:
            all_passed = False
        
        print(f"{domain:<20} ${base_expected:<11.2f} ${trustee_expected:<9.2f} ${actual_total:<11.2f} {status:<8}")
        
        if not price_match:
            print(f"  Expected: ${total_expected:.2f}, Got: ${actual_total:.2f}")
    
    print("-" * 70)
    
    # Summary
    if all_passed:
        print("✅ ALL TRUSTEE COST INTEGRATION TESTS PASSED")
        print("💰 Domain service now correctly includes 2x trustee markup")
        print("🎯 Bot will charge accurate prices including trustee services")
    else:
        print("❌ SOME TRUSTEE COST INTEGRATION TESTS FAILED")
        print("🔧 Check domain service _get_trustee_cost() method")
    
    print("\n🧾 SAMPLE CUSTOMER INVOICES WITH TRUSTEE COSTS:")
    print("-" * 50)
    
    sample_invoices = [
        "example.com",     # Standard domain
        "mybrand.fr",      # France domain with trustee
        "startup.ca",      # Canada domain with trustee  
        "business.com.br", # Brazil domain with free trustee
        "shop.au",         # Australia domain with trustee
    ]
    
    for domain in sample_invoices:
        price = domain_service.get_domain_price(domain)
        tld = "." + domain.split(".", 1)[1]
        trustee_cost = domain_service._get_trustee_cost(tld)
        base_price = price - trustee_cost
        
        print(f"\n📄 Invoice: {domain}")
        print(f"   Domain Registration (1 year): ${base_price:.2f}")
        if trustee_cost > 0:
            print(f"   Local Presence Service: ${trustee_cost:.2f}")
        print(f"   TOTAL: ${price:.2f}")
    
    return all_passed

if __name__ == "__main__":
    success = test_trustee_cost_integration()
    
    print("\n" + "="*70)
    if success:
        print("🎉 TRUSTEE COST INTEGRATION SUCCESSFUL")
        print("📊 All domain prices now include 2x trustee markup")
        print("✅ Bot ready for accurate international domain billing")
    else:
        print("⚠️  TRUSTEE COST INTEGRATION NEEDS FIXES")
        print("🔧 Check domain service pricing calculations")
    print("="*70)