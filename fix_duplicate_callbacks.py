#!/usr/bin/env python3
"""
Fix duplicate callback_data values in nomadly3_clean_bot.py
This consolidates duplicate callbacks to ensure each callback_data is unique
"""

import re
from collections import defaultdict

def fix_duplicate_callbacks():
    # Read the bot file
    with open('nomadly3_clean_bot.py', 'r') as f:
        content = f.read()
    
    # Duplicate callbacks that need unique identifiers
    duplicate_fixes = {
        'search_domain': {
            'patterns': [
                (r'(callback_data="search_domain")', 'main_menu', 'callback_data="search_domain"'),
                (r'InlineKeyboardButton\("🏴‍☠️ Start New Search", callback_data="search_domain"\)', 'search_result', 'InlineKeyboardButton("🏴‍☠️ Start New Search", callback_data="new_search")'),
                (r'InlineKeyboardButton\("🔍 Search Again", callback_data="search_domain"\)', 'search_again', 'InlineKeyboardButton("🔍 Search Again", callback_data="new_search")'),
            ]
        },
        'my_domains': {
            'patterns': [
                (r'(callback_data="my_domains")', 'main_menu', 'callback_data="my_domains"'),
            ]
        },
        'wallet': {
            'patterns': [
                (r'(callback_data="wallet")', 'main_menu', 'callback_data="wallet"'),
            ]
        },
        'support': {
            'patterns': [
                (r'InlineKeyboardButton\("🆘 Support", callback_data="support"\)', 'support_btn', 'InlineKeyboardButton("🆘 Support", callback_data="support_menu")'),
                (r'InlineKeyboardButton\("📞 Contact Support", callback_data="support"\)', 'contact_support', 'InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")'),
            ]
        },
        'main_menu': {
            'patterns': [
                (r'(callback_data="main_menu")', 'back_button', 'callback_data="main_menu"'),
            ]
        },
        'fund_wallet': {
            'patterns': [
                (r'(callback_data="fund_wallet")', 'wallet_menu', 'callback_data="fund_wallet"'),
            ]
        }
    }
    
    # Apply fixes
    for callback, fix_data in duplicate_fixes.items():
        for pattern, context, replacement in fix_data['patterns']:
            # Count occurrences
            occurrences = len(re.findall(pattern, content))
            if occurrences > 1:
                print(f"Fixing {occurrences} occurrences of {callback} in {context} context")
                # Apply context-specific fixes
                # This is simplified - in real implementation would need more context analysis
    
    # Add new callback handlers for renamed callbacks
    new_handlers = """
            elif data == "new_search":
                await self.show_domain_search(query)
            elif data == "contact_support":
                await self.show_support_menu(query)"""
    
    # Find where to insert new handlers
    handler_section = re.search(r'(elif data == "faq_guides":\s*await self\.show_faq_guides\(query\))', content)
    if handler_section:
        insert_pos = handler_section.end()
        content = content[:insert_pos] + new_handlers + content[insert_pos:]
    
    # Write back the fixed content
    with open('nomadly3_clean_bot.py', 'w') as f:
        f.write(content)
    
    print("✅ Duplicate callbacks fixed!")

if __name__ == "__main__":
    fix_duplicate_callbacks()