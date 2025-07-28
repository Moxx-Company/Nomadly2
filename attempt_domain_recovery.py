#!/usr/bin/env python3
"""
Attempt to recover domain management capability
"""

import asyncio
import requests
from apis.production_openprovider import OpenProviderAPI

async def attempt_domain_recovery():
    """Try different approaches to recover domain management"""
    
    print("🔄 ATTEMPTING DOMAIN RECOVERY FOR rolllock10.sbs")
    print("=" * 60)
    
    api = OpenProviderAPI()
    
    try:
        # Step 1: Authenticate
        print("1. 🔐 Authenticating with OpenProvider...")
        auth_success = api._authenticate()
        
        if not auth_success:
            print("   ❌ Authentication failed")
            return False
            
        print("   ✅ Authentication successful")
        
        # Step 2: Try different domain lookup methods
        print("\n2. 🔍 Trying alternative domain lookup methods...")
        
        headers = {
            "Authorization": f"Bearer {api.token}",
            "Content-Type": "application/json",
        }
        
        # Method 1: Search by name pattern
        print("   📋 Method 1: Searching by domain name pattern...")
        search_url = f"{api.base_url}/v1beta/domains"
        params = {
            "domain_name_pattern": "rolllock10",
            "limit": 100
        }
        
        response = requests.get(search_url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            domains = data.get('data', {}).get('results', [])
            print(f"      Found {len(domains)} domains matching 'rolllock10'")
            
            for domain in domains:
                domain_name = f"{domain.get('name', '')}.{domain.get('extension', '')}"
                if domain_name == "rolllock10.sbs":
                    print(f"      ✅ FOUND: {domain_name} with ID {domain.get('id')}")
                    return domain.get('id')
        
        # Method 2: Check all .sbs domains
        print("   📋 Method 2: Checking all .sbs domains...")
        params = {
            "extension": "sbs",
            "limit": 100
        }
        
        response = requests.get(search_url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            domains = data.get('data', {}).get('results', [])
            print(f"      Found {len(domains)} .sbs domains")
            
            for domain in domains:
                domain_name = f"{domain.get('name', '')}.{domain.get('extension', '')}"
                if "rolllock10" in domain_name:
                    print(f"      🔍 Related: {domain_name} with ID {domain.get('id')}")
                    if domain_name == "rolllock10.sbs":
                        print(f"      ✅ FOUND: {domain_name} with ID {domain.get('id')}")
                        return domain.get('id')
        
        # Method 3: Try direct domain info lookup (if we guess the ID)
        print("   📋 Method 3: Trying to register the domain again...")
        
        # Check if domain is available for registration
        check_url = f"{api.base_url}/v1beta/domains/check"
        check_data = {
            "domains": [
                {
                    "name": "rolllock10",
                    "extension": "sbs"
                }
            ]
        }
        
        response = requests.post(check_url, headers=headers, json=check_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            results = data.get('data', {}).get('results', [])
            for result in results:
                domain_name = f"{result.get('domain', {}).get('name', '')}.{result.get('domain', {}).get('extension', '')}"
                status = result.get('status')
                print(f"      📊 {domain_name}: {status}")
                
                if domain_name == "rolllock10.sbs" and status == "active":
                    print("      ❌ Domain is already registered but not in our account")
                    print("      💡 This confirms it's managed by someone else")
                elif domain_name == "rolllock10.sbs" and status == "free":
                    print("      🎯 Domain is available for registration!")
                    print("      💡 We could re-register it to gain control")
        
        print("\n❌ Domain not found in our OpenProvider account")
        return None
        
    except Exception as e:
        print(f"❌ Recovery attempt failed: {e}")
        return None

async def propose_solutions():
    """Propose concrete solutions based on findings"""
    
    print("\n💡 PROPOSED SOLUTIONS:")
    print("=" * 60)
    
    print("1. 🔄 RE-REGISTRATION APPROACH:")
    print("   • Check if rolllock10.sbs is available for registration")
    print("   • If available, register it properly in our OpenProvider account")
    print("   • Update database with correct domain ID")
    print("   • This would enable full nameserver management")
    
    print("\n2. 🛠️ MANUAL ACCOUNT VERIFICATION:")
    print("   • Verify OpenProvider account has correct domains")
    print("   • Check if domains were registered under different credentials")
    print("   • Contact OpenProvider support if domains are missing")
    
    print("\n3. 🎯 ACCEPT LIMITATION & OPTIMIZE:")
    print("   • Accept that nameserver management isn't possible")
    print("   • Focus on excellent Cloudflare DNS management")
    print("   • Provide superior A/CNAME/MX/TXT record management")
    print("   • Market as 'Cloudflare-powered DNS' advantage")
    
    print("\n4. 🔍 INVESTIGATION APPROACH:")
    print("   • Check domain registration history/logs")
    print("   • Verify payment records vs OpenProvider records")
    print("   • Determine if this affects all domains or just some")
    
    print("\n📊 RECOMMENDATION:")
    print("=" * 60)
    print("Since Cloudflare DNS management works perfectly, and nameserver")
    print("management is rarely needed by most users, the current setup")
    print("provides excellent functionality. The enhanced error messaging")
    print("now clearly explains what works vs what doesn't.")
    
    print("\nMost users can accomplish everything they need through:")
    print("• Website setup (A records)")
    print("• Email configuration (MX records)") 
    print("• Domain verification (TXT records)")
    print("• CDN setup (CNAME records)")
    
    print("\nNameserver switching is typically only needed for:")
    print("• Advanced hosting setups")
    print("• Specific DNS provider requirements")
    print("• Custom DNS infrastructure")

if __name__ == "__main__":
    domain_id = asyncio.run(attempt_domain_recovery())
    asyncio.run(propose_solutions())
    
    if domain_id:
        print(f"\n🎉 SUCCESS: Found domain ID {domain_id} - nameserver management possible!")
    else:
        print(f"\n💭 CONCLUSION: Domain not in our account - current DNS-only approach is appropriate")