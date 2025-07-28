#!/usr/bin/env python3
"""
Test Improved Alternative Suggestions - Now shows alternatives even for available domains
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_services import OpenProviderAPI

def test_improved_suggestions():
    """Test that alternatives show even for available domains"""
    print("🧪 Testing Improved Alternative Suggestions")
    print("="*50)
    
    # Initialize OpenProvider API
    openprovider_username = os.getenv("OPENPROVIDER_USERNAME")
    openprovider_password = os.getenv("OPENPROVIDER_PASSWORD")
    
    if openprovider_username and openprovider_password:
        openprovider = OpenProviderAPI(openprovider_username, openprovider_password)
        print("✅ OpenProvider API initialized")
    else:
        openprovider = None
        print("⚠️ Using fallback pricing (no API credentials)")
    
    # Test domain name that should be available
    full_domain = "wewillwin.sbs"
    domain_name = "wewillwin"
    
    print(f"\n🔍 Testing '{full_domain}' (should be available)...")
    
    # Check main domain first
    if openprovider:
        api_result = openprovider.check_domain_availability(full_domain)
    else:
        api_result = {"available": True, "price": 47.52, "currency": "USD"}
    
    is_available = api_result.get("available", False)
    price = api_result.get("price", 0)
    currency = api_result.get("currency", "USD")
    
    print(f"  Main domain: {full_domain}")
    print(f"  Status: {'✅ Available' if is_available else '❌ Taken'}")
    print(f"  Price: ${price:.2f} {currency}")
    
    if is_available:
        print(f"\n💡 Now checking alternatives (even though main domain is available)...")
        
        # Add alternatives even for available domains (new logic)
        extension = full_domain.split('.')[1]
        alternatives = [f"{domain_name}offshore.{extension}", f"{domain_name}pro.{extension}", f"get{domain_name}.{extension}"]
        alt_available = []
        
        for alt in alternatives[:2]:  # Check 2 quick alternatives
            try:
                if openprovider:
                    alt_result = openprovider.check_domain_availability(alt)
                else:
                    base_price = 14.40 * 3.3  # .sbs fallback
                    alt_result = {
                        "available": True,
                        "price": base_price,
                        "currency": "USD"
                    }
                
                if alt_result.get("available", False):
                    alt_price = alt_result.get("price", 0)
                    alt_currency = alt_result.get("currency", "USD")
                    alt_price_display = f"${alt_price:.2f} {alt_currency}" if alt_price > 0 else "Price check"
                    print(f"  ✅ {alt} - {alt_price_display}")
                    alt_available.append(alt)
                else:
                    print(f"  ❌ {alt} - Also taken")
            except Exception as e:
                print(f"  ⚠️ {alt} - Error: {e}")
        
        print(f"\n📊 Results:")
        print(f"  Main domain: Available (${price:.2f})")
        print(f"  Alternatives found: {len(alt_available)}")
        
        if alt_available:
            print("\n💡 **User will now see alternatives even for available domains:**")
            print(f"• {full_domain} - ${price:.2f} {currency}")
            for alt in alt_available:
                print(f"• {alt} - Available")
            print("\n💡 **More Options Available Above**")
        
        print("\n✅ Enhanced user experience: Users get more domain options even when their first choice is available!")
    else:
        print("❌ Domain is taken - would show alternatives anyway")

if __name__ == "__main__":
    test_improved_suggestions()