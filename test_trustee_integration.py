#!/usr/bin/env python3
"""
Test script to demonstrate trustee service integration in Nomadly3
Shows how country-specific domains trigger trustee services with pricing
"""

from trustee_service_manager import TrusteeServiceManager

def test_trustee_integration():
    """Test the trustee service integration with various domains"""
    
    trustee_manager = TrusteeServiceManager()
    
    # Test domains that require trustee services
    test_domains = [
        ("mycompany.de", 49.50),  # German domain - requires trustee
        ("business.ca", 59.40),   # Canadian domain - requires trustee  
        ("startup.com", 49.50),   # .com domain - no trustee needed
        ("tech.fr", 52.80),       # French domain - requires trustee
        ("crypto.au", 75.00),     # Australian domain - requires trustee
        ("privacy.eu", 68.00),    # EU domain - requires trustee
        ("secure.br", 45.00),     # Brazilian domain - requires trustee
        ("offshore.net", 59.40),  # .net domain - no trustee needed
    ]
    
    print("🏛️ NOMADLY3 TRUSTEE SERVICE INTEGRATION TEST")
    print("=" * 60)
    print()
    
    for domain, base_price in test_domains:
        print(f"🔍 Testing: {domain}")
        print(f"   Base Price: ${base_price:.2f}")
        
        # Calculate trustee pricing
        final_price, pricing_info = trustee_manager.calculate_trustee_pricing(base_price, domain)
        
        print(f"   Final Price: ${final_price:.2f}")
        
        if pricing_info.get('requires_trustee', False):
            risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(pricing_info.get('risk_level', 'LOW'), "🟢")
            print(f"   🏛️ Trustee Required: {pricing_info.get('trustee_name', 'Professional Service')}")
            print(f"   {risk_emoji} Risk Level: {pricing_info.get('risk_level', 'LOW')}")
            print(f"   📋 Registration Success: {pricing_info.get('registration_success_rate', 95)}%")
            print(f"   📄 Documents Required: {pricing_info.get('documents_required', 'None')}")
            print(f"   💰 Trustee Fee: ${pricing_info.get('trustee_fee', 0):.2f}")
        else:
            print(f"   ✅ No trustee required - standard registration")
        
        print()
    
    print("✅ Trustee service integration test completed!")
    print("🚀 Bot will automatically show trustee pricing and requirements")

if __name__ == "__main__":
    test_trustee_integration()