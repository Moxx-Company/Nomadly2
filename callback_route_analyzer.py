#!/usr/bin/env python3
"""
Telegram Bot Callback Route Analyzer
Detects duplicate callback patterns and routing conflicts
"""

import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict

def analyze_callback_patterns():
    """Analyze callback patterns in nomadly3_simple.py for duplicates and conflicts"""
    
    print("🔍 TELEGRAM BOT CALLBACK ROUTE ANALYSIS")
    print("=" * 60)
    print()
    
    # Read the bot file
    try:
        with open('nomadly3_simple.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ nomadly3_simple.py not found")
        return False
    
    # Extract callback patterns
    callback_patterns = extract_callback_patterns(content)
    
    # Analyze for duplicates and conflicts
    duplicates = find_duplicate_patterns(callback_patterns)
    conflicts = find_pattern_conflicts(callback_patterns)
    coverage = analyze_pattern_coverage(callback_patterns)
    
    # Report findings
    print("📋 CALLBACK PATTERN INVENTORY:")
    print("-" * 40)
    for pattern_type, patterns in callback_patterns.items():
        print(f"**{pattern_type}:** {len(patterns)} patterns")
        for pattern in sorted(patterns):
            print(f"  ✓ {pattern}")
    print()
    
    # Check for duplicates
    if duplicates:
        print("⚠️  DUPLICATE PATTERNS DETECTED:")
        print("-" * 40)
        for pattern, locations in duplicates.items():
            print(f"❌ Pattern: {pattern}")
            print(f"   Found in: {', '.join(locations)}")
        print()
    else:
        print("✅ NO DUPLICATE PATTERNS FOUND")
        print()
    
    # Check for conflicts
    if conflicts:
        print("⚠️  PATTERN CONFLICTS DETECTED:")
        print("-" * 40)
        for conflict in conflicts:
            print(f"❌ Conflict: {conflict}")
        print()
    else:
        print("✅ NO PATTERN CONFLICTS FOUND")
        print()
    
    # Coverage analysis
    print("📊 PATTERN COVERAGE ANALYSIS:")
    print("-" * 40)
    for area, info in coverage.items():
        status = "✅" if info['complete'] else "⚠️"
        print(f"{status} {area}: {info['count']} patterns ({info['status']})")
    print()
    
    return len(duplicates) == 0 and len(conflicts) == 0

def extract_callback_patterns(content: str) -> Dict[str, Set[str]]:
    """Extract all callback patterns from bot code"""
    
    patterns = defaultdict(set)
    
    # Extract callback_data patterns from InlineKeyboardButton calls
    button_patterns = re.findall(r'callback_data=["\']([^"\']+)["\']', content)
    for pattern in button_patterns:
        if '_' in pattern:
            prefix = pattern.split('_')[0]
            patterns['button_callbacks'].add(pattern)
            patterns[f'{prefix}_group'].add(pattern)
    
    # Extract callback handling patterns from if/elif statements
    handler_patterns = re.findall(r'data\.startswith\(["\']([^"\']+)["\']', content)
    for pattern in handler_patterns:
        patterns['handler_patterns'].add(pattern)
    
    # Extract direct callback checks
    direct_patterns = re.findall(r'data\s*==\s*["\']([^"\']+)["\']', content)
    for pattern in direct_patterns:
        patterns['direct_callbacks'].add(pattern)
    
    return dict(patterns)

def find_duplicate_patterns(patterns: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """Find duplicate callback patterns"""
    
    duplicates = {}
    all_patterns = []
    
    # Collect all patterns with their sources
    for source, pattern_set in patterns.items():
        for pattern in pattern_set:
            all_patterns.append((pattern, source))
    
    # Group by pattern
    pattern_groups = defaultdict(list)
    for pattern, source in all_patterns:
        pattern_groups[pattern].append(source)
    
    # Find duplicates
    for pattern, sources in pattern_groups.items():
        if len(set(sources)) > 1:  # Pattern appears in multiple contexts
            duplicates[pattern] = list(set(sources))
    
    return duplicates

def find_pattern_conflicts(patterns: Dict[str, Set[str]]) -> List[str]:
    """Find conflicting callback patterns"""
    
    conflicts = []
    
    # Check for prefix conflicts (e.g., "crypto_" vs "crypto_btc")
    all_patterns = set()
    for pattern_set in patterns.values():
        all_patterns.update(pattern_set)
    
    for pattern1 in all_patterns:
        for pattern2 in all_patterns:
            if pattern1 != pattern2:
                if pattern1.startswith(pattern2) or pattern2.startswith(pattern1):
                    conflict = f"{pattern1} conflicts with {pattern2}"
                    if conflict not in conflicts:
                        conflicts.append(conflict)
    
    return conflicts

def analyze_pattern_coverage(patterns: Dict[str, Set[str]]) -> Dict[str, Dict]:
    """Analyze pattern coverage by functional area"""
    
    coverage = {
        'Domain Management': {
            'patterns': ['domain_', 'dns_', 'ns_'],
            'count': 0,
            'complete': False,
            'status': 'checking...'
        },
        'Payment Processing': {
            'patterns': ['crypto_', 'pay_', 'switch_', 'check_payment'],
            'count': 0,
            'complete': False,
            'status': 'checking...'
        },
        'User Interface': {
            'patterns': ['back_', 'menu', 'language', 'search'],
            'count': 0,
            'complete': False,
            'status': 'checking...'
        },
        'Wallet Management': {
            'patterns': ['wallet', 'fund_', 'add_funds'],
            'count': 0,
            'complete': False,
            'status': 'checking...'
        }
    }
    
    # Count patterns in each area
    all_patterns = set()
    for pattern_set in patterns.values():
        all_patterns.update(pattern_set)
    
    for area, info in coverage.items():
        count = 0
        for pattern in all_patterns:
            if any(prefix in pattern for prefix in info['patterns']):
                count += 1
        
        info['count'] = count
        info['complete'] = count >= 5  # Arbitrary threshold
        info['status'] = 'Complete' if info['complete'] else 'Needs attention'
    
    return coverage

def suggest_routing_improvements():
    """Suggest improvements to callback routing structure"""
    
    print("💡 ROUTING IMPROVEMENT SUGGESTIONS:")
    print("=" * 60)
    print()
    
    suggestions = [
        "1. **Create Callback Route Registry**",
        "   - Central registry of all callback patterns",
        "   - Validation before registration",
        "   - Conflict detection system",
        "",
        "2. **Implement Route Namespacing**", 
        "   - domain.manage.dns.add",
        "   - payment.crypto.switch.btc",
        "   - user.wallet.fund.eth",
        "",
        "3. **Add Route Parameter Parsing**",
        "   - crypto_{type}_{domain} → params: {type: 'btc', domain: 'example.com'}",
        "   - Structured parameter extraction",
        "",
        "4. **Create Route Middleware System**",
        "   - Authentication checks",
        "   - User state validation", 
        "   - Rate limiting",
        "",
        "5. **Implement Route Testing Framework**",
        "   - Unit tests for each callback route",
        "   - Integration tests for user flows",
        "   - Mock callback data generation"
    ]
    
    for suggestion in suggestions:
        print(suggestion)
    print()

if __name__ == "__main__":
    print("🚀 Starting Telegram Bot Callback Route Analysis...")
    print()
    
    # Run analysis
    analysis_passed = analyze_callback_patterns()
    
    # Provide suggestions
    suggest_routing_improvements()
    
    # Summary
    print("📋 ANALYSIS SUMMARY:")
    print("=" * 60)
    if analysis_passed:
        print("✅ Callback routing structure is clean")
        print("✅ Ready to continue with mock UI completion")
        print("💡 Consider implementing suggestions for production")
    else:
        print("⚠️  Issues found in callback routing")
        print("🔧 Recommend fixing conflicts before proceeding")
        print("📋 Use suggestions above to improve architecture")
    
    print()
    print("🎯 RECOMMENDATION: Complete mock UI first, then refactor routing")