#!/usr/bin/env python3
"""
Test Nomadly Branding - Verify all UI text uses "Nomadly" instead of "OpenProvider"
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_nomadly_branding():
    """Check that all user-facing text uses Nomadly branding"""
    print("🧪 Testing Nomadly Branding in UI Text")
    print("="*50)
    
    with open('nomadly3_clean_bot.py', 'r') as f:
        content = f.read()
    
    # Find all UI message strings that should now show "Nomadly"
    ui_texts = [
        "Querying Nomadly registry...",
        "Querying Nomadly registry for multiple extensions...",
        "Live pricing from Nomadly registry",
        "checked in real-time via Nomadly"
    ]
    
    print("✅ Checking UI branding changes:")
    all_found = True
    
    for text in ui_texts:
        if text in content:
            print(f"  ✅ Found: '{text}'")
        else:
            print(f"  ❌ Missing: '{text}'")
            all_found = False
    
    # Check that no OpenProvider references remain in UI text
    ui_openprovider_refs = [
        "OpenProvider API...",
        "Live pricing from OpenProvider",
        "via OpenProvider"
    ]
    
    print("\n🔍 Checking for remaining OpenProvider UI references:")
    clean_ui = True
    
    for text in ui_openprovider_refs:
        if text in content:
            print(f"  ❌ Still found: '{text}' (should be changed)")
            clean_ui = False
        else:
            print(f"  ✅ Removed: '{text}'")
    
    print(f"\n📊 Results:")
    print(f"  Nomadly branding added: {'✅ Yes' if all_found else '❌ No'}")
    print(f"  OpenProvider UI references removed: {'✅ Yes' if clean_ui else '❌ No'}")
    
    if all_found and clean_ui:
        print("\n🎉 Perfect! All UI text now uses Nomadly branding while keeping technical API references intact.")
        print("Users will see:")
        print("  • 'Querying Nomadly registry...' during searches")
        print("  • 'Live pricing from Nomadly registry' in results")
        print("  • Consistent offshore domain registration branding")
    else:
        print("\n⚠️ Some branding changes may need additional fixes")
    
    print("\n✅ Nomadly branding test completed!")

if __name__ == "__main__":
    test_nomadly_branding()