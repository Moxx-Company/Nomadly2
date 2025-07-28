#!/usr/bin/env python3
"""
Telegram Bot Callback Routing Conflict Resolution
Fixes all identified routing conflicts and implements proper namespacing
"""

import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class CallbackRouter:
    """Central callback routing system with conflict detection and resolution"""
    
    def __init__(self):
        self.routes = {}
        self.patterns = {}
        self.conflicts = []
        
    def register_route(self, pattern: str, handler: str, description: str = ""):
        """Register a callback route with conflict detection"""
        if pattern in self.routes:
            self.conflicts.append(f"Duplicate route: {pattern}")
            return False
            
        # Check for prefix conflicts
        for existing_pattern in self.routes:
            if pattern.startswith(existing_pattern) or existing_pattern.startswith(pattern):
                if pattern != existing_pattern:
                    self.conflicts.append(f"Prefix conflict: {pattern} vs {existing_pattern}")
        
        self.routes[pattern] = {
            'handler': handler,
            'description': description
        }
        return True
    
    def get_route_suggestions(self) -> Dict[str, str]:
        """Generate suggestions to fix routing conflicts"""
        suggestions = {}
        
        # Analyze current conflicts and suggest fixes
        conflict_fixes = {
            'crypto_pay_': 'payment.crypto.process_',
            'crypto_': 'payment.crypto.select_',
            'add_funds_20': 'wallet.fund.amount_20',
            'add_funds_': 'wallet.fund.select_',
            'check_domain_example.com': 'domain.check.example_com',
            'check_domain_': 'domain.check.availability_',
            'domain_details_': 'domain.info.details_',
            'domain_': 'domain.manage.action_',
            'lang_en': 'user.language.set_en',
            'lang_': 'user.language.select_',
            'register_domain': 'domain.register.process',
            'register_': 'domain.register.workflow_'
        }
        
        return conflict_fixes

