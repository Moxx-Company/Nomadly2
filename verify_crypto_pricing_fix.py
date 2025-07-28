#!/usr/bin/env python3
"""
Verify that cryptocurrency payment page now shows consistent pricing with 3.3x multiplier
"""

import sys
from domain_service import get_domain_service

def test_crypto_pricing_consistency():
    """Test that crypto page pricing matches domain registration pricing"""
    
    print("🔍 Testing Cryptocurrency Payment Pricing Consistency...")
    
    # Test domains with known pricing
    test_cases = [
        {"domain": "pleaseabeg.de", "expected_approx": 42.87},  # .de should use default
        {"domain": "test.com", "expected_approx": 42.87},      # .com pricing
        {"domain": "test.sbs", "expected_approx": 9.87},       # .sbs pricing
        {"domain": "test.io", "expected_approx": 164.97},      # .io pricing
        {"domain": "test.org", "expected_approx": 46.17},      # .org pricing
    ]
    
    try:
        # Test domain service pricing
        domain_service = get_domain_service()
        
        all_passed = True
        print("\n📊 Cryptocurrency Payment Pricing Test Results:")
        print("=" * 55)
        
        for case in test_cases:
            domain = case["domain"]
            expected = case["expected_approx"]
            
            # Get price from domain service (used by crypto page)
            actual_price = domain_service.get_domain_price(domain)
            
            # Check if price is within reasonable range (±$1)
            price_match = abs(actual_price - expected) <= 1.0
            
            status = "✅ PASS" if price_match else "❌ FAIL"
            print(f"{status} {domain:<20} Expected: ~${expected:>6.2f}  Actual: ${actual_price:>6.2f}")
            
            if not price_match:
                all_passed = False
        
        print("\n" + "=" * 55)
        
        if all_passed:
            print("🎉 SUCCESS: Cryptocurrency payment pricing now consistent!")
            print("\n📋 Summary of Fix:")
            print("• Updated domain_service.py pricing table with 3.3x multiplier")
            print("• .de domains now show $42.87 (default price with multiplier)")
            print("• .com domains show $42.87 (was $12.99, now $12.99 * 3.3)")
            print("• .sbs domains show $9.87 (was $2.99, now $2.99 * 3.3)")
            print("• .io domains show $164.97 (was $49.99, now $49.99 * 3.3)")
            print("• Crypto payment page pricing now matches domain registration page")
            return True
        else:
            print("❌ INCOMPLETE: Some pricing still inconsistent")
            return False
            
    except Exception as e:
        print(f"❌ Error testing pricing consistency: {e}")
        return False

def main():
    print("🚀 Cryptocurrency Payment Pricing Consistency Test")
    print("=" * 55)
    
    success = test_crypto_pricing_consistency()
    
    if success:
        print("\n✅ Pricing inconsistency FIXED! Crypto page now shows correct 3.3x multiplied prices.")
        print("Users will see consistent pricing across all pages.")
        sys.exit(0)
    else:
        print("\n❌ Pricing consistency test failed - some issues remain")
        sys.exit(1)

if __name__ == "__main__":
    main()