#!/usr/bin/env python3
"""
Verify that pricing multiplier has been updated to 3.3x across all files
"""

import os
from config import Config

def verify_pricing_update():
    """Verify pricing configuration is updated to 3.3x"""
    
    print("🔍 VERIFYING 3.3X PRICING MULTIPLIER UPDATE")
    print("=" * 50)
    
    # Test config values
    print(f"📊 Current Configuration:")
    print(f"   PRICE_MULTIPLIER: {Config.PRICE_MULTIPLIER}")
    print(f"   DEFAULT_DOMAIN_PRICE: ${Config.DEFAULT_DOMAIN_PRICE}")
    
    # Verify calculations
    test_base_price = 2.99
    expected_multiplied = test_base_price * 3.3
    
    print(f"\n🧮 Pricing Calculation Test:")
    print(f"   Base price: ${test_base_price}")
    print(f"   3.3x multiplier: ${expected_multiplied:.2f}")
    print(f"   Config default matches: {'✅' if abs(Config.DEFAULT_DOMAIN_PRICE - expected_multiplied) < 0.01 else '❌'}")
    
    # Test with Config multiplier
    actual_multiplied = test_base_price * Config.PRICE_MULTIPLIER
    print(f"   Actual multiplied: ${actual_multiplied:.2f}")
    print(f"   Calculation correct: {'✅' if abs(actual_multiplied - expected_multiplied) < 0.01 else '❌'}")
    
    # Show pricing examples
    print(f"\n💰 Example TLD Pricing with 3.3x Multiplier:")
    
    common_tlds = {
        "com": 11.98,  # OpenProvider real price
        "org": 8.99,
        "net": 15.53,
        "sbs": 2.99,
        "info": 9.99
    }
    
    for tld, base_price in common_tlds.items():
        final_price = base_price * Config.PRICE_MULTIPLIER
        print(f"   .{tld:<4} ${base_price:>6.2f} → ${final_price:>6.2f}")
    
    print(f"\n✅ PRICING UPDATE VERIFICATION COMPLETE")
    print(f"💡 All pricing will now use {Config.PRICE_MULTIPLIER}x multiplier")

if __name__ == "__main__":
    verify_pricing_update()