def analyze_and_fix_routing_conflicts():
    """Main function to analyze and fix all routing conflicts"""
    
    print("🔧 TELEGRAM BOT ROUTING CONFLICT RESOLUTION")
    print("=" * 60)
    print()
    
    # Step 1: Read current bot file
    try:
        with open('nomadly3_simple.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ nomadly3_simple.py not found")
        return False
    
    # Step 2: Extract all callback patterns
    callback_patterns = extract_all_patterns(content)
    conflicts = identify_conflicts(callback_patterns)
    
    print("📋 IDENTIFIED CONFLICTS:")
    print("-" * 40)
    for i, conflict in enumerate(conflicts, 1):
        print(f"{i}. {conflict}")
    print()
    
    # Step 3: Generate fixes
    fixes = generate_routing_fixes(conflicts)
    
    print("🔧 PROPOSED FIXES:")
    print("-" * 40)
    for old_pattern, new_pattern in fixes.items():
        print(f"'{old_pattern}' → '{new_pattern}'")
    print()
    
    # Step 4: Apply fixes to the bot file
    updated_content = apply_routing_fixes(content, fixes)
    
    # Step 5: Validate no new conflicts introduced
    validation_result = validate_fixes(updated_content)
    
    if validation_result['success']:
        # Step 6: Write the updated file
        with open('nomadly3_simple_fixed_routing.py', 'w') as f:
            f.write(updated_content)
        
        print("✅ ROUTING FIXES APPLIED SUCCESSFULLY")
        print("-" * 40)
        print(f"✓ Fixed {len(fixes)} routing conflicts")
        print(f"✓ Created nomadly3_simple_fixed_routing.py")
        print(f"✓ No new conflicts introduced")
        print()
        
        return True
    else:
        print("❌ VALIDATION FAILED")
        print("-" * 40)
        for error in validation_result['errors']:
            print(f"✗ {error}")
        return False

def extract_all_patterns(content: str) -> Dict[str, Set[str]]:
    """Extract all callback patterns from bot code"""
    
    patterns = {
        'callback_data_patterns': set(),
        'startswith_patterns': set(),
        'direct_patterns': set()
    }
    
    # Extract callback_data patterns
    callback_data_matches = re.findall(r'callback_data=["\']([^"\']+)["\']', content)
    patterns['callback_data_patterns'].update(callback_data_matches)
    
    # Extract startswith patterns
    startswith_matches = re.findall(r'data\.startswith\(["\']([^"\']+)["\']', content)
    patterns['startswith_patterns'].update(startswith_matches)
    
    # Extract direct comparison patterns
    direct_matches = re.findall(r'data\s*==\s*["\']([^"\']+)["\']', content)
    patterns['direct_patterns'].update(direct_matches)
    
    return patterns

def identify_conflicts(patterns: Dict[str, Set[str]]) -> List[str]:
    """Identify routing conflicts between patterns"""
    
    conflicts = []
    all_patterns = set()
    
    # Collect all patterns
    for pattern_set in patterns.values():
        all_patterns.update(pattern_set)
    
    # Find conflicts
    pattern_list = list(all_patterns)
    for i, pattern1 in enumerate(pattern_list):
        for j, pattern2 in enumerate(pattern_list[i+1:], i+1):
            if pattern1 != pattern2:
                # Check for prefix conflicts
                if pattern1.startswith(pattern2) or pattern2.startswith(pattern1):
                    # Avoid false positives for completely different patterns
                    if not (pattern1.endswith('_') and pattern2.endswith('_')):
                        conflicts.append(f"{pattern1} conflicts with {pattern2}")
    
    return conflicts

def generate_routing_fixes(conflicts: List[str]) -> Dict[str, str]:
    """Generate routing fixes using namespaced patterns"""
    
    fixes = {}
    
    # Define routing namespace mapping
    namespace_mapping = {
        # Payment system
        'crypto_pay_': 'payment.crypto.process_',
        'crypto_': 'payment.crypto.select_',
        'switch_crypto_': 'payment.crypto.switch_',
        'check_payment_': 'payment.status.check_',
        'copy_addr_': 'payment.address.copy_',
        'copy_address_': 'payment.address.copy_full_',
        'generate_qr_': 'payment.qr.generate_',
        
        # Wallet system
        'add_funds_20': 'wallet.fund.amount_20',
        'add_funds_50': 'wallet.fund.amount_50', 
        'add_funds_100': 'wallet.fund.amount_100',
        'add_funds_': 'wallet.fund.select_',
        'fund_crypto_': 'wallet.deposit.crypto_',
        'pay_wallet_': 'wallet.payment.process_',
        
        # Domain system
        'check_domain_example.com': 'domain.check.example_com',
        'check_domain_offshore.io': 'domain.check.offshore_io',
        'check_domain_private.org': 'domain.check.private_org',
        'check_domain_secure.net': 'domain.check.secure_net',
        'check_domain_': 'domain.check.availability_',
        'domain_details_': 'domain.info.details_',
        'domain_': 'domain.manage.action_',
        'register_domain': 'domain.register.process',
        'register_': 'domain.register.workflow_',
        'dns_manage_': 'domain.dns.manage_',
        'ns_manage_': 'domain.nameserver.manage_',
        
        # Language system
        'lang_en': 'user.language.set_en',
        'lang_fr': 'user.language.set_fr',
        'lang_es': 'user.language.set_es',
        'lang_hi': 'user.language.set_hi',
        'lang_zh': 'user.language.set_zh',
        'lang_': 'user.language.select_',
        
        # DNS system
        'dns_': 'dns.manage.action_',
        'dns_cloudflare': 'dns.provider.cloudflare',
        'dns_custom': 'dns.provider.custom',
    }
    
    # Apply namespace mapping to resolve conflicts
    for conflict in conflicts:
        parts = conflict.split(' conflicts with ')
        if len(parts) == 2:
            pattern1, pattern2 = parts
            
            # Map to namespaced versions
            if pattern1 in namespace_mapping:
                fixes[pattern1] = namespace_mapping[pattern1]
            if pattern2 in namespace_mapping:
                fixes[pattern2] = namespace_mapping[pattern2]
    
    return fixes

def apply_routing_fixes(content: str, fixes: Dict[str, str]) -> str:
    """Apply routing fixes to the bot content"""
    
    updated_content = content
    
    for old_pattern, new_pattern in fixes.items():
        # Fix callback_data references
        old_callback = f'callback_data="{old_pattern}"'
        new_callback = f'callback_data="{new_pattern}"'
        updated_content = updated_content.replace(old_callback, new_callback)
        
        old_callback_single = f"callback_data='{old_pattern}'"
        new_callback_single = f"callback_data='{new_pattern}'"
        updated_content = updated_content.replace(old_callback_single, new_callback_single)
        
        # Fix startswith references
        old_startswith = f'data.startswith("{old_pattern}")'
        new_startswith = f'data.startswith("{new_pattern}")'
        updated_content = updated_content.replace(old_startswith, new_startswith)
        
        old_startswith_single = f"data.startswith('{old_pattern}')"
        new_startswith_single = f"data.startswith('{new_pattern}')"
        updated_content = updated_content.replace(old_startswith_single, new_startswith_single)
        
        # Fix direct comparison references
        old_direct = f'data == "{old_pattern}"'
        new_direct = f'data == "{new_pattern}"'
        updated_content = updated_content.replace(old_direct, new_direct)
        
        old_direct_single = f"data == '{old_pattern}'"
        new_direct_single = f"data == '{new_pattern}'"
        updated_content = updated_content.replace(old_direct_single, new_direct_single)
    
    return updated_content

def validate_fixes(content: str) -> Dict[str, any]:
    """Validate that fixes don't introduce new conflicts"""
    
    patterns = extract_all_patterns(content)
    conflicts = identify_conflicts(patterns)
    
    return {
        'success': len(conflicts) == 0,
        'conflicts_remaining': len(conflicts),
        'errors': conflicts
    }

if __name__ == "__main__":
    print("🚀 Starting Telegram Bot Routing Conflict Resolution...")
    print()
    
    success = analyze_and_fix_routing_conflicts()
    
    if success:
        print("🎉 ROUTING CONFLICTS SUCCESSFULLY RESOLVED!")
        print("=" * 60)
        print("Next steps:")
        print("1. Review nomadly3_simple_fixed_routing.py")
        print("2. Test all callback handlers work correctly")
        print("3. Update main bot file when satisfied")
        print("4. Implement callback route registry for future conflicts")
    else:
        print("❌ ROUTING CONFLICT RESOLUTION FAILED")
        print("Manual intervention required")