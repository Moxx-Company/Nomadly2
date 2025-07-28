#!/usr/bin/env python3
"""
Investigate why nameserver management can't work and explore potential solutions
"""

import os
import logging
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def investigate_nameserver_management():
    """Investigate the root cause and potential solutions for nameserver management"""
    
    print("🔍 NAMESERVER MANAGEMENT INVESTIGATION")
    print("=" * 60)
    
    try:
        db_manager = get_db_manager()
        
        # Get all domains with their registration details
        from models import RegisteredDomain
        session = db_manager.get_session()
        
        try:
            domains = session.query(RegisteredDomain).all()
            
            print(f"📊 Found {len(domains)} registered domains")
            print()
            
            print("🔍 DOMAIN ANALYSIS:")
            for domain in domains[:3]:  # Analyze first 3 domains
                print(f"\n📋 Domain: {domain.domain_name}")
                print(f"   OpenProvider ID: {domain.openprovider_domain_id}")
                print(f"   Contact Handle: {domain.openprovider_contact_handle}")
                print(f"   Registration Date: {domain.created_at}")
                print(f"   Nameserver Mode: {domain.nameserver_mode}")
                
                # Try to understand why it's marked as not manageable
                if str(domain.openprovider_domain_id) == "not_manageable_account_mismatch":
                    print(f"   ❌ Status: Domain not manageable - account mismatch")
                    print(f"   🔍 Possible reasons:")
                    print(f"      • Domain registered under different OpenProvider account")
                    print(f"      • Domain transferred or moved after registration")
                    print(f"      • Registration process incomplete or failed")
                    print(f"      • Domain exists but not in our OpenProvider control")
            
            print("\n" + "=" * 60)
            print("🎯 ROOT CAUSE ANALYSIS:")
            print("=" * 60)
            
            print("The domains were registered but marked as 'not_manageable_account_mismatch'")
            print("This typically means:")
            print("1. Domains exist in OpenProvider system")
            print("2. But they're not in our specific OpenProvider account")
            print("3. Could be registration race condition issues")
            print("4. Or domains registered under different credentials")
            
            print("\n💡 POTENTIAL SOLUTIONS:")
            print("=" * 60)
            
            print("1. 🔍 DOMAIN ID LOOKUP:")
            print("   • Try to find actual OpenProvider domain IDs")
            print("   • Query OpenProvider API for domain details")
            print("   • Update database with correct IDs")
            
            print("\n2. 🔄 RE-REGISTRATION ATTEMPT:")
            print("   • Check if domains can be properly claimed")
            print("   • Update registration process to get correct IDs")
            print("   • Ensure domains are in our account")
            
            print("\n3. 🛠️ MANUAL DOMAIN ID CORRECTION:")
            print("   • Use OpenProvider customer panel to find IDs")
            print("   • Manually update database with correct values")
            print("   • Test nameserver management after correction")
            
            print("\n4. 🎯 OPENPROVIDER API INVESTIGATION:")
            print("   • Test API access with current credentials")
            print("   • List domains in our account")
            print("   • Compare with database records")
            
            print("\n📊 IMMEDIATE TESTING APPROACH:")
            print("=" * 60)
            print("Let's test if we can:")
            print("1. Authenticate with OpenProvider API")
            print("2. List domains in our account")
            print("3. Find if rolllock10.sbs is actually manageable")
            print("4. Get the correct domain ID if it exists")
            
            return True
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Investigation error: {e}")
        return False

async def test_openprovider_domain_access():
    """Test if we can actually access domains through OpenProvider API"""
    
    print("\n🧪 TESTING OPENPROVIDER DOMAIN ACCESS")
    print("=" * 60)
    
    try:
        from apis.production_openprovider import OpenProviderAPI
        
        # Initialize OpenProvider API
        api = OpenProviderAPI()
        
        print("1. 🔐 Testing authentication...")
        auth_success = api._authenticate()
        
        if auth_success:
            print("   ✅ Authentication successful")
            
            print("\n2. 🔍 Testing domain lookup for rolllock10.sbs...")
            
            # Try to get domain details
            import requests
            
            headers = {
                "Authorization": f"Bearer {api.token}",
                "Content-Type": "application/json",
            }
            
            # Try to search for the domain
            search_url = f"{api.base_url}/v1beta/domains"
            
            try:
                response = requests.get(search_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    domains_data = response.json()
                    print(f"   📊 API Response: {response.status_code}")
                    
                    # Look for our domain
                    domains = domains_data.get('data', {}).get('results', [])
                    print(f"   📋 Found {len(domains)} domains in OpenProvider account")
                    
                    rolllock_found = False
                    for domain in domains:
                        domain_name = f"{domain.get('name', '')}.{domain.get('extension', '')}"
                        domain_id = domain.get('id')
                        
                        if domain_name == "rolllock10.sbs":
                            print(f"   ✅ FOUND rolllock10.sbs with ID: {domain_id}")
                            rolllock_found = True
                            
                            # This is the solution! Update database with correct ID
                            print(f"   🎯 SOLUTION: Update database with correct ID {domain_id}")
                            return domain_id
                        
                        print(f"   📋 Domain: {domain_name} (ID: {domain_id})")
                    
                    if not rolllock_found:
                        print("   ❌ rolllock10.sbs NOT found in our OpenProvider account")
                        print("   🔍 This confirms the domain is not manageable through our account")
                else:
                    print(f"   ❌ API Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Domain lookup error: {e}")
                
        else:
            print("   ❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ OpenProvider API test error: {e}")
        
    return None

if __name__ == "__main__":
    investigate_nameserver_management()
    
    # Test if we can actually find the domain
    import asyncio
    domain_id = asyncio.run(test_openprovider_domain_access())
    
    if domain_id:
        print(f"\n🎉 SOLUTION FOUND: Domain ID {domain_id} can be used to enable nameserver management!")
    else:
        print(f"\n💡 CONCLUSION: Domain is not in our OpenProvider account - nameserver management not possible")