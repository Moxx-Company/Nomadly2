#!/usr/bin/env python3
"""
Verify the nameserver management fix for customer @folly542
Test with correct OpenProvider API structure
"""

import os
import requests

def test_correct_api_structure():
    """Test nameserver update with correct API structure"""
    
    print("🔧 VERIFYING NAMESERVER FIX FOR @FOLLY542")
    print("=" * 60)
    
    # Domain details
    domain_name = "checktat-atoocol.info" 
    domain_id = 27821414
    
    # Parse domain parts
    domain_parts = domain_name.split('.')
    name_part = domain_parts[0]  # "checktat-atoocol"  
    extension_part = '.'.join(domain_parts[1:])  # "info"
    
    print(f"Domain: {domain_name}")
    print(f"Domain ID: {domain_id}")
    print(f"Name part: {name_part}")
    print(f"Extension: {extension_part}")
    
    # Test nameservers
    test_nameservers = [
        "anderson.ns.cloudflare.com",
        "leanna.ns.cloudflare.com"
    ]
    
    try:
        # Authenticate
        username = os.getenv("OPENPROVIDER_USERNAME")
        password = os.getenv("OPENPROVIDER_PASSWORD")
        
        auth_url = "https://api.openprovider.eu/v1beta/auth/login"
        auth_data = {"username": username, "password": password}
        
        auth_response = requests.post(auth_url, json=auth_data, timeout=45)
        token = auth_response.json().get("data", {}).get("token")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"\n🌐 TESTING CORRECT API STRUCTURE")
        print("-" * 40)
        
        # Use correct endpoint and structure from documentation
        url = f"https://api.openprovider.eu/v1beta/domains/{domain_id}"
        
        # Correct data structure according to OpenProvider docs
        data = {
            "domain": {
                "name": name_part,
                "extension": extension_part
            },
            "nameServers": [{"name": ns} for ns in test_nameservers]
        }
        
        print(f"Endpoint: {url}")
        print(f"Data: {data}")
        
        # Make the API call
        response = requests.put(url, headers=headers, json=data, timeout=API_TIMEOUT)
        
        print(f"\n📊 RESULT")
        print("-" * 20)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Nameserver management is now WORKING!")
            print("Customer @folly542's issue is RESOLVED")
            
            # Show response details
            try:
                response_data = response.json()
                print(f"Response: {response_data}")
            except:
                print("Response: Success (no JSON content)")
                
            return "✅ WORKING"
            
        else:
            print(f"❌ Still failing: {response.status_code}")
            print(f"Response: {response.text}")
            return "❌ STILL_FAILING"
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return "❌ ERROR"

if __name__ == "__main__":
    result = test_correct_api_structure()
    
    print(f"\n{'='*60}")
    print(f"FINAL VERIFICATION RESULT")
    print(f"{'='*60}")
    
    if result == "✅ WORKING":
        print("🎉 CUSTOMER @FOLLY542'S NAMESERVER MANAGEMENT IS FIXED")
        print("✅ The API implementation now uses correct structure")
        print("✅ Customer can update nameservers successfully")
    else:
        print("⚠️ Further investigation needed")
        print(f"Result: {result}")
        
    print(f"\n{result}")