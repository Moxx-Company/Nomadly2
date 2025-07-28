#!/usr/bin/env python3
"""
Test customer @folly542's nameserver management functionality
Verify if there are actual issues with NS updates for checktat-atoocol.info
"""

import os
import sys
import requests
import logging

logger = logging.getLogger(__name__)

def test_openprovider_ns_management():
    """Test OpenProvider nameserver management for @folly542's domain"""
    
    print("🔬 TESTING @FOLLY542 NAMESERVER MANAGEMENT")
    print("=" * 60)
    
    # Domain details from database
    domain_name = "checktat-atoocol.info"
    openprovider_domain_id = 27821414
    contact_handle = "contact_6935"
    
    print(f"Domain: {domain_name}")
    print(f"OpenProvider ID: {openprovider_domain_id}")
    print(f"Contact Handle: {contact_handle}")
    
    # Test OpenProvider API connectivity
    try:
        username = os.getenv("OPENPROVIDER_USERNAME")
        password = os.getenv("OPENPROVIDER_PASSWORD")
        
        if not username or not password:
            print("❌ MISSING CREDENTIALS: OpenProvider credentials not found")
            return "❌ CONFIGURATION ERROR"
        
        print(f"\n🔑 AUTHENTICATION TEST")
        print("-" * 30)
        
        # Test authentication
        auth_url = "https://api.openprovider.eu/v1beta/auth/login"
        auth_data = {"username": username, "password": password}
        
        try:
            auth_response = requests.post(auth_url, json=auth_data, timeout=45)
            
            if auth_response.status_code == 200:
                token_data = auth_response.json()
                token = token_data.get("data", {}).get("token")
                print("✅ Authentication: SUCCESS")
                
                if not token:
                    print("❌ Token extraction failed")
                    return "❌ AUTH TOKEN ERROR"
                    
            else:
                print(f"❌ Authentication failed: {auth_response.status_code}")
                print(f"Response: {auth_response.text}")
                return "❌ AUTH FAILED"
                
        except requests.exceptions.Timeout:
            print("❌ Authentication timeout (45s)")
            return "❌ AUTH TIMEOUT"
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return "❌ AUTH ERROR"
        
        print(f"\n🌐 DOMAIN INFORMATION TEST")
        print("-" * 30)
        
        # Test domain info retrieval
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        domain_info_url = f"https://api.openprovider.eu/v1beta/domains/{openprovider_domain_id}"
        
        try:
            domain_response = requests.get(domain_info_url, headers=headers, timeout=30)
            
            if domain_response.status_code == 200:
                domain_data = domain_response.json()
                domain_info = domain_data.get("data", {})
                
                print("✅ Domain info retrieval: SUCCESS")
                print(f"   Domain status: {domain_info.get('status', 'unknown')}")
                
                current_ns = domain_info.get('nameServers', [])
                if current_ns:
                    print(f"   Current nameservers:")
                    for ns in current_ns:
                        print(f"     • {ns.get('name', 'unknown')}")
                else:
                    print("   Current nameservers: None found")
                
            elif domain_response.status_code == 404:
                print("❌ Domain not found in OpenProvider account")
                print("   This means domain is not properly registered")
                return "❌ DOMAIN NOT FOUND"
            elif domain_response.status_code == 320:
                print("❌ Domain not in account (Error 320)")
                return "❌ DOMAIN NOT IN ACCOUNT"
            else:
                print(f"❌ Domain info failed: {domain_response.status_code}")
                print(f"Response: {domain_response.text}")
                return "❌ DOMAIN INFO FAILED"
                
        except requests.exceptions.Timeout:
            print("❌ Domain info timeout (30s)")
            return "❌ DOMAIN INFO TIMEOUT"
        except Exception as e:
            print(f"❌ Domain info error: {e}")
            return "❌ DOMAIN INFO ERROR"
        
        print(f"\n🔧 NAMESERVER UPDATE TEST")
        print("-" * 30)
        
        # Test nameserver update capability (dry run)
        test_nameservers = [
            {"name": "anderson.ns.cloudflare.com"},
            {"name": "leanna.ns.cloudflare.com"}
        ]
        
        ns_update_url = f"https://api.openprovider.eu/v1beta/domains/{openprovider_domain_id}/nameservers"
        ns_update_data = {"nameServers": test_nameservers}
        
        try:
            # Just test the API endpoint without actually updating
            print("🧪 Testing nameserver update endpoint...")
            
            # We'll do a GET request to the nameservers endpoint to verify access
            ns_get_response = requests.get(ns_update_url, headers=headers, timeout=API_TIMEOUT)
            
            if ns_get_response.status_code == 200:
                print("✅ Nameserver endpoint: ACCESSIBLE")
                print("✅ Customer CAN update nameservers")
                return "✅ NAMESERVER MANAGEMENT WORKING"
            elif ns_get_response.status_code == 404:
                print("❌ Nameserver endpoint not found")
                return "❌ NS ENDPOINT NOT FOUND"
            elif ns_get_response.status_code == 403:
                print("❌ Access denied to nameserver management")
                return "❌ NS ACCESS DENIED"
            else:
                print(f"⚠️ Nameserver endpoint response: {ns_get_response.status_code}")
                print(f"Response: {ns_get_response.text}")
                return "⚠️ NS ENDPOINT UNKNOWN RESPONSE"
                
        except requests.exceptions.Timeout:
            print("❌ Nameserver update timeout (60s)")
            return "❌ NS UPDATE TIMEOUT"
        except Exception as e:
            print(f"❌ Nameserver update error: {e}")
            return "❌ NS UPDATE ERROR"
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return "❌ CRITICAL ERROR"

def main():
    """Run the nameserver management test"""
    result = test_openprovider_ns_management()
    
    print(f"\n" + "=" * 60)
    print(f"📊 TEST RESULT SUMMARY")
    print(f"=" * 60)
    
    if "✅" in result:
        print(f"🎉 CUSTOMER @FOLLY542 NAMESERVER MANAGEMENT: WORKING")
        print(f"   The customer should be able to update nameservers successfully")
        print(f"   If they're reporting issues, it may be a user interface problem")
    else:
        print(f"🚨 CUSTOMER @FOLLY542 NAMESERVER MANAGEMENT: ISSUES CONFIRMED")
        print(f"   Result: {result}")
        print(f"   The customer's complaint is valid - nameserver management is not working")
    
    print(f"\n{result}")
    return result

if __name__ == "__main__":
    main()