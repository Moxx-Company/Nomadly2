#!/usr/bin/env python3
"""
Test script to verify 3.8x pricing multiplier is working correctly
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from api_services import OpenProviderAPI
from domain_service import get_domain_service

async def test_pricing_multiplier():
    """Test that 3.8x pricing multiplier is applied correctly"""
    print("🧪 TESTING 3.8x PRICING MULTIPLIER")
    print("=" * 40)
    
    # Test configuration
    print(f"✅ Config PRICE_MULTIPLIER: {Config.PRICE_MULTIPLIER}")
    print(f"✅ Config DEFAULT_DOMAIN_PRICE: ${Config.DEFAULT_DOMAIN_PRICE}")
    
    # Test domains with known pricing
    test_domains = [
        "testdomain123456.com",
        "testdomain789012.sbs", 
        "testdomain345678.net"
    ]
    
    # Test with domain service
    domain_service = get_domain_service()
    
    for domain in test_domains:
        try:
            print(f"\n🔍 Testing pricing for: {domain}")
            domain_info = await domain_service.get_domain_info(domain)
            
            if domain_info:
                price = domain_info.get("price", "N/A")
                available = domain_info.get("available", False)
                
                print(f"  • Available: {'Yes' if available else 'No'}")
                print(f"  • Final Price: ${price}")
                
                # Check if pricing looks reasonable (should be higher than base due to 3.8x)
                if isinstance(price, (int, float)) and price > 10:
                    print(f"  ✅ Price appears to include 3.8x multiplier")
                else:
                    print(f"  ⚠️  Price may not include multiplier: ${price}")
            else:
                print(f"  ❌ Could not get domain info for {domain}")
                
        except Exception as e:
            print(f"  ❌ Error testing {domain}: {e}")
    
    # Test API services directly
    print(f"\n🔧 Testing API services directly...")
    api_service = OpenProviderAPI()
    
    try:
        result = api_service.check_domain_availability("testdomain999888.com")
        if result.get("price"):
            api_price = result.get("api_price", "N/A")
            final_price = result.get("price", "N/A") 
            print(f"  • API Price: ${api_price}")
            print(f"  • Final Price (with multiplier): ${final_price}")
            
            if api_price != "N/A" and final_price != "N/A":
                calculated_multiplier = final_price / api_price if api_price > 0 else 0
                print(f"  • Calculated multiplier: {calculated_multiplier:.2f}x")
                
                if abs(calculated_multiplier - 3.8) < 0.1:
                    print("  ✅ 3.8x multiplier applied correctly")
                else:
                    print("  ⚠️  Multiplier may not be 3.8x")
        else:
            print("  ⚠️  No pricing data returned from API")
            
    except Exception as e:
        print(f"  ❌ API test error: {e}")
    
    print(f"\n✅ Pricing multiplier testing complete!")

if __name__ == "__main__":
    asyncio.run(test_pricing_multiplier())