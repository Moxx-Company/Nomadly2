#!/usr/bin/env python3
"""Test script to verify domain search functionality"""

import asyncio
from trustee_service_manager import TrusteeServiceManager

async def test_domain_search():
    manager = TrusteeServiceManager()
    
    # Test domains
    test_domains = [
        "example.com",
        "example.de",
        "example.ca",
        "example.sbs",
        "huhsishdhdd.sbs"
    ]
    
    print("Testing TrusteeServiceManager methods...")
    print("="*60)
    
    for domain in test_domains:
        print(f"\nTesting: {domain}")
        
        # Test check_trustee_requirement
        try:
            trustee_info = manager.check_trustee_requirement(domain)
            print(f"✅ check_trustee_requirement: {trustee_info['requires_trustee']}")
            print(f"   Country: {trustee_info['country']}")
            print(f"   Complexity: {trustee_info['registration_complexity']}")
        except Exception as e:
            print(f"❌ check_trustee_requirement failed: {e}")
        
        # Test calculate_trustee_pricing
        try:
            base_price = 49.50  # Example price
            total_price, pricing_info = manager.calculate_trustee_pricing(base_price, domain)
            print(f"✅ calculate_trustee_pricing:")
            print(f"   Total: ${total_price:.2f}")
            print(f"   Trustee fee: ${pricing_info['trustee_cost']:.2f}")
            print(f"   Risk level: {pricing_info['risk_level']}")
        except Exception as e:
            print(f"❌ calculate_trustee_pricing failed: {e}")
    
    print("\n" + "="*60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test_domain_search())