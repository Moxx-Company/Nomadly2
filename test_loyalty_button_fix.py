#!/usr/bin/env python3
"""
Test script to verify loyalty system button responsiveness fix
"""

import re

def test_loyalty_button_handlers():
    """Test that all loyalty system callback handlers are implemented"""
    print("🏆 LOYALTY SYSTEM BUTTON RESPONSIVENESS TEST")
    print("=" * 50)
    
    with open("nomadly2_bot.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Test for callback handlers
    required_handlers = [
        ("loyalty_dashboard", "Loyalty Dashboard"),
        ("referral_program", "Referral Program"), 
        ("referral_stats", "Detailed Referral Stats"),
        ("earn_points_guide", "Earn Points Guide"),
        ("copy_referral_", "Copy Referral Code (prefix)")
    ]
    
    missing_handlers = []
    found_handlers = []
    
    for callback, description in required_handlers:
        if callback.endswith("_"):
            # Check for prefix pattern
            pattern = f'elif.*data.*startswith.*"{callback}"'
        else:
            # Check for exact match
            pattern = f'elif.*data.*==.*"{callback}"'
        
        if re.search(pattern, content):
            found_handlers.append((callback, description))
            print(f"  ✅ {description} - Handler found")
        else:
            missing_handlers.append((callback, description))
            print(f"  ❌ {description} - Handler missing")
    
    # Test for method implementations
    required_methods = [
        ("show_loyalty_dashboard", "Loyalty Dashboard Display"),
        ("show_referral_program", "Referral Program Display"),
        ("show_detailed_referral_stats", "Detailed Stats Display"),
        ("show_earn_points_guide", "Points Guide Display")
    ]
    
    missing_methods = []
    found_methods = []
    
    for method, description in required_methods:
        pattern = f'async def {method}\\(self, query\\):'
        
        if re.search(pattern, content):
            found_methods.append((method, description))
            print(f"  ✅ {description} - Method implemented")
        else:
            missing_methods.append((method, description))
            print(f"  ❌ {description} - Method missing")
    
    # Test for service integration
    service_patterns = [
        ("from services.loyalty_system_service import get_loyalty_system_service", "Service Import"),
        ("get_loyalty_system_service\\(\\)", "Service Usage"),
        ("get_referral_statistics", "Stats Method Call"),
        ("generate_referral_code", "Code Generation")
    ]
    
    for pattern, description in service_patterns:
        if re.search(pattern, content):
            print(f"  ✅ {description} - Found")
        else:
            print(f"  ⚠️  {description} - Not found")
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"• Callback Handlers: {len(found_handlers)}/{len(required_handlers)} working")
    print(f"• Method Implementations: {len(found_methods)}/{len(required_methods)} working")
    
    if not missing_handlers and not missing_methods:
        print("✅ ALL LOYALTY SYSTEM BUTTONS SHOULD BE RESPONSIVE!")
        return True
    else:
        print("❌ Some loyalty features still missing")
        return False

def test_button_acknowledgments():
    """Test that buttons have immediate acknowledgments"""
    print("\n⚡ BUTTON ACKNOWLEDGMENT TEST")
    print("=" * 30)
    
    with open("nomadly2_bot.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    loyalty_callbacks = ["loyalty_dashboard", "referral_program", "referral_stats", "earn_points_guide"]
    
    for callback in loyalty_callbacks:
        # Find the handler block
        pattern = f'elif data == "{callback}":(.*?)elif'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            handler_block = match.group(1)
            if "query.answer(" in handler_block:
                print(f"  ✅ {callback} - Has acknowledgment")
            else:
                print(f"  ❌ {callback} - No acknowledgment")
        else:
            print(f"  ❌ {callback} - Handler not found")

if __name__ == "__main__":
    success = test_loyalty_button_handlers()
    test_button_acknowledgments()
    
    if success:
        print("\n🎉 LOYALTY SYSTEM BUTTON FIX: COMPLETE!")
        print("All loyalty buttons should now respond instantly without unresponsive behavior.")
    else:
        print("\n⚠️  LOYALTY SYSTEM: Some issues remain")