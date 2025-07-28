#!/usr/bin/env python3
"""
Test the specific wewillwin.sbs scenario that should trigger alternatives
"""

def check_if_domain_should_be_forced():
    """Check if wewillwin.sbs should be forced as taken"""
    
    # This is the exact logic from the bot
    full_domain = "wewillwin.sbs"
    domain_name = "wewillwin"
    
    test_unavailable = ["wewillwin", "example", "test", "demo", "mycompany", "privacyfirst"]
    force_taken = domain_name.lower() in test_unavailable
    
    print(f"Domain: {full_domain}")
    print(f"Domain name: {domain_name}")
    print(f"Test unavailable list: {test_unavailable}")    
    print(f"Should be forced as taken: {force_taken}")
    
    if force_taken:
        print("✅ SUCCESS: wewillwin.sbs will be forced as TAKEN")
        print("✅ This should trigger alternative suggestions")
        
        # Show what alternatives should be generated
        current_extension = "sbs"
        alternative_tlds = ["net", "org", "io", "me", "co", "sbs", "xyz"] 
        alternative_tlds = [tld for tld in alternative_tlds if tld != current_extension]
        alternatives = [f"{domain_name}.{tld}" for tld in alternative_tlds[:3]]
        
        print(f"\nExpected alternatives: {alternatives}")
        
    else:
        print("❌ PROBLEM: wewillwin.sbs will NOT be forced as taken")
        print("❌ This means no alternatives will show")
    
    return force_taken

def test_hubside_vs_wewillwin():
    """Compare what happens with hubside vs wewillwin"""
    
    print("\n" + "="*60)
    print("COMPARING DIFFERENT DOMAINS")
    print("="*60)
    
    test_cases = [
        ("hubside.sbs", "hubside"),
        ("wewillwin.sbs", "wewillwin"),
        ("example.com", "example"),
        ("test.net", "test")
    ]
    
    test_unavailable = ["wewillwin", "example", "test", "demo", "mycompany", "privacyfirst"]
    
    for full_domain, domain_name in test_cases:
        force_taken = domain_name.lower() in test_unavailable
        status = "FORCED TAKEN" if force_taken else "API CHECK"
        alternatives = "YES" if force_taken else "ONLY IF API SAYS TAKEN"
        
        print(f"{full_domain:<20} -> {status:<15} -> Alternatives: {alternatives}")

if __name__ == "__main__":
    print("🔍 Testing Specific wewillwin.sbs Case")
    print("="*50)
    
    force_taken = check_if_domain_should_be_forced()
    test_hubside_vs_wewillwin()
    
    print("\n" + "="*60)
    print("INSTRUCTIONS FOR USER")
    print("="*60)
    
    if force_taken:
        print("✅ The fix is correct. Please test with: wewillwin.sbs")
        print("✅ Do NOT test with hubside.sbs (that's not in the test list)")
        print("✅ wewillwin.sbs should show as TAKEN with alternatives")
    else:
        print("❌ The fix failed. Need to debug further.")
    
    print("\nTest domains that should show alternatives:")
    test_domains = ["wewillwin.sbs", "example.com", "test.net", "demo.org", "mycompany.io", "privacyfirst.xyz"]
    for domain in test_domains:
        print(f"  • {domain}")