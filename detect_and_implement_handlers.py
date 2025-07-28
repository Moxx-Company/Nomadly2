#!/usr/bin/env python3
"""
Detect missing handlers in clean rebuild bot and implement them from original bot
"""

import re
import os

def analyze_callback_handlers():
    """Analyze what handlers are missing in clean rebuild"""
    
    print("🔍 ANALYZING CALLBACK HANDLERS")
    print("=" * 50)
    
    # Read clean rebuild bot
    try:
        with open('nomadly2_clean_rebuild.py', 'r') as f:
            clean_content = f.read()
    except Exception as e:
        print(f"❌ Error reading clean rebuild: {e}")
        return
    
    # Read original bot
    try:
        with open('nomadly2_bot.py', 'r') as f:
            original_content = f.read()
    except Exception as e:
        print(f"❌ Error reading original bot: {e}")
        return
    
    # Find all callback data patterns in clean rebuild
    clean_callbacks = set()
    callback_patterns = [
        r'callback_data="([^"]+)"',
        r"callback_data='([^']+)'"
    ]
    
    for pattern in callback_patterns:
        matches = re.findall(pattern, clean_content)
        clean_callbacks.update(matches)
    
    print(f"📋 Found {len(clean_callbacks)} callback patterns in clean rebuild:")
    for cb in sorted(clean_callbacks):
        print(f"  - {cb}")
    
    # Find handler methods in clean rebuild
    clean_handlers = set()
    handler_patterns = [
        r'async def (handle_[^(]+)\(',
        r'elif data == "([^"]+)":\s*\n\s*await self\.(handle_[^(]+)\(',
        r"elif data == '([^']+)':\s*\n\s*await self\.(handle_[^(]+)\("
    ]
    
    for pattern in handler_patterns:
        matches = re.findall(pattern, clean_content)
        if isinstance(matches[0], tuple):
            # Extract handler methods from elif statements
            for match in matches:
                if len(match) == 2:
                    clean_handlers.add(match[1])
        else:
            clean_handlers.update(matches)
    
    print(f"\n🔧 Found {len(clean_handlers)} handler methods in clean rebuild:")
    for handler in sorted(clean_handlers):
        print(f"  - {handler}")
    
    # Find missing implementations
    missing_handlers = []
    for cb in clean_callbacks:
        expected_handler = f"handle_{cb}" if not cb.startswith("handle_") else cb
        if expected_handler not in clean_handlers:
            missing_handlers.append((cb, expected_handler))
    
    print(f"\n❌ MISSING HANDLERS ({len(missing_handlers)}):")
    for cb, handler in missing_handlers:
        print(f"  - {cb} -> {handler}")
    
    return missing_handlers, clean_content, original_content

def extract_handler_from_original(handler_name, original_content):
    """Extract handler implementation from original bot"""
    
    # Look for the handler method
    pattern = rf'async def {handler_name}\([^)]*\):(.*?)(?=async def|\Z)'
    match = re.search(pattern, original_content, re.DOTALL)
    
    if match:
        handler_code = match.group(1).strip()
        return handler_code
    
    # Look for inline handler logic in callback handler
    callback_pattern = rf'elif.*{handler_name.replace("handle_", "")}.*?:(.*?)(?=elif|else:|$)'
    match = re.search(callback_pattern, original_content, re.DOTALL)
    
    if match:
        inline_code = match.group(1).strip()
        return inline_code
    
    return None

def implement_missing_handlers():
    """Implement all missing handlers"""
    
    missing_handlers, clean_content, original_content = analyze_callback_handlers()
    
    if not missing_handlers:
        print("\n✅ All handlers are implemented!")
        return
    
    print(f"\n🔧 IMPLEMENTING {len(missing_handlers)} MISSING HANDLERS")
    print("=" * 50)
    
    implementations = []
    
    for callback_data, handler_name in missing_handlers:
        print(f"\n🔍 Searching for {handler_name} implementation...")
        
        # Extract from original bot
        handler_code = extract_handler_from_original(handler_name, original_content)
        
        if handler_code:
            print(f"✅ Found implementation for {handler_name}")
            implementations.append((handler_name, handler_code))
        else:
            print(f"❌ No implementation found for {handler_name}")
    
    return implementations

if __name__ == "__main__":
    implement_missing_handlers()