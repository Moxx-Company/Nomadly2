#!/usr/bin/env python3
"""
Test Switch Payment Callback Recognition
"""

import re

# Test callback patterns that might be affecting switch payment
callback_patterns = [
    "switch_crypto_84178e26",
    "switch_crypto_c8d7cca7", 
    "refresh_status_84178e26_1737383000",
    "check_payment_84178e26"
]

print("🔧 TESTING CALLBACK PATTERN MATCHING")
print("=" * 50)

for callback in callback_patterns:
    print(f"\n📋 Testing callback: {callback}")
    
    # Test switch_crypto pattern
    if callback.startswith("switch_crypto_"):
        print("  ✅ Matches switch_crypto_ pattern")
        order_id = callback.replace("switch_crypto_", "")
        print(f"  📋 Extracted order ID: {order_id}")
    else:
        print("  ❌ Does not match switch_crypto_ pattern")
    
    # Test refresh_status pattern  
    if callback.startswith("refresh_status_"):
        print("  ✅ Matches refresh_status_ pattern")
        parts = callback.split("refresh_status_", 1)[1].split("_")
        order_id = parts[0]
        print(f"  📋 Extracted order ID: {order_id}")
    elif callback.startswith("check_payment_"):
        print("  ✅ Matches check_payment_ pattern")
        order_id = callback.split("check_payment_", 1)[1]
        print(f"  📋 Extracted order ID: {order_id}")
    else:
        print("  ❓ No refresh/check pattern match")

print(f"\n🎯 CALLBACK PROCESSING TEST COMPLETE")