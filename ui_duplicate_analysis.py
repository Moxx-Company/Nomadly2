#!/usr/bin/env python3
"""
UI Duplicate Analysis - Find and categorize UI-affecting duplicates in nomadly2_bot.py
"""

import re
import logging
from collections import defaultdict

def analyze_ui_duplicates():
    """Analyze nomadly2_bot.py for UI-affecting duplicates"""
    
    try:
        with open('nomadly2_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Track different types of duplicates
    duplicates = {
        'main_menu_functions': [],
        'duplicate_buttons': defaultdict(list),
        'callback_conflicts': defaultdict(list),
        'repeated_keyboards': [],
    }
    
    # Find main menu functions
    main_menu_pattern = r'async def.*main_menu.*\(.*\):'
    for i, line in enumerate(lines, 1):
        if re.search(main_menu_pattern, line):
            duplicates['main_menu_functions'].append((i, line.strip()))
    
    # Find button duplicates
    button_pattern = r'InlineKeyboardButton\("([^"]+)",\s*callback_data="([^"]+)"\)'
    for i, line in enumerate(lines, 1):
        matches = re.findall(button_pattern, line)
        for text, callback in matches:
            duplicates['duplicate_buttons'][callback].append((i, text, callback))
    
    # Find callback conflicts
    callback_pattern = r'elif.*data.*[=~].*"([^"]+)"'
    for i, line in enumerate(lines, 1):
        matches = re.findall(callback_pattern, line)
        for callback in matches:
            duplicates['callback_conflicts'][callback].append((i, line.strip()))
    
    # Report findings
    print("🔍 UI DUPLICATE ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"\n📱 MAIN MENU FUNCTIONS FOUND: {len(duplicates['main_menu_functions'])}")
    for line_num, func_def in duplicates['main_menu_functions']:
        print(f"  Line {line_num}: {func_def}")
    
    print(f"\n🔘 DUPLICATE BUTTON CALLBACKS (>2 occurrences):")
    critical_duplicates = 0
    for callback, occurrences in duplicates['duplicate_buttons'].items():
        if len(occurrences) > 2:
            critical_duplicates += 1
            print(f"  '{callback}' appears {len(occurrences)} times:")
            for line_num, text, cb in occurrences[:5]:  # Show first 5
                print(f"    Line {line_num}: \"{text}\" -> {cb}")
            if len(occurrences) > 5:
                print(f"    ... and {len(occurrences)-5} more")
    
    print(f"\n⚠️  CRITICAL ISSUES SUMMARY:")
    print(f"  • {len(duplicates['main_menu_functions'])} main menu implementations")
    print(f"  • {critical_duplicates} buttons with excessive duplicates")
    
    # Generate specific recommendations
    recommendations = []
    
    if len(duplicates['main_menu_functions']) > 2:
        recommendations.append("🎯 CONSOLIDATE MAIN MENU: Remove redundant main menu functions")
        
    critical_buttons = ['main_menu', 'my_domains', 'wallet', 'manage_dns']
    for button in critical_buttons:
        count = len(duplicates['duplicate_buttons'].get(button, []))
        if count > 8:  # Too many duplicates
            recommendations.append(f"🔧 STANDARDIZE '{button}' BUTTON: {count} occurrences")
    
    print(f"\n🚀 PRIORITY FIXES NEEDED:")
    for rec in recommendations[:5]:  # Top 5 priorities
        print(f"  {rec}")
    
    return duplicates

if __name__ == "__main__":
    analyze_ui_duplicates()