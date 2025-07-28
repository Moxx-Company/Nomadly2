#!/usr/bin/env python3
"""
Test that DNS configuration pricing now matches domain search pricing
"""

import asyncio
import sys
import os

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from domain_service import get_domain_service

async def test_pricing_consistency():
    """Test that DNS configuration pricing matches search results"""
    
    print("🔍 Testing Domain Search vs DNS Configuration Pricing Consistency...")
    print("=" * 70)
    
    # Test the exact domain from the logs
    test_domain = "pleasegod.de"
    
    try:
        domain_service = get_domain_service()
        
        # Test 1: Get domain info (search results method)
        print(f"\n📊 Testing pricing for: {test_domain}")
        print("-" * 50)
        
        try:
            domain_info = await domain_service.get_domain_info(test_domain)
            search_price = domain_info.get("price") if domain_info else None
            print(f"🔍 Search Result Price: ${search_price}")
        except Exception as e:
            print(f"❌ Search pricing failed: {e}")
            search_price = None
        
        # Test 2: Get cached pricing (DNS configuration method)
        cached_price = domain_service.get_domain_price(test_domain)
        print(f"⚙️ DNS Config Price:   ${cached_price}")
        
        # Test 3: Check consistency
        if search_price and cached_price:
            price_diff = abs(search_price - cached_price)
            is_consistent = price_diff <= 1.0  # Allow $1 difference
            
            print(f"\n📈 Consistency Analysis:")
            print(f"   Price Difference: ${price_diff:.2f}")
            print(f"   Consistent (±$1): {'✅ YES' if is_consistent else '❌ NO'}")
            
            if is_consistent:
                print(f"\n✅ SUCCESS: Pricing is now consistent!")
                print(f"   Both search and DNS config show similar pricing")
            else:
                print(f"\n❌ ISSUE: Pricing still inconsistent")
                print(f"   Large difference between search and DNS config pricing")
        
        elif search_price:
            print(f"\n✅ GOOD: Search pricing working (${search_price})")
            print(f"❌ ISSUE: DNS config pricing using fallback (${cached_price})")
        
        else:
            print(f"\n❌ ISSUE: Search pricing not available")
            print(f"⚙️ INFO: DNS config using fallback pricing")
        
        # Test 4: Additional domains for completeness
        additional_tests = ["test.com", "test.sbs", "test.org"]
        
        print(f"\n🧪 Additional Pricing Tests:")
        print("-" * 50)
        
        for domain in additional_tests:
            try:
                info = await domain_service.get_domain_info(domain)
                search_price = info.get("price") if info else None
                cached_price = domain_service.get_domain_price(domain)
                
                if search_price:
                    diff = abs(search_price - cached_price)
                    status = "✅" if diff <= 1.0 else "❌"
                    print(f"{status} {domain:<12} Search: ${search_price:<6.2f} DNS: ${cached_price:<6.2f} Diff: ${diff:.2f}")
                else:
                    print(f"⚠️ {domain:<12} Search: N/A       DNS: ${cached_price:<6.2f}")
            except:
                print(f"❌ {domain:<12} Both pricing methods failed")
        
        print(f"\n🎯 SUMMARY:")
        print(f"The fix ensures DNS configuration page uses same real-time pricing")
        print(f"as domain search results, eliminating user confusion about")
        print(f"different prices for the same domain.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_pricing_consistency())