#!/usr/bin/env python3
"""
Check actual OpenProvider pricing for .com, .org, .net domains
"""

import os
import requests
from config import Config

def check_openprovider_pricing():
    """Check actual OpenProvider pricing"""
    print("🔍 CHECKING ACTUAL OPENPROVIDER PRICING")
    print("=" * 45)
    
    # Get credentials
    username = os.getenv("OPENPROVIDER_USERNAME")
    password = os.getenv("OPENPROVIDER_PASSWORD")
    
    if not username or not password:
        print("❌ OpenProvider credentials not found")
        return
    
    # Authenticate
    try:
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
        
        # Check domain pricing via domain check API
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        target_domains = [
            {"name": "testpricingcheck12345", "extension": "com"},
            {"name": "testpricingcheck12345", "extension": "org"}, 
            {"name": "testpricingcheck12345", "extension": "net"}
        ]
        
        print(f"\n📊 ACTUAL OPENPROVIDER PRICING:")
        print(f"Current multiplier: {Config.PRICE_MULTIPLIER}x")
        print("-" * 45)
        
        for domain_data in target_domains:
            try:
                check_url = "https://api.openprovider.eu/v1beta/domains/check"
                check_data = {
                    "domains": [domain_data],
                    "with_price": True
                }
                
                response = requests.post(check_url, json=check_data, headers=headers, timeout=8)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("data", {}).get("results", [])
                    
                    if results:
                        result = results[0]
                        price_info = result.get("price", {})
                        reseller_price = price_info.get("reseller", {})
                        api_price = float(reseller_price.get("price", 0))
                        
                        if api_price > 0:
                            final_price = round(api_price * Config.PRICE_MULTIPLIER, 2)
                            tld = domain_data["extension"]
                            print(f".{tld:>3}: ${api_price:>6.2f} → ${final_price:>6.2f} ({Config.PRICE_MULTIPLIER}x)")
                        else:
                            print(f".{domain_data['extension']:>3}: No pricing in response")
                    else:
                        print(f".{domain_data['extension']:>3}: No results returned")
                else:
                    print(f".{domain_data['extension']:>3}: Check failed ({response.status_code})")
                    
            except Exception as e:
                print(f".{domain_data['extension']:>3}: Error - {e}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_openprovider_pricing()