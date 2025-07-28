#!/usr/bin/env python3
"""
Get all available top-level domains from OpenProvider
"""

import os
import requests
import json

def get_all_tlds():
    """Get all available TLDs from OpenProvider"""
    print("🌐 FETCHING ALL AVAILABLE TOP-LEVEL DOMAINS")
    print("=" * 50)
    
    # Get credentials
    username = os.getenv("OPENPROVIDER_USERNAME")
    password = os.getenv("OPENPROVIDER_PASSWORD")
    
    if not username or not password:
        print("❌ OpenProvider credentials not found")
        return
    
    try:
        # Authenticate
        auth_url = "https://api.openprovider.eu/v1beta/auth/login"
        auth_data = {"username": username, "password": password}
        
        response = requests.post(auth_url, json=auth_data, timeout=8)
        
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.status_code}")
            return
            
        token = response.json().get("data", {}).get("token")
        if not token:
            print("❌ No token received")
            return
            
        print("✅ Authenticated with OpenProvider")
        
        # Get all extensions
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        extensions_url = "https://api.openprovider.eu/v1beta/domains/extensions"
        response = requests.get(extensions_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Extensions request failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return
            
        data = response.json()
        extensions = data.get("data", {}).get("results", [])
        
        if not extensions:
            print("❌ No extensions found in response")
            return
        
        print(f"\n📊 FOUND {len(extensions)} TOP-LEVEL DOMAINS:")
        print("-" * 50)
        
        # Group TLDs by category
        generic_tlds = []
        country_tlds = []
        new_tlds = []
        premium_tlds = []
        
        for ext in extensions:
            tld = ext.get("name", "").lower()
            if not tld:
                continue
                
            prices = ext.get("prices", {})
            create_price = prices.get("create", {})
            price = float(create_price.get("price", 0))
            
            # Categorize TLDs
            if tld in ["com", "net", "org", "info", "biz"]:
                generic_tlds.append((tld, price))
            elif len(tld) == 2:  # Country codes are typically 2 letters
                country_tlds.append((tld, price))
            elif price > 50:  # Premium TLDs
                premium_tlds.append((tld, price))
            else:
                new_tlds.append((tld, price))
        
        # Display by category
        categories = [
            ("🏛️ GENERIC TLDs", generic_tlds),
            ("🌍 COUNTRY TLDs", country_tlds[:20]),  # Limit country TLDs for readability
            ("🚀 NEW TLDs", new_tlds[:30]),  # Limit new TLDs
            ("💎 PREMIUM TLDs", premium_tlds[:15])  # Limit premium TLDs
        ]
        
        for category_name, tld_list in categories:
            if tld_list:
                print(f"\n{category_name} ({len(tld_list)} shown):")
                tld_list.sort(key=lambda x: x[1])  # Sort by price
                
                for i, (tld, price) in enumerate(tld_list):
                    if i % 4 == 0 and i > 0:
                        print()  # New line every 4 TLDs
                    print(f".{tld:>8} ${price:>6.2f}", end="  ")
                print("\n")
        
        # Save complete list to file
        all_tlds = [(ext.get("name", "").lower(), float(ext.get("prices", {}).get("create", {}).get("price", 0))) 
                   for ext in extensions if ext.get("name")]
        all_tlds.sort()
        
        with open("all_tlds_complete.json", "w") as f:
            json.dump(all_tlds, f, indent=2)
        
        print(f"💾 Complete list saved to all_tlds_complete.json")
        print(f"📊 Total TLDs available: {len(all_tlds)}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_all_tlds()