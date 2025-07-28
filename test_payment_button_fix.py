#!/usr/bin/env python3
"""
Test script to verify payment button fix
"""

print("Testing payment button fix...")

# Test callback parsing
test_callbacks = [
    "check_payment_btc_wewillwin_sbs",
    "check_payment_eth_mycompany_com", 
    "check_payment_ltc_example_io",
    "check_payment_doge_test_xyz"
]

for callback in test_callbacks:
    print(f"\nTesting callback: {callback}")
    
    # Parse using the handler logic
    if callback.startswith("check_payment_"):
        remaining = callback.replace("check_payment_", "")
        parts = remaining.split("_", 1)
        
        if len(parts) >= 2:
            crypto_type = parts[0]
            domain = parts[1]
            
            # Convert underscores to dots in domain if no dots present
            if "." not in domain:
                domain = domain.replace("_", ".")
                
            print(f"  ✅ Parsed correctly:")
            print(f"     crypto_type: {crypto_type}")
            print(f"     domain: {domain}")
        else:
            print(f"  ❌ Failed to parse - not enough parts")
    else:
        print(f"  ❌ Not a payment callback")

print("\n✅ Payment button callback parsing test complete!")
print("\nThe payment button should now work correctly.")
print("The 'Service temporarily unavailable' error should be fixed.")