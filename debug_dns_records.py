#!/usr/bin/env python3
"""
Debug DNS Records - Test DNS record retrieval for claudeb.sbs
"""

import asyncio
import sys
import os
from database import get_db_manager
from unified_dns_manager import UnifiedDNSManager

async def test_dns_records():
    """Test DNS record retrieval for claudeb.sbs"""
    domain = "claudeb.sbs"
    
    print(f"🔍 Testing DNS record retrieval for {domain}")
    
    # Test 1: Check database for zone_id
    print("\n📊 Step 1: Database Zone ID Lookup")
    try:
        db = get_db_manager()
        registered_domains = db.get_all_registered_domains()
        
        zone_id = None
        for domain_record in registered_domains:
            if hasattr(domain_record, 'domain_name') and domain_record.domain_name == domain:
                if hasattr(domain_record, 'zone_id') and domain_record.zone_id:
                    zone_id = domain_record.zone_id
                    print(f"✅ Found zone_id in database: {zone_id}")
                    print(f"✅ Domain status: {getattr(domain_record, 'status', 'unknown')}")
                    print(f"✅ Nameserver mode: {getattr(domain_record, 'nameserver_mode', 'unknown')}")
                    break
        
        if not zone_id:
            print(f"❌ No zone_id found in database for {domain}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        zone_id = None
    
    # Test 2: Initialize DNS Manager
    print("\n🔧 Step 2: DNS Manager Initialization")
    try:
        dns_manager = UnifiedDNSManager()
        print(f"✅ DNS Manager initialized")
        print(f"✅ Authentication method: {dns_manager.auth_method}")
        print(f"✅ Manager enabled: {dns_manager.enabled}")
        
        if not dns_manager.enabled:
            print("❌ DNS Manager is disabled - check credentials")
            return
            
    except Exception as e:
        print(f"❌ DNS Manager initialization error: {e}")
        return
    
    # Test 3: Zone ID Lookup via API
    print("\n🌐 Step 3: Zone ID API Lookup")
    try:
        api_zone_id = await dns_manager.get_zone_id(domain)
        if api_zone_id:
            print(f"✅ Zone ID from API: {api_zone_id}")
        else:
            print(f"❌ No zone ID found via API for {domain}")
    except Exception as e:
        print(f"❌ Zone ID API lookup error: {e}")
    
    # Test 4: DNS Records Retrieval
    print("\n📋 Step 4: DNS Records Retrieval")
    try:
        records = await dns_manager.get_dns_records(domain)
        if records:
            print(f"✅ Found {len(records)} DNS records:")
            for i, record in enumerate(records[:5], 1):  # Show first 5 records
                print(f"  {i}. Type: {record.get('type', 'N/A')}, Name: {record.get('name', 'N/A')}, Content: {record.get('content', 'N/A')}")
                print(f"     ID: {record.get('id', 'N/A')}, TTL: {record.get('ttl', 'N/A')}")
        else:
            print(f"❌ No DNS records found for {domain}")
    except Exception as e:
        print(f"❌ DNS records retrieval error: {e}")
    
    # Test 5: Direct Cloudflare API Test
    print("\n☁️ Step 5: Direct Cloudflare API Test")
    try:
        import httpx
        
        # Check credentials
        email = os.getenv("CLOUDFLARE_EMAIL", "").strip()
        api_key = os.getenv("CLOUDFLARE_GLOBAL_API_KEY", "").strip()
        
        if email and api_key:
            headers = {
                "X-Auth-Email": email,
                "X-Auth-Key": api_key,
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient() as client:
                # Test user endpoint
                response = await client.get("https://api.cloudflare.com/client/v4/user", headers=headers)
                if response.status_code == 200:
                    print("✅ Cloudflare API authentication successful")
                else:
                    print(f"❌ Cloudflare API authentication failed: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                
                # Test zones endpoint
                response = await client.get("https://api.cloudflare.com/client/v4/zones", headers=headers)
                if response.status_code == 200:
                    zones_data = response.json()
                    zones = zones_data.get('result', [])
                    print(f"✅ Found {len(zones)} zones in Cloudflare account")
                    
                    # Find claudeb.sbs zone
                    claudeb_zone = None
                    for zone in zones:
                        if zone.get('name') == domain:
                            claudeb_zone = zone
                            print(f"✅ Found {domain} zone: {zone.get('id')}")
                            print(f"✅ Zone status: {zone.get('status')}")
                            break
                    
                    if not claudeb_zone:
                        print(f"❌ {domain} zone not found in Cloudflare account")
                else:
                    print(f"❌ Zones API failed: {response.status_code}")
        else:
            print("❌ Missing Cloudflare credentials")
            
    except Exception as e:
        print(f"❌ Direct API test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_dns_records())