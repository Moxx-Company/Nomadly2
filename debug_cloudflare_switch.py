#!/usr/bin/env python3
"""
Debug script to diagnose Cloudflare switching issues for claudeb.sbs
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_cloudflare_switch():
    """Debug the Cloudflare switching process for claudeb.sbs"""
    domain = "claudeb.sbs"
    
    print(f"🔍 CLOUDFLARE SWITCHING DIAGNOSTICS")
    print(f"=" * 50)
    print(f"Domain: {domain}")
    print(f"Timestamp: {asyncio.get_event_loop().time()}")
    print()
    
    # Step 1: Check Cloudflare credentials
    print(f"📋 STEP 1: CLOUDFLARE CREDENTIALS CHECK")
    print("-" * 40)
    
    api_token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    email = os.getenv("CLOUDFLARE_EMAIL", "").strip()
    api_key = os.getenv("CLOUDFLARE_GLOBAL_API_KEY", "").strip()
    
    print(f"API Token present: {'Yes' if api_token else 'No'} (Length: {len(api_token)})")
    print(f"Email present: {'Yes' if email else 'No'} ({email[:20] + '...' if email else 'None'})")
    print(f"Global API Key present: {'Yes' if api_key else 'No'} (Length: {len(api_key)})")
    
    # Determine auth method
    if email and api_key and len(api_key) > 10:
        auth_method = "Global API Key"
        print(f"✅ Authentication method: {auth_method}")
    elif api_token and len(api_token) > 10:
        auth_method = "API Token"
        print(f"✅ Authentication method: {auth_method}")
    else:
        auth_method = None
        print(f"❌ No valid authentication method found")
        return
    
    # Step 2: Test Cloudflare API connectivity
    print(f"\n🌐 STEP 2: CLOUDFLARE API CONNECTIVITY TEST")
    print("-" * 45)
    
    try:
        from unified_dns_manager import UnifiedDNSManager
        
        dns_manager = UnifiedDNSManager()
        print(f"DNS Manager enabled: {dns_manager.enabled}")
        print(f"DNS Manager auth method: {dns_manager.auth_method}")
        
        # Test API connection
        import httpx
        headers = dns_manager._get_headers()
        
        async with httpx.AsyncClient() as client:
            # Test with user endpoint
            response = await client.get(
                "https://api.cloudflare.com/client/v4/user",
                headers=headers,
                timeout=10
            )
            
            print(f"API Test Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Connection successful")
                print(f"User ID: {data.get('result', {}).get('id', 'Unknown')}")
                print(f"Email: {data.get('result', {}).get('email', 'Unknown')}")
            else:
                print(f"❌ API Connection failed")
                print(f"Response: {response.text}")
                return
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return
    
    # Step 3: Check if zone already exists
    print(f"\n🔍 STEP 3: ZONE EXISTENCE CHECK")
    print("-" * 35)
    
    try:
        zone_id = await dns_manager.get_zone_id(domain)
        if zone_id:
            print(f"✅ Zone exists: {zone_id}")
            
            # Get zone nameservers
            nameservers = await dns_manager.get_zone_nameservers(zone_id)
            print(f"Zone nameservers: {nameservers}")
        else:
            print(f"ℹ️ No existing zone found for {domain}")
            
            # Try to create zone
            print(f"🆕 Attempting to create new zone...")
            new_zone_id = await dns_manager.create_zone(domain)
            if new_zone_id:
                print(f"✅ Zone created successfully: {new_zone_id}")
                nameservers = await dns_manager.get_zone_nameservers(new_zone_id)
                print(f"New zone nameservers: {nameservers}")
            else:
                print(f"❌ Failed to create zone")
                return
                
    except Exception as e:
        print(f"❌ Error with zone operations: {e}")
        return
    
    # Step 4: Check database status
    print(f"\n📊 STEP 4: DATABASE STATUS CHECK")
    print("-" * 35)
    
    try:
        from database import get_db_manager
        db = get_db_manager()
        
        user_domains = db.get_user_domains(7339720062)  # Your user ID
        domain_found = False
        
        for d in user_domains:
            if d.get('domain_name') == domain:
                domain_found = True
                print(f"✅ Domain found in database")
                print(f"Nameserver mode: {d.get('nameserver_mode', 'unknown')}")
                print(f"Nameservers: {d.get('nameservers', [])}")
                break
        
        if not domain_found:
            print(f"❌ Domain not found in database")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Step 5: Test complete switching process
    print(f"\n⚡ STEP 5: FULL SWITCHING SIMULATION")
    print("-" * 40)
    
    try:
        # Import OpenProvider API
        from apis.production_openprovider import ProductionOpenProviderAPI
        op_api = ProductionOpenProviderAPI()
        
        # Run the complete switch
        switch_result = await dns_manager.switch_domain_to_cloudflare(domain, op_api)
        
        print(f"Switch result: {switch_result}")
        
        if switch_result['success']:
            print(f"✅ COMPLETE SUCCESS!")
            print(f"Zone ID: {switch_result['zone_id']}")
            print(f"Nameservers: {switch_result['nameservers']}")
            print(f"Zone created: {switch_result['zone_created']}")
        else:
            print(f"❌ SWITCH FAILED")
            print(f"Error: {switch_result['error']}")
            
    except Exception as e:
        print(f"❌ Error in full switch test: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🏁 DIAGNOSTIC COMPLETE")
    print(f"=" * 30)

if __name__ == "__main__":
    asyncio.run(debug_cloudflare_switch())