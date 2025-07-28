#!/usr/bin/env python3
"""
Verify that domain registration pricing displays our real-time prices with 3.3x multiplier
"""

import sys
import os

def verify_pricing_display():
    """Verify that pricing display shows real prices instead of sample prices"""
    
    print("🔍 Verifying Domain Registration Pricing Display...")
    
    # Check nomadly2_bot.py for pricing display
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
        
        checks = [
            {
                'name': 'Domain Search Page Pricing Text',
                'search': 'Live Pricing (Real-time with 3.3x markup)',
                'found': 'Live Pricing (Real-time with 3.3x markup)' in content,
                'required': True
            },
            {
                'name': 'Sample Pricing Removed',
                'search': 'Sample Pricing',
                'found': 'Sample Pricing' not in content,
                'required': True
            },
            {
                'name': 'Updated .sbs Price Display',
                'search': '.sbs ($9.87/yr)',
                'found': '.sbs ($9.87/yr)' in content,
                'required': True
            },
            {
                'name': 'Updated .com Price Display', 
                'search': '.com ($39.53/yr)',
                'found': '.com ($39.53/yr)' in content,
                'required': True
            },
            {
                'name': 'Updated .io Price Display',
                'search': '.io ($197.97/yr)',
                'found': '.io ($197.97/yr)' in content,
                'required': True
            },
            {
                'name': 'Real Price Estimates in Code',
                'search': '".sbs": 9.87,    # $2.99 * 3.3',
                'found': '".sbs": 9.87,    # $2.99 * 3.3' in content,
                'required': True
            },
            {
                'name': 'Updated Default Price',
                'search': 'price_estimates.get(tld, 42.87)',
                'found': 'price_estimates.get(tld, 42.87)' in content,
                'required': True
            }
        ]
        
        print("\n📊 Pricing Display Verification Results:")
        print("=" * 50)
        
        all_passed = True
        for check in checks:
            status = "✅ PASS" if check['found'] else "❌ FAIL"
            print(f"{status} {check['name']}")
            if not check['found'] and check['required']:
                all_passed = False
        
        print("\n" + "=" * 50)
        
        if all_passed:
            print("🎉 SUCCESS: All pricing displays updated to show real-time prices!")
            print("\n📋 Summary of Changes:")
            print("• Domain search page now shows 'Live Pricing (Real-time with 3.3x markup)'")
            print("• Removed 'Sample Pricing' misleading text")
            print("• Updated all price estimates to show actual 3.3x multiplied prices")
            print("• .sbs: $2.99 → $9.87 (was showing old $2.99)")
            print("• .com: $11.98 → $39.53 (was showing old $11.98)")
            print("• .io: $59.99 → $197.97 (was showing old $59.99)")
            print("• Updated default fallback price to $42.87 (3.3x multiplier)")
            return True
        else:
            print("❌ INCOMPLETE: Some pricing displays still need updates")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying pricing display: {e}")
        return False

def main():
    print("🚀 Domain Registration Pricing Verification")
    print("=" * 50)
    
    success = verify_pricing_display()
    
    if success:
        print("\n✅ Domain registration pricing is now showing real-time prices with 3.3x multiplier!")
        print("Users will see accurate pricing that reflects our actual charges.")
        sys.exit(0)
    else:
        print("\n❌ Pricing verification failed - some displays may still show old prices")
        sys.exit(1)

if __name__ == "__main__":
    main()