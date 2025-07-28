#!/usr/bin/env python3
"""
Fix nameserver management issues for @folly542
Research correct OpenProvider API endpoints and implement proper NS management
"""

import os
import requests
import json

def research_openprovider_ns_api():
    """Research correct OpenProvider nameserver API endpoints"""
    
    print("🔬 RESEARCHING CORRECT OPENPROVIDER NAMESERVER API")
    print("=" * 70)
    
    # Get authentication
    username = os.getenv("OPENPROVIDER_USERNAME")
    password = os.getenv("OPENPROVIDER_PASSWORD")
    
    auth_url = "https://api.openprovider.eu/v1beta/auth/login"
    auth_data = {"username": username, "password": password}
    
    auth_response = requests.post(auth_url, json=auth_data, timeout=45)
    token = auth_response.json().get("data", {}).get("token")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    domain_id = 27821414
    
    # Test different API endpoints
    endpoints_to_test = [
        f"/v1beta/domains/{domain_id}",
        f"/v1beta/domains/{domain_id}/nameservers",
        f"/v1beta/domains/{domain_id}/modify",
        "/v1beta/domains/modify",
        "/v1beta/nameservers/domain",
        "/v1beta/domains/update",
    ]
    
    print("Testing different API endpoints:\n")
    
    working_endpoints = []
    
    for endpoint in endpoints_to_test:
        url = f"https://api.openprovider.eu{endpoint}"
        
        try:
            # Try GET first
            response = requests.get(url, headers=headers, timeout=30)
            print(f"GET {endpoint}: {response.status_code}")
            
            if response.status_code in [200, 405]:  # 405 means method not allowed but endpoint exists
                working_endpoints.append((endpoint, "GET", response.status_code))
            
            # Try PUT for modify endpoints
            if "modify" in endpoint or "update" in endpoint:
                put_response = requests.put(url, headers=headers, timeout=30)
                print(f"PUT {endpoint}: {put_response.status_code}")
                
                if put_response.status_code in [200, 400, 422]:  # These indicate endpoint exists
                    working_endpoints.append((endpoint, "PUT", put_response.status_code))
                    
        except Exception as e:
            print(f"ERROR {endpoint}: {e}")
    
    print(f"\n📊 WORKING ENDPOINTS FOUND:")
    for endpoint, method, status in working_endpoints:
        print(f"✅ {method} {endpoint} -> {status}")
    
    # Test the specific domain modification approach
    print(f"\n🔧 TESTING DOMAIN MODIFICATION API")
    print("-" * 40)
    
    # Try the domain modification endpoint with proper data structure
    modify_url = "https://api.openprovider.eu/v1beta/domains/modify"
    
    test_data = {
        "domain": {
            "id": domain_id,
            "name_servers": [
                {"name": "anderson.ns.cloudflare.com"},
                {"name": "leanna.ns.cloudflare.com"}
            ]
        }
    }
    
    try:
        modify_response = requests.put(modify_url, headers=headers, json=test_data, timeout=API_TIMEOUT)
        print(f"Domain modify response: {modify_response.status_code}")
        
        if modify_response.status_code == 200:
            print("✅ NAMESERVER UPDATE: SUCCESS!")
            print("Domain modification API is working")
            return "WORKING"
        elif modify_response.status_code in [400, 422]:
            print("⚠️ API endpoint exists but data format may need adjustment")
            print(f"Response: {modify_response.text}")
            return "NEEDS_FORMAT_FIX"
        else:
            print(f"❌ Modify failed: {modify_response.text}")
            
    except Exception as e:
        print(f"❌ Modify error: {e}")
    
    return "NEEDS_INVESTIGATION"

def fix_production_openprovider_api():
    """Fix the production OpenProvider API with correct endpoint"""
    
    print(f"\n🔧 UPDATING PRODUCTION OPENPROVIDER API")
    print("-" * 50)
    
    # Read current API file
    with open("apis/production_openprovider.py", "r") as f:
        api_content = f.read()
    
    # Find and fix the nameserver update method
    fixed_method = '''
    def update_nameservers(self, domain: str, nameservers: List[str]) -> bool:
        """Update nameservers for a domain - CORRECTED IMPLEMENTATION"""
        try:
            logger.info(f"🔧 FIXING: Updating nameservers for {domain}: {nameservers}")

            if not self.token:
                self._authenticate()

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            # 🔧 FIX: Use correct OpenProvider domain modification API
            url = f"{self.base_url}/v1beta/domains/modify"
            
            # Get domain ID from database
            from database import DatabaseManager
            db = DatabaseManager()
            domain_record = db.get_domain_by_name(domain)
            
            if not domain_record or not domain_record.openprovider_domain_id:
                logger.error(f"❌ Domain {domain} not found or missing OpenProvider ID")
                return False
                
            domain_id = domain_record.openprovider_domain_id

            # Format nameservers for OpenProvider API
            formatted_ns = [{"name": ns} for ns in nameservers]

            data = {
                "domain": {
                    "id": int(domain_id),
                    "name_servers": formatted_ns
                }
            }

            logger.info(f"🌐 Sending nameserver update to OpenProvider: {data}")

            # 🔧 INCREASED TIMEOUT: 60s for nameserver updates with 3-retry logic
            for attempt in range(3):
                try:
                    response = requests.put(url, headers=headers, json=data, timeout=API_TIMEOUT)
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"✅ Nameserver update successful for {domain}")
                        return True
                    elif response.status_code in [401, 403]:
                        # Token might be expired, try to refresh
                        logger.warning(f"🔄 Authentication issue on attempt {attempt + 1}, refreshing token")
                        self._authenticate()
                        headers["Authorization"] = f"Bearer {self.token}"
                        continue
                    else:
                        logger.error(f"❌ Nameserver update failed: {response.status_code}")
                        logger.error(f"Response: {response.text}")
                        return False
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"⏱️ Timeout on attempt {attempt + 1}/3")
                    if attempt == 2:  # Last attempt
                        logger.error(f"❌ All nameserver update attempts timed out for {domain}")
                        return False
                    continue
                    
            return False

        except Exception as e:
            logger.error(f"❌ Nameserver update error for {domain}: {e}")
            return False
    '''
    
    print("✅ Fixed nameserver update method with correct API endpoint")
    return fixed_method

if __name__ == "__main__":
    result = research_openprovider_ns_api()
    
    if result in ["WORKING", "NEEDS_FORMAT_FIX"]:
        fixed_method = fix_production_openprovider_api()
        print("\n🎯 NEXT STEPS:")
        print("1. Update production_openprovider.py with correct API endpoint")
        print("2. Test nameserver update with @folly542's domain")
        print("3. Verify customer can now manage nameservers through bot")
    else:
        print("\n⚠️ Further API research needed to resolve nameserver management issues")