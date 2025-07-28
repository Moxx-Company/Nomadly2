#!/usr/bin/env python3
"""
Test the domain availability simulation logic
"""

def simulate_domain_availability(domain_name, extension):
    """Simulate domain availability check"""
    # Force specific domains to be unavailable to test alternatives (HIGHEST PRIORITY)
    test_unavailable = ["wewillwin", "example", "test", "demo", "mycompany", "privacyfirst"]
    
    if domain_name.lower() in test_unavailable:
        return False  # Force these domains to show as taken - NO EXCEPTIONS
    
    # Popular domains are typically taken
    popular_domains = ["google", "facebook", "amazon", "microsoft", "apple", "company", "business", "crypto", "bitcoin", "ethereum"]
    
    if domain_name in popular_domains:
        return False
    
    # Some domains are taken for .com but available for other extensions
    taken_com_domains = ["business", "startup", "company", "crypto", "bitcoin"]
    if domain_name.lower() in taken_com_domains and extension == "com":
        return False
    
    # Simulate some realistic availability patterns
    # .sbs domains are generally more available (but test domains override this above)
    if extension in ["sbs", "xyz", "online", "site"]:
        return True
    
    # Most unique domains are available
    return True

# Test the critical case
print("🔍 Testing wewillwin.sbs availability:")
result = simulate_domain_availability("wewillwin", "sbs")
print(f"wewillwin.sbs available: {result}")
print(f"Expected: False (taken)")
print()

if result == False:
    print("✅ SUCCESS: wewillwin.sbs will show as TAKEN")
    print("✅ This means alternatives will be displayed")
else:
    print("❌ PROBLEM: wewillwin.sbs shows as available")
    print("❌ This means NO alternatives will be shown")

print()
print("Testing other cases:")
test_cases = [
    ("wewillwin", "com"),
    ("example", "net"), 
    ("test", "org"),
    ("mycompany", "io"),
    ("google", "com"),
    ("randomname", "sbs")
]

for domain, ext in test_cases:
    available = simulate_domain_availability(domain, ext)
    print(f"{domain}.{ext}: {'Available' if available else 'Taken'}")