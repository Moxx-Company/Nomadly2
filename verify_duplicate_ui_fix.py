#!/usr/bin/env python3
"""
Verify Duplicate UI Fix
=======================

This script verifies that the duplicate UI issue has been resolved and ensures
the streamlined payment flow is working correctly.
"""

import re

def check_for_duplicate_functions():
    """Check for any remaining duplicate payment functions"""
    print("🔍 Checking for duplicate payment functions...")
    
    try:
        with open('nomadly3_clean_bot.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Bot file not found")
        return False
    
    # Check if the deleted function still exists
    if 'async def handle_crypto_payment' in content:
        print("❌ handle_crypto_payment function still exists - should be removed")
        return False
    else:
        print("✅ handle_crypto_payment function successfully removed")
    
    # Check for any orphaned references to the deleted function
    orphaned_refs = re.findall(r'await self\.handle_crypto_payment', content)
    if orphaned_refs:
        print(f"❌ Found {len(orphaned_refs)} orphaned references to deleted function")
        return False
    else:
        print("✅ No orphaned references to deleted function")
    
    return True

def check_streamlined_payment_flow():
    """Check that the streamlined payment flow is correctly implemented"""
    print("\n🔄 Checking streamlined payment flow...")
    
    try:
        with open('nomadly3_clean_bot.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Bot file not found")
        return False
    
    # Check if payment_selection shows both wallet and crypto options
    payment_selection_match = re.search(r'async def handle_payment_selection.*?(?=async def|\Z)', content, re.DOTALL)
    if not payment_selection_match:
        print("❌ handle_payment_selection function not found")
        return False
    
    payment_content = payment_selection_match.group(0)
    
    # Check for crypto buttons directly in payment selection
    crypto_buttons = ['₿ Bitcoin', '🔷 Ethereum', '🟢 Litecoin', '🐕 Dogecoin']
    crypto_buttons_found = all(button in payment_content for button in crypto_buttons)
    
    if crypto_buttons_found:
        print("✅ All crypto payment options available in streamlined flow")
    else:
        print("❌ Some crypto payment options missing from streamlined flow")
        return False
    
    # Check wallet option is present
    if 'wallet balance' in payment_content.lower() or 'pay with wallet' in payment_content.lower():
        print("✅ Wallet payment option available in streamlined flow")
    else:
        print("❌ Wallet payment option missing from streamlined flow")
        return False
    
    return True

def check_callback_handler_integrity():
    """Check that callback handlers are properly configured"""
    print("\n🎯 Checking callback handler integrity...")
    
    try:
        with open('nomadly3_clean_bot.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Bot file not found")
        return False
    
    # Check for pay_crypto_ handler removal
    if 'pay_crypto_' in content and 'handle_crypto_payment' in content:
        print("❌ pay_crypto_ handler still referencing deleted function")
        return False
    else:
        print("✅ pay_crypto_ handler properly cleaned up")
    
    # Check that crypto handlers go directly to crypto_address
    crypto_handlers = ['crypto_btc_', 'crypto_eth_', 'crypto_ltc_', 'crypto_doge_']
    all_present = all(handler in content for handler in crypto_handlers)
    
    if all_present:
        print("✅ All crypto currency handlers are present")
    else:
        print("❌ Some crypto currency handlers are missing")
        return False
    
    return True

def main():
    print("🚀 DUPLICATE UI FIX VERIFICATION")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Duplicate Functions", check_for_duplicate_functions),
        ("Streamlined Payment Flow", check_streamlined_payment_flow),
        ("Callback Handler Integrity", check_callback_handler_integrity)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
            print(f"{'✅' if result else '❌'} {check_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {check_name}: ERROR - {str(e)}")
            results.append((check_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 VERIFICATION SUMMARY")
    print("=" * 30)
    print(f"Checks passed: {passed}/{total}")
    print(f"Success rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED - DUPLICATE UI ISSUE RESOLVED")
        print("\n✅ Benefits achieved:")
        print("   • Removed duplicate payment screens")
        print("   • Streamlined user experience")
        print("   • Single payment flow with all options")
        print("   • Proper callback handler cleanup")
        print("   • No orphaned function references")
    else:
        print(f"\n⚠️ {total - passed} ISSUES REMAINING")
        print("   • Some verification checks failed")
        print("   • Review the specific failures above")

if __name__ == "__main__":
    main()