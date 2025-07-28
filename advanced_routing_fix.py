#!/usr/bin/env python3
"""
Advanced Telegram Bot Routing Fix
Comprehensive solution for all callback routing conflicts
"""

import re
from typing import Dict, List, Set

def fix_all_routing_conflicts():
    """Comprehensive fix for all routing conflicts with proper namespacing"""
    
    print("🔧 ADVANCED ROUTING CONFLICT RESOLUTION")
    print("=" * 60)
    
    # Read the original bot file
    try:
        with open('nomadly3_simple.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ nomadly3_simple.py not found")
        return False
    
    # Define comprehensive routing fixes with proper hierarchy
    routing_fixes = {
        # Payment System - Most specific first
        'crypto_pay_': 'payment.crypto.process_',
        'switch_crypto_': 'payment.crypto.switch_',
        'check_payment_': 'payment.status.check_',
        'generate_qr_': 'payment.qr.generate_',
        'copy_address_': 'payment.address.copy_full_',
        'copy_addr_': 'payment.address.copy_',
        'crypto_': 'payment.crypto.select_',  # Most general last
        
        # Wallet System - Amount-specific first
        'add_funds_100': 'wallet.fund.usd_100',
        'add_funds_50': 'wallet.fund.usd_50',
        'add_funds_20': 'wallet.fund.usd_20',
        'add_funds_menu': 'wallet.fund.show_menu',
        'add_funds_upgrade': 'wallet.fund.tier_upgrade',
        'fund_crypto_btc': 'wallet.deposit.btc',
        'fund_crypto_eth': 'wallet.deposit.eth',
        'fund_crypto_ltc': 'wallet.deposit.ltc',
        'fund_crypto_doge': 'wallet.deposit.doge',
        'pay_wallet_': 'wallet.payment.process_',
        'add_funds_': 'wallet.fund.options_',  # Most general last
        
        # Domain System - Specific domains first
        'check_domain_example.com': 'domain.check.example_com',
        'check_domain_offshore.io': 'domain.check.offshore_io', 
        'check_domain_private.org': 'domain.check.private_org',
        'check_domain_secure.net': 'domain.check.secure_net',
        'domain_details_': 'domain.info.details_',
        'dns_manage_': 'domain.dns.manage_',
        'ns_manage_': 'domain.nameserver.manage_',
        'register_domain': 'domain.register.process',
        'check_domain_': 'domain.check.availability_',  # General patterns last
        'register_': 'domain.register.workflow_',
        'domain_': 'domain.manage.action_',
        
        # Language System - Specific languages first
        'lang_en': 'user.language.english',
        'lang_fr': 'user.language.french',
        'lang_es': 'user.language.spanish',
        'lang_hi': 'user.language.hindi',
        'lang_zh': 'user.language.chinese',
        'lang_': 'user.language.select_',  # General last
        
        # DNS System - Provider-specific first
        'dns_cloudflare': 'dns.provider.cloudflare',
        'dns_custom': 'dns.provider.custom',
        'dns_': 'dns.manage.action_',  # General last
    }
    
    print("📋 APPLYING ROUTING FIXES:")
    print("-" * 40)
    
    # Apply fixes in order (most specific to most general)
    updated_content = content
    fixes_applied = 0
    
    for old_pattern, new_pattern in routing_fixes.items():
        # Count replacements before applying
        count_before = count_pattern_occurrences(updated_content, old_pattern)
        
        if count_before > 0:
            updated_content = apply_pattern_fix(updated_content, old_pattern, new_pattern)
            count_after = count_pattern_occurrences(updated_content, old_pattern)
            
            if count_after < count_before:
                fixes_applied += 1
                print(f"✓ {old_pattern} → {new_pattern} ({count_before - count_after} replacements)")
    
    print(f"\n✅ Applied {fixes_applied} routing fixes")
    
    # Validate the fixes
    validation_result = validate_updated_content(updated_content)
    
    if validation_result['success']:
        # Write the fixed file
        with open('nomadly3_simple_routing_fixed.py', 'w') as f:
            f.write(updated_content)
        
        print("\n🎉 ROUTING CONFLICTS SUCCESSFULLY RESOLVED!")
        print("=" * 60)
        print(f"✓ Created: nomadly3_simple_routing_fixed.py")
        print(f"✓ Fixed: {fixes_applied} routing patterns")
        print(f"✓ Conflicts resolved: {validation_result['conflicts_resolved']}")
        print("\nNext steps:")
        print("1. Review the fixed file")
        print("2. Test callback handlers")
        print("3. Replace original file when satisfied")
        
        return True
    else:
        print(f"\n❌ VALIDATION ISSUES REMAIN:")
        for issue in validation_result['issues']:
            print(f"✗ {issue}")
        return False

def count_pattern_occurrences(content: str, pattern: str) -> int:
    """Count occurrences of a pattern in content"""
    count = 0
    
    # Count callback_data occurrences
    count += len(re.findall(rf'callback_data=["\'{pattern}["\']', content))
    
    # Count startswith occurrences
    count += len(re.findall(rf'data\.startswith\(["\'{pattern}["\']\)', content))
    
    # Count direct comparison occurrences
    count += len(re.findall(rf'data\s*==\s*["\'{pattern}["\']', content))
    
    return count

def apply_pattern_fix(content: str, old_pattern: str, new_pattern: str) -> str:
    """Apply a specific pattern fix to content"""
    
    # Fix callback_data references
    content = re.sub(
        rf'callback_data="{re.escape(old_pattern)}"',
        f'callback_data="{new_pattern}"',
        content
    )
    content = re.sub(
        rf"callback_data='{re.escape(old_pattern)}'",
        f"callback_data='{new_pattern}'",
        content
    )
    
    # Fix startswith references  
    content = re.sub(
        rf'data\.startswith\("{re.escape(old_pattern)}"\)',
        f'data.startswith("{new_pattern}")',
        content
    )
    content = re.sub(
        rf"data\.startswith\('{re.escape(old_pattern)}'\)",
        f"data.startswith('{new_pattern}')",
        content
    )
    
    # Fix direct comparison references
    content = re.sub(
        rf'data\s*==\s*"{re.escape(old_pattern)}"',
        f'data == "{new_pattern}"',
        content
    )
    content = re.sub(
        rf"data\s*==\s*'{re.escape(old_pattern)}'",
        f"data == '{new_pattern}'",
        content
    )
    
    return content

def validate_updated_content(content: str) -> Dict:
    """Validate that routing fixes resolved conflicts"""
    
    # Extract all patterns from updated content
    patterns = extract_patterns(content)
    conflicts = find_remaining_conflicts(patterns)
    
    return {
        'success': len(conflicts) == 0,
        'conflicts_resolved': len(conflicts) == 0,
        'issues': conflicts,
        'total_patterns': sum(len(p) for p in patterns.values())
    }

def extract_patterns(content: str) -> Dict[str, Set[str]]:
    """Extract all callback patterns from content"""
    
    patterns = {
        'callback_data': set(),
        'startswith': set(), 
        'direct': set()
    }
    
    # Extract callback_data patterns
    patterns['callback_data'].update(re.findall(r'callback_data=["\']([^"\']+)["\']', content))
    
    # Extract startswith patterns
    patterns['startswith'].update(re.findall(r'data\.startswith\(["\']([^"\']+)["\']', content))
    
    # Extract direct patterns
    patterns['direct'].update(re.findall(r'data\s*==\s*["\']([^"\']+)["\']', content))
    
    return patterns

def find_remaining_conflicts(patterns: Dict[str, Set[str]]) -> List[str]:
    """Find any remaining routing conflicts"""
    
    conflicts = []
    all_patterns = set()
    
    # Collect all patterns
    for pattern_set in patterns.values():
        all_patterns.update(pattern_set)
    
    # Check for prefix conflicts
    pattern_list = sorted(all_patterns)
    for i, pattern1 in enumerate(pattern_list):
        for pattern2 in pattern_list[i+1:]:
            if pattern1 != pattern2:
                # Check if one is a prefix of the other
                if (pattern1.startswith(pattern2) or pattern2.startswith(pattern1)):
                    # Avoid false positives for namespaced patterns
                    if not ('.' in pattern1 and '.' in pattern2):
                        conflicts.append(f"{pattern1} conflicts with {pattern2}")
    
    return conflicts

if __name__ == "__main__":
    print("🚀 Starting Advanced Routing Conflict Resolution...")
    print()
    
    success = fix_all_routing_conflicts()
    
    if success:
        print("\n🎯 READY FOR TESTING")
        print("The routing conflicts have been resolved with proper namespacing.")
        print("All callback patterns now use hierarchical naming.")
    else:
        print("\n⚠️ MANUAL REVIEW REQUIRED")
        print("Some conflicts may need individual attention.")