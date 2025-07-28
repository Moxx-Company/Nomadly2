#!/usr/bin/env python3
"""
Scan nomadly2_bot.py for missing callback handlers
Check for buttons that create callbacks but don't have corresponding handlers
"""

import re
import os

def find_callback_definitions():
    """Find all callback_data definitions in the bot code"""
    callbacks_defined = set()
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
            
        # Find callback_data patterns
        patterns = [
            r'callback_data=["\']([^"\']+)["\']',
            r"callback_data=f['\"]([^'\"]+)['\"]",
            r'callback_data=f"([^"]+)"',
            r"callback_data=f'([^']+)'"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Clean up f-string patterns
                clean_match = re.sub(r'\{[^}]+\}', '*', match)
                if clean_match and not clean_match.startswith('{'):
                    callbacks_defined.add(clean_match)
                    
    except FileNotFoundError:
        print("❌ nomadly2_bot.py not found")
        return set()
        
    return callbacks_defined

def find_callback_handlers():
    """Find all callback handlers in the handle_callback method"""
    handlers_found = set()
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
            
        # Find the handle_callback method
        handler_match = re.search(r'async def handle_callback.*?(?=async def|\Z)', content, re.DOTALL)
        if not handler_match:
            print("❌ handle_callback method not found")
            return set()
            
        handler_content = handler_match.group(0)
        
        # Find exact match patterns
        exact_patterns = re.findall(r'data == ["\']([^"\']+)["\']', handler_content)
        for pattern in exact_patterns:
            handlers_found.add(pattern)
            
        # Find startswith patterns  
        startswith_patterns = re.findall(r'data\.startswith\(["\']([^"\']+)["\']', handler_content)
        for pattern in startswith_patterns:
            handlers_found.add(pattern + '*')  # Mark as prefix
            
    except FileNotFoundError:
        print("❌ nomadly2_bot.py not found")
        return set()
        
    return handlers_found

def check_handler_coverage(callbacks_defined, handlers_found):
    """Check which callbacks are covered by handlers"""
    covered_callbacks = set()
    missing_callbacks = set()
    
    for callback in callbacks_defined:
        is_covered = False
        
        # Check exact matches
        if callback in handlers_found:
            is_covered = True
            covered_callbacks.add(callback)
        else:
            # Check prefix matches
            for handler in handlers_found:
                if handler.endswith('*'):  # Prefix handler
                    prefix = handler[:-1]
                    if callback.startswith(prefix):
                        is_covered = True
                        covered_callbacks.add(callback)
                        break
        
        if not is_covered:
            missing_callbacks.add(callback)
            
    return covered_callbacks, missing_callbacks

def main():
    print("🔍 SCANNING FOR MISSING CALLBACK HANDLERS")
    print("=" * 60)
    
    # Find all callback definitions
    print("📋 Finding callback definitions...")
    callbacks_defined = find_callback_definitions()
    print(f"   Found {len(callbacks_defined)} callback definitions")
    
    # Find all callback handlers
    print("🔧 Finding callback handlers...")
    handlers_found = find_callback_handlers()  
    print(f"   Found {len(handlers_found)} callback handlers")
    
    # Check coverage
    print("📊 Checking handler coverage...")
    covered, missing = check_handler_coverage(callbacks_defined, handlers_found)
    
    print(f"\n📈 COVERAGE ANALYSIS")
    print("-" * 30)
    print(f"Total callbacks defined: {len(callbacks_defined)}")
    print(f"Callbacks covered: {len(covered)}")
    print(f"Callbacks missing: {len(missing)}")
    print(f"Coverage rate: {(len(covered)/len(callbacks_defined)*100):.1f}%" if callbacks_defined else "N/A")
    
    if missing:
        print(f"\n❌ MISSING HANDLERS:")
        print("-" * 20)
        for callback in sorted(missing):
            print(f"  • {callback}")
            
        print(f"\n🔧 SUGGESTED HANDLER CODE:")
        print("-" * 25)
        for callback in sorted(missing):
            if '*' not in callback:  # Only exact matches
                print(f'elif data == "{callback}":')
                print(f'    await query.answer("⚡ Loading...")')
                print(f'    await self.handle_{callback.replace("-", "_")}(query)')
                print()
    else:
        print(f"\n✅ ALL CALLBACKS HAVE HANDLERS!")
        
    print(f"\n📋 ALL DEFINED CALLBACKS:")
    print("-" * 25)
    for callback in sorted(callbacks_defined):
        status = "✅" if callback in covered else "❌"
        print(f"{status} {callback}")
        
    print(f"\n🔧 ALL REGISTERED HANDLERS:")
    print("-" * 28)
    for handler in sorted(handlers_found):
        print(f"✅ {handler}")

if __name__ == "__main__":
    main()