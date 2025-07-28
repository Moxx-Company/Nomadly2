#!/usr/bin/env python3
"""
Debug OpenProvider Registration Data Format
Test the correct data format for domain registration
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

def debug_registration_format():
    """Debug the registration data format issue"""
    
    print("🔍 DEBUGGING OPENPROVIDER REGISTRATION FORMAT")
    print("=" * 50)
    
    # Test domain details
    domain_name = "ehobalpbwg.sbs"
    contact_handle = "contact_1337"
    
    print(f"📋 Original domain name: {domain_name}")
    print(f"📋 Contact handle: {contact_handle}")
    
    # Extract domain parts correctly
    if '.' in domain_name:
        domain_parts = domain_name.split('.')
        clean_domain_name = domain_parts[0]
        domain_tld = '.'.join(domain_parts[1:])
    else:
        clean_domain_name = domain_name
        domain_tld = "sbs"  # fallback
    
    print(f"\n🎯 CORRECTED FORMAT:")
    print(f"   Clean domain name: {clean_domain_name}")
    print(f"   Domain TLD: {domain_tld}")
    
    # Correct data format
    correct_data = {
        "domain": {"name": clean_domain_name, "extension": domain_tld},
        "period": 1,
        "owner_handle": contact_handle,
        "admin_handle": contact_handle,
        "tech_handle": contact_handle,
        "billing_handle": contact_handle,
    }
    
    print(f"\n✅ CORRECT API DATA:")
    import json
    print(json.dumps(correct_data, indent=2))
    
    # Compare with incorrect format from logs
    incorrect_data = {
        "domain": {"name": "ehobalpbwg.sbs", "extension": "contact_1337"},
        "period": 1,
        "owner_handle": "JP987496-US",
        "admin_handle": "JP987496-US",
        "tech_handle": "JP987496-US",
        "billing_handle": "JP987496-US",
    }
    
    print(f"\n❌ INCORRECT FORMAT (from logs):")
    print(json.dumps(incorrect_data, indent=2))
    
    print(f"\n🔧 KEY ISSUE IDENTIFIED:")
    print(f"   The 'extension' field was receiving the contact handle instead of TLD")
    print(f"   Fixed: extension should be '{domain_tld}' not '{contact_handle}'")
    
    return correct_data

if __name__ == "__main__":
    debug_registration_format()
    print(f"\n✅ REGISTRATION FORMAT DEBUG COMPLETE")
    print(f"🚀 Ready to test with corrected OpenProvider API")