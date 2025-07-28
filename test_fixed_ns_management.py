#!/usr/bin/env python3
"""
Test the fixed nameserver management for customer @folly542
Verify if the corrected API implementation works
"""

import os
import sys
import requests
import logging

def test_fixed_nameserver_api():
    """Test the fixed OpenProvider nameserver API"""
    
    print("🔧 TESTING FIXED NAMESERVER MANAGEMENT FOR @FOLLY542")
    print("=" * 70)
    
    # Domain details
    domain_name = "checktat-atoocol.info"
    openprovider_domain_id = 27821414
    
    # Test nameservers
    test_nameservers = [
        "anderson.ns.cloudflare.com",
        "leanna.ns.cloudflare.com"
    ]
    
    print(f"Domain: {domain_name}")
    print(f"OpenProvider ID: {openprovider_domain_id}")
    print(f"Test Nameservers: {test_nameservers}")
    
    try:
        # Get credentials
        username = os.getenv("OPENPROVIDER_USERNAME")
        password = os.getenv("OPENPROVIDER_PASSWORD")
        
        # Authenticate
        auth_url = "https://api.openprovider.eu/v1beta/auth/login"
        auth_data = {"username": username, "password": password}
        
        auth_response = requests.post(auth_url, json=auth_data, timeout=45)
        token = auth_response.json().get("data", {}).get("token")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"\n🔧 TESTING FIXED API IMPLEMENTATION")
        print("-" * 50)
        
        # Use the corrected API endpoint and data structure
        url = "https://api.openprovider.eu/v1beta/domains/modify"
        
        # Format data according to OpenProvider documentation
        formatted_ns = [{"name": ns} for ns in test_nameservers]
        
        data = {
            "domain": {
                "id": int(openprovider_domain_id),
                "name_servers": formatted_ns
            }
        }
        
        print(f"Using URL: {url}")
        print(f"Data structure: {data}")
        
        # Make the API call
        response = requests.put(url, headers=headers, json=data, timeout=API_TIMEOUT)
        
        print(f"\n📊 API RESPONSE")
        print("-" * 20)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Nameserver management is now WORKING")
            print("Customer @folly542 can now update nameservers successfully")
            return "✅ FIXED"
        elif response.status_code == 400:
            print("\n⚠️ Data format needs further adjustment")
            return "⚠️ NEEDS_FORMAT_ADJUSTMENT" 
        elif response.status_code == 422:
            print("\n⚠️ Validation error - may need different data structure")
            return "⚠️ VALIDATION_ERROR"
        else:
            print(f"\n❌ Still not working: {response.status_code}")
            return "❌ STILL_BROKEN"
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return "❌ ERROR"

def test_alternative_formats():
    """Test alternative API data formats"""
    
    print(f"\n🧪 TESTING ALTERNATIVE DATA FORMATS")
    print("-" * 50)
    
    # Get credentials
    username = os.getenv("OPENPROVIDER_USERNAME")  
    password = os.getenv("OPENPROVIDER_PASSWORD")
    
    # Authenticate
    auth_url = "https://api.openprovider.eu/v1beta/auth/login"
    auth_data = {"username": username, "password": password}
    
    auth_response = requests.post(auth_url, json=auth_data, timeout=45)
    token = auth_response.json().get("data", {}).get("token")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    domain_id = 27821414
    url = "https://api.openprovider.eu/v1beta/domains/modify"
    
    # Try different data format variations
    formats_to_test = [
        # Format 1: name_servers
        {
            "domain": {
                "id": domain_id,
                "name_servers": [
                    {"name": "anderson.ns.cloudflare.com"},
                    {"name": "leanna.ns.cloudflare.com"}
                ]
            }
        },
        # Format 2: nameServers 
        {
            "domain": {
                "id": domain_id,
                "nameServers": [
                    {"name": "anderson.ns.cloudflare.com"},
                    {"name": "leanna.ns.cloudflare.com"}
                ]
            }
        },
        # Format 3: ns_group
        {
            "domain": {
                "id": domain_id,
                "ns_group": {
                    "name_servers": [
                        {"name": "anderson.ns.cloudflare.com"},
                        {"name": "leanna.ns.cloudflare.com"}
                    ]
                }
            }
        }
    ]
    
    for i, data_format in enumerate(formats_to_test, 1):
        try:
            print(f"\n🧪 Testing format {i}: {list(data_format['domain'].keys())}")
            
            response = requests.put(url, headers=headers, json=data_format, timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ FORMAT {i} WORKS!")
                return data_format
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                print(f"   ⚠️ Format {i} - Bad request: {error_data.get('desc', 'Unknown')}")
            else:
                print(f"   ❌ Format {i} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Format {i} error: {e}")
    
    return None

if __name__ == "__main__":
    print("Testing fixed nameserver management implementation...")
    
    # Test main fix
    result = test_fixed_nameserver_api()
    
    # If main fix didn't work, try alternatives
    if result not in ["✅ FIXED"]:
        print("\nTrying alternative data formats...")
        working_format = test_alternative_formats()
        
        if working_format:
            print(f"\n🎉 FOUND WORKING FORMAT!")
            print(f"Update the API with this structure: {working_format}")
        else:
            print(f"\n❌ No working format found - need deeper API research")
    
    print(f"\n{'='*70}")
    print(f"FINAL RESULT: {result}")
    print(f"{'='*70}")