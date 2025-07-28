#!/usr/bin/env python3
"""
Debug cryptocurrency pricing issue - check actual values being passed
"""

import asyncio
import sys
import os

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from domain_service import get_domain_service

async def debug_crypto_pricing():
    """Debug the pricing values being used in crypto payments"""
    
    print("🔍 DEBUGGING CRYPTOCURRENCY PRICING ISSUE")
    print("=" * 60)
    
    # Test the exact domain from the user's example
    test_domain = "pleasedearlied.de"
    
    try:
        domain_service = get_domain_service()
        
        print(f"\n📊 Testing pricing for: {test_domain}")
        print("-" * 50)
        
        # Test 1: Real-time pricing (what crypto payment should use)
        try:
            domain_info = await domain_service.get_domain_info(test_domain)
            realtime_price = domain_info.get("price") if domain_info else None
            print(f"🌐 Real-time API Price: ${realtime_price}")
        except Exception as e:
            print(f"❌ Real-time pricing failed: {e}")
            realtime_price = None
        
        # Test 2: Cached pricing (fallback)
        cached_price = domain_service.get_domain_price(test_domain)
        print(f"💾 Cached Price:       ${cached_price}")
        
        # Test 3: What the crypto payment function would actually use
        if realtime_price is not None:
            final_price = realtime_price
            print(f"✅ Crypto would use:   ${final_price} (real-time)")
        else:
            final_price = cached_price
            print(f"⚠️ Crypto would use:   ${final_price} (cached fallback)")
        
        # Test 4: Check ETH conversion 
        print(f"\n💎 ETH Conversion Analysis:")
        print("-" * 30)
        
        # Estimate ETH amount based on ~$2600 per ETH
        eth_rate = 2600  # Approximate ETH price
        expected_eth = final_price / eth_rate
        print(f"Expected ETH amount: {expected_eth:.8f} ETH")
        
        # Compare with user's observation (~$14 worth)
        user_observed_usd = 14.0
        user_observed_eth = user_observed_usd / eth_rate
        print(f"User observed (~$14): {user_observed_eth:.8f} ETH")
        
        # Calculate what price would result in $14 worth
        implied_price = user_observed_usd
        print(f"Implied USD price: ${implied_price:.2f}")
        
        print(f"\n🔍 ANALYSIS:")
        if abs(final_price - implied_price) > 2:
            print(f"❌ PRICING MISMATCH DETECTED!")
            print(f"   Expected: ${final_price:.2f}")
            print(f"   User saw: ~${implied_price:.2f}")
            print(f"   Difference: ${abs(final_price - implied_price):.2f}")
            
            if abs(9.99 - implied_price) < 2:
                print(f"🎯 ROOT CAUSE: Crypto payment still using old raw price ($9.99)")
            else:
                print(f"🤔 UNKNOWN: Price doesn't match expected patterns")
        else:
            print(f"✅ Pricing appears consistent")
        
        return final_price, implied_price
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return None, None

if __name__ == "__main__":
    asyncio.run(debug_crypto_pricing())