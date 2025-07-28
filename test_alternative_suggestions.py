#!/usr/bin/env python3
"""
Test Alternative Suggestions - Nomadly3 Clean Bot
Quick test to demonstrate alternative domain suggestions functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_services import OpenProviderAPI

def test_alternative_suggestions():
    """Test the alternative suggestions logic"""
    print("🧪 Testing Alternative Suggestions Functionality")
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
    
    # Test domain name
    domain_name = "wewillwin"
    
    print(f"\n🔍 Testing alternatives for '{domain_name}' when main extensions are taken...")
    
    # Alternative suggestions logic (from bot)
    alternatives = [f"{domain_name}offshore.com", f"{domain_name}pro.com", f"get{domain_name}.com", f"{domain_name}.sbs", f"{domain_name}.xyz"]
    alt_available = []
    
    for alt in alternatives[:3]:  # Check 3 alternatives
        try:
            alt_ext = alt.split('.')[1]
            if openprovider:
                alt_result = openprovider.check_domain_availability(alt)
            else:
                # Fallback pricing
                base_prices = {
                    "com": 15.00, "sbs": 14.40, "xyz": 2.40
                }
                base_price = base_prices.get(alt_ext, 15.00)
                offshore_price = base_price * 3.3
                alt_result = {
                    "available": True,  # Assume alternatives are available in fallback
                    "price": round(offshore_price, 2),
                    "currency": "USD"
                }
            
            if alt_result.get("available", False):
                alt_price = alt_result.get("price", 0)
                currency = alt_result.get("currency", "USD")
                alt_price_display = f"${alt_price:.2f} {currency}" if alt_price > 0 else "Price check"
                alt_available.append({"domain": alt, "price": alt_price_display})
                print(f"  ✅ {alt} - {alt_price_display}")
            else:
                print(f"  ❌ {alt} - Also taken")
        except Exception as e:
            print(f"  ⚠️ {alt} - Error: {e}")
            # Fallback for this alternative
            alt_ext = alt.split('.')[1]
            base_price = 15.00 * 3.3
            alt_available.append({"domain": alt, "price": f"${base_price:.2f} USD (estimated)"})
            print(f"  💡 {alt} - ${base_price:.2f} USD (estimated)")
    
    print(f"\n📊 Results:")
    print(f"  Found {len(alt_available)} alternative suggestions")
    
    if alt_available:
        print("\n💡 **Suggested Alternatives:**")
        for alt_info in alt_available:
            print(f"  • {alt_info['domain']} - {alt_info['price']}")
    else:
        print("  No alternatives found")
    
    print("\n✅ Alternative suggestions test completed!")

if __name__ == "__main__":
    test_alternative_suggestions()