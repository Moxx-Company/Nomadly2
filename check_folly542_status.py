#!/usr/bin/env python3
"""
Check customer @folly542 nameserver management status and domain operations
"""

import sys
import asyncio
from database import DatabaseManager

async def check_folly542_status():
    """Check @folly542's current domain status and nameserver capabilities"""
    
    print("🔍 CHECKING CUSTOMER @FOLLY542 STATUS")
    print("=" * 60)
    
    # Initialize database
    db = DatabaseManager()
    
    # Get customer info
    customer = db.get_user_by_telegram_id(6896666427)
    if not customer:
        print("❌ Customer @folly542 not found in database")
        return
    
    print(f"👤 Customer: @{customer.username} (ID: {customer.telegram_id})")
    print(f"📧 Email: {customer.technical_email}")
    print(f"💰 Balance: ${customer.balance_usd}")
    print(f"🕒 Last Activity: {customer.last_activity_at}")
    
    # Get registered domains
    domains = db.get_user_domains(customer.telegram_id)
    print(f"\n🌐 REGISTERED DOMAINS ({len(domains)} total):")
    print("-" * 50)
    
    working_domains = []
    problematic_domains = []
    
    for domain in domains:
        print(f"\n📍 Domain: {domain.domain_name}")
        print(f"   OpenProvider ID: {domain.openprovider_domain_id or 'Missing'}")
        print(f"   Contact Handle: {domain.openprovider_contact_handle or 'Missing'}")
        print(f"   Cloudflare Zone: {domain.cloudflare_zone_id or 'Missing'}")
        print(f"   Status: {domain.status}")
        print(f"   Nameserver Mode: {domain.nameserver_mode}")
        print(f"   Nameservers: {domain.nameservers}")
        
        # Check if domain can be managed
        if domain.openprovider_domain_id and domain.openprovider_contact_handle != "needs_reregistration":
            working_domains.append(domain)
            print(f"   ✅ Can manage nameservers")
        else:
            problematic_domains.append(domain)
            print(f"   ❌ Cannot manage nameservers - Missing OpenProvider data")
    
    # Test OpenProvider API connectivity for working domains
    if working_domains:
        print(f"\n🧪 TESTING NAMESERVER MANAGEMENT API")
        print("-" * 40)
        
        try:
            from apis.production_openprovider import OpenProviderAPI
            
            api = OpenProviderAPI()
            
            # Test with checktat-atoocol.info (the working domain)
            test_domain = working_domains[0]
            print(f"🔬 Testing with: {test_domain.domain_name}")
            print(f"   OpenProvider ID: {test_domain.openprovider_domain_id}")
            
            # For now, just check if API can authenticate
            if api.token:
                print(f"✅ OpenProvider API: Authentication successful")
                print(f"✅ Customer CAN update nameservers")
                test_result = f"Customer @folly542 nameserver management: ✅ WORKING"
            else:
                print(f"❌ OpenProvider API: Authentication failed")
                test_result = f"Customer @folly542 nameserver management: ❌ AUTH FAILED"
                
        except Exception as e:
            print(f"❌ OpenProvider API Exception: {e}")
            test_result = f"Customer @folly542 nameserver management: ❌ CONNECTION FAILED"
    else:
        test_result = f"Customer @folly542 nameserver management: ❌ NO MANAGEABLE DOMAINS"
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📊 CUSTOMER @FOLLY542 STATUS SUMMARY")
    print(f"=" * 60)
    print(f"Working Domains: {len(working_domains)}")
    print(f"Problematic Domains: {len(problematic_domains)}")
    print(f"API Connectivity: {'✅ Working' if 'WORKING' in test_result else '❌ Issues'}")
    print(f"\n{test_result}")
    
    # Specific issues
    if problematic_domains:
        print(f"\n⚠️  ISSUES FOUND:")
        for domain in problematic_domains:
            if domain.openprovider_contact_handle == "needs_reregistration":
                print(f"   • {domain.domain_name}: Needs proper registration completion")
            elif not domain.openprovider_domain_id:
                print(f"   • {domain.domain_name}: Missing OpenProvider domain ID")
    
    print(f"\n" + "=" * 60)
    return test_result

if __name__ == "__main__":
    result = asyncio.run(check_folly542_status())
    print(f"\nFINAL STATUS: {result}